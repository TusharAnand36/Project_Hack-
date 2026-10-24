import { useTranslation } from "react-i18next";

import type { Tag } from "@/api/client";
import { cn } from "@/lib/utils";

const COLOUR: Record<Tag, string> = {
  measured: "border-tag-measured text-tag-measured",
  published: "border-tag-published text-tag-published",
  assumed: "border-tag-assumed text-tag-assumed",
  synthetic: "border-tag-synthetic text-tag-synthetic",
};

/** Letter chip M/P/A/S plus colour; the full word is the accessible name. */
export function TagChip({ tag, className }: { tag: Tag; className?: string }) {
  const { t } = useTranslation();
  return (
    <span
      className={cn(
        "inline-flex h-5 min-w-5 items-center justify-center rounded border px-1 text-[0.7rem] font-bold leading-none",
        COLOUR[tag],
        className,
      )}
      title={t(`tag.${tag}`)}
    >
      <span aria-hidden="true">{t(`tag.letter.${tag}`)}</span>
      <span className="sr-only">{t(`tag.${tag}`)}</span>
    </span>
  );
}
