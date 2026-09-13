import { HTMLAttributes } from "react";
import clsx from "clsx";

export function Card({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={clsx(
        "rounded-xl border border-border bg-surface p-6 shadow-sm shadow-black/[0.03]",
        className
      )}
      {...props}
    />
  );
}
