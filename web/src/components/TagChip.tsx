import { useTranslation } from "react-i18next";

import type { Tag } from "@/api/client";
import { cn } from "@/lib/utils";

const COLOUR: Record<Tag, string> = {
  measured: "border-tag-measured text-tag-measured",
  published: "border-tag-published text-tag-published",
  assumed: "border-border text-muted-foreground",
  synthetic: "border-tag-synthetic text-tag-synthetic",
};

/** Letter chip M/P/A/S plus colour; the full word is the accessible name. */
export function TagChip({ tag, className }: { tag: Tag; className?: string }) {
  const { t } = useTranslation();
  return (
    <span
      className={cn(
        "inline-flex min-h-5 items-center justify-center rounded border px-1 text-[0.65rem] font-medium leading-normal",
        COLOUR[tag],
        className,
      )}
      title={t(`tag.${tag}`)}
    >
      {t(`tag.${tag}`)}
    </span>
  );
}
