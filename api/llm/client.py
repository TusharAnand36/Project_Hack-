"""LLM client: Amazon Bedrock first, optional Groq, deterministic template last (website plan §8.3).

- Credentials only from the environment or a local AWS profile; never in code, prompts or the
  browser. The model id comes from BEDROCK_MODEL_ID (copied from the Bedrock console).
- Token bucket: at most 1 request per second per process; callers queue, they do not fail.
- Timeout 20 s, one retry, then the caller falls back to the template.
- Responses cached by hash(endpoint, input, language, model) in memory and in api/.cache/.
- Logs provider, model id, latency and verifier result; never the user's text.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

log = logging.getLogger("compass.llm")
CACHE_DIR = Path(__file__).resolve().parents[1] / ".cache"
TIMEOUT_S = 20.0


class LLMUnavailable(RuntimeError):
    """No provider configured or the call failed: use the template."""


class TokenBucket:
    """Blocking rate limiter (1 token per `period` seconds). Clock and sleep are injectable for tests."""

    def __init__(
        self,
        period: float = 1.0,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self.period, self.clock, self.sleep = period, clock, sleep
        self._next = 0.0
        self._lock = threading.Lock()

    def acquire(self) -> None:
        with self._lock:
            now = self.clock()
            wait = self._next - now
            self._next = max(now, self._next) + self.period
        if wait > 0:
            self.sleep(wait)


@dataclass
class Completion:
    text: str
    provider: str
    model_id: str | None
    cached: bool = False


class LLMClient:
    def __init__(self, provider: str | None = None, cache_dir: Path | None = CACHE_DIR) -> None:
        self.cache_dir = cache_dir  # None = memory cache only
        self.provider = (provider or os.getenv("LLM_PROVIDER", "template")).lower()
        self.model_id = os.getenv("BEDROCK_MODEL_ID") or None
        self.region = os.getenv("AWS_REGION", "us-east-1")
        self.bucket = TokenBucket(1.0)
        self._mem: dict[str, str] = {}
        self._bedrock = None

    @property
    def enabled(self) -> bool:
        if self.provider == "bedrock":
            return bool(self.model_id)
        if self.provider == "groq":
            return bool(os.getenv("GROQ_API_KEY"))
        return False

    def _key(self, endpoint: str, payload: str, lang: str) -> str:
        return hashlib.sha256(
            f"{endpoint}|{payload}|{lang}|{self.provider}|{self.model_id}".encode()
        ).hexdigest()

    def complete(
        self, endpoint: str, system: str, user: str, lang: str = "en", cache_input: str | None = None
    ) -> Completion:
        if not self.enabled:
            raise LLMUnavailable(f"provider '{self.provider}' not configured")
        key = self._key(endpoint, cache_input if cache_input is not None else user, lang)
        if key in self._mem:
            return Completion(self._mem[key], self.provider, self.model_id, cached=True)
        disk = self.cache_dir / f"{key}.json" if self.cache_dir else None
        if disk is not None and disk.exists():
            text = json.loads(disk.read_text())["text"]
            self._mem[key] = text
            return Completion(text, self.provider, self.model_id, cached=True)
        last: Exception | None = None
        for attempt in range(2):  # one retry
            self.bucket.acquire()
            t0 = time.perf_counter()
            try:
                text = self._call(system, user)
                log.info(
                    "llm endpoint=%s provider=%s model=%s latency_ms=%d attempt=%d",
                    endpoint,
                    self.provider,
                    self.model_id,
                    (time.perf_counter() - t0) * 1000,
                    attempt + 1,
                )
                self._mem[key] = text
                if disk is not None:
                    try:
                        disk.parent.mkdir(exist_ok=True)
                        disk.write_text(json.dumps({"text": text}))
                    except OSError:
                        pass
                return Completion(text, self.provider, self.model_id)
            except Exception as e:  # network, throttling, auth: never surface details to the user
                last = e
                log.warning(
                    "llm endpoint=%s provider=%s failed attempt=%d error=%s",
                    endpoint,
                    self.provider,
                    attempt + 1,
                    type(e).__name__,
                )
        raise LLMUnavailable(type(last).__name__ if last else "unknown error")

    def _call(self, system: str, user: str) -> str:
        if self.provider == "bedrock":
            return self._bedrock_call(system, user)
        if self.provider == "groq":
            return self._groq_call(system, user)
        raise LLMUnavailable(self.provider)

    def _bedrock_call(self, system: str, user: str) -> str:
        if self._bedrock is None:
            import boto3  # optional dependency, imported only when Bedrock is used
            from botocore.config import Config

            self._bedrock = boto3.client(
                "bedrock-runtime",
                region_name=self.region,
                config=Config(read_timeout=TIMEOUT_S, connect_timeout=5, retries={"max_attempts": 1}),
            )
        r = self._bedrock.converse(
            modelId=self.model_id,
            system=[{"text": system}],
            messages=[{"role": "user", "content": [{"text": user}]}],
            inferenceConfig={"temperature": 0.2, "maxTokens": 700},
        )
        return "".join(part.get("text", "") for part in r["output"]["message"]["content"]).strip()

    def _groq_call(self, system: str, user: str) -> str:
        import httpx

        r = httpx.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {os.environ['GROQ_API_KEY']}"},
            json={
                "model": os.getenv("GROQ_MODEL_ID", ""),
                "temperature": 0.2,
                "max_tokens": 700,
                "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            },
            timeout=TIMEOUT_S,
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"].strip()
