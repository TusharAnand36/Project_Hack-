// Every English key must exist in Hindi unless it is safety wording kept in English until reviewed
// (src/locales/review.json); no stale Hindi keys; interpolation placeholders must match.
import { readFileSync } from "node:fs";

const load = (f) => JSON.parse(readFileSync(new URL(`../src/locales/${f}`, import.meta.url), "utf8"));
const flat = (o, p = "") =>
  Object.entries(o).flatMap(([k, v]) => (v && typeof v === "object" ? flat(v, `${p}${k}.`) : [[`${p}${k}`, v]]));
const en = Object.fromEntries(flat(load("en.json")));
const hi = Object.fromEntries(flat(load("hi.json")));
const keep = new Set(load("review.json").hi.english_until_reviewed);
const vars = (s) => [...String(s).matchAll(/{{\s*(\w+)\s*}}/g)].map((m) => m[1]).sort().join(",");

const errors = [];
for (const k of Object.keys(en)) {
  if (keep.has(k)) {
    if (k in hi) errors.push(`${k}: safety wording must stay in English until reviewed (remove it from hi.json)`);
  } else if (!(k in hi)) errors.push(`${k}: missing in hi.json`);
  else if (vars(en[k]) !== vars(hi[k])) errors.push(`${k}: placeholders differ (${vars(en[k])} vs ${vars(hi[k])})`);
}
for (const k of Object.keys(hi)) if (!(k in en)) errors.push(`${k}: in hi.json but not in en.json`);
for (const k of keep) if (!(k in en)) errors.push(`${k}: listed in review.json but not an English key`);

if (errors.length) {
  console.error(errors.join("\n"));
  process.exit(1);
}
console.log(`locales ok: ${Object.keys(hi).length} Hindi strings, ${keep.size} kept in English until reviewed`);
