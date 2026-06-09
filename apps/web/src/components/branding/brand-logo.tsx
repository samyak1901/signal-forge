import type { ComponentProps } from "react";
import { cn } from "@/lib/utils";

type LogoProps = ComponentProps<"span"> & {
  variant?: "full" | "icon";
};

export function BrandLogo({ variant = "full", className, ...props }: LogoProps) {
  return (
    <span
      className={cn("inline-flex items-center gap-2 font-heading font-semibold", className)}
      {...props}
    >
      <span className="flex size-6 items-center justify-center rounded-lg bg-primary text-[10px] font-bold text-primary-foreground">
        SF
      </span>
      {variant === "full" && <span>SignalForge</span>}
    </span>
  );
}
