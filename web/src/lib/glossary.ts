import glossary from "@/locales/glossary.hi.json";

const TERMS = Object.entries(glossary.terms as Record<string, string>).sort(
  (a, b) => b[0].length - a[0].length,
);

/** "Aflatoxin B1" -> "Aflatoxin B1 (एफ्लाटॉक्सिन)" when Hindi is active: English term kept, Hindi gloss added. */
export function gloss(text: string, lang: string): string {
  if (lang !== "hi") return text;
  const lower = text.toLowerCase();
  const hit = TERMS.find(([en]) => lower.includes(en));
  return hit ? `${text} (${hit[1]})` : text;
}
