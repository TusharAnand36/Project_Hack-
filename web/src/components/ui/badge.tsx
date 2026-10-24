import { cva, type VariantProps } from "class-variance-authority";
import type { HTMLAttributes } from "react";

import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center gap-1 rounded-md border px-2 py-0.5 text-sm font-medium",
  {
    variants: {
      variant: {
        ok: "border-ok text-ok",
        warn: "border-warn text-warn",
        bad: "border-bad text-bad",
        muted: "border-border text-muted-foreground",
      },
    },
    defaultVariants: { variant: "muted" },
  },
);

export interface BadgeProps extends HTMLAttributes<HTMLSpanElement>, VariantProps<typeof badgeVariants> {}

export function Badge({ className, variant, ...props }: BadgeProps) {
  return <span className={cn(badgeVariants({ variant }), className)} {...props} />;
}
