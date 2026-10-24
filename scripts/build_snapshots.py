"""Build everything the web app needs to run with no API (website plan Phase 8, NFR-07).

Writes into web/public/:
  snapshots/<preset>.<lang>.json          /analyze result + {"snapshot": {engine, dataset, generated_at, lang}}
  snapshots/<preset>.<lang>.explain.json  template explanation (no LLM, numbers from the engine)
  snapshots/presets.json                  the preset list for the Input screen
  offline-data/<file>.json                dataset files the screens read (sources, by-products, ...)
  open-data-pack.zip                      /data + schemas + sources + DATA_TODO + a README (FR-22)

Run after any data or engine change:  make snapshots
"""

from __future__ import annotations

import json
import sys
import zipfile
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "engine"), str(ROOT)]

from api.llm import service  # noqa: E402
from api.llm.client import LLMClient  # noqa: E402
from compass import __version__  # noqa: E402
from compass.analyze import analyze  # noqa: E402
from compass.contract import AnalyzeRequest  # noqa: E402
from compass.data import DEFAULT_DATA_DIR, FILES, load_dataset, read_raw, report  # noqa: E402

PUBLIC = ROOT / "web" / "public"
LANGS = ("en", "hi")
OFFLINE_FILES = ("sources", "byproducts", "applications", "treatments", "functional_evidence", "research_evidence")

PACK_README = """# Upcycle Compass open data pack

Dataset version: {version}. Generated {generated}.

Every value carries `tag` (measured / published / assumed / synthetic), `evidence_grade` (A-D),
`source_id` (see sources.json) and, for evidence borrowed from another material, `applicability` (alpha).
Missing values are null and listed in DATA_TODO.md. JSON Schemas are in schema/.

Licence: not chosen yet by the team. Each row cites its source; cite the original sources when you reuse
a value. Unpublished team documents are cited but not included.

Proof of concept. Decision support only; not a regulatory approval.
"""


def write(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")


def main() -> int:
    ds = load_dataset()
    stamp = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    llm = LLMClient("template", cache_dir=None)  # snapshots never depend on an LLM
    snaps = PUBLIC / "snapshots"
    for pid, preset in ds.presets.items():
        req = AnalyzeRequest.model_validate(preset.payload)
        result = analyze(req, ds)
        body = result.model_dump(mode="json")
        body["meta"]["generated_at"] = stamp
        for lang in LANGS:
            body["snapshot"] = {
                "engine_version": __version__,
                "dataset_version": ds.version,
                "generated_at": stamp,
                "lang": lang,
                "preset": pid,
            }
            write(snaps / f"{pid}.{lang}.json", body)
            write(
                snaps / f"{pid}.{lang}.explain.json", service.explain(result, req, llm, set(ds.sources), lang)
            )
        print(f"snapshot {pid}: {result.verdict.label.value}, {result.meta.elapsed_ms} ms")
    write(snaps / "presets.json", [p.model_dump() for p in ds.presets.values()])
    off = PUBLIC / "offline-data"
    for name in OFFLINE_FILES:
        write(off / f"{name}.json", read_raw(name))
    write(off / "report.json", report(ds))

    pack = PUBLIC / "open-data-pack.zip"
    with zipfile.ZipFile(pack, "w", zipfile.ZIP_DEFLATED) as z:
        for name in FILES:
            z.write(DEFAULT_DATA_DIR / f"{name}.json", f"data/{name}.json")
        for f in sorted((DEFAULT_DATA_DIR / "schema").glob("*.json")):
            z.write(f, f"data/schema/{f.name}")
        z.write(ROOT / "DATA_TODO.md", "DATA_TODO.md")
        z.writestr("README.md", PACK_README.format(version=ds.version, generated=stamp))
    print(f"wrote {pack.relative_to(ROOT)} ({pack.stat().st_size // 1024} KB) and offline data")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
