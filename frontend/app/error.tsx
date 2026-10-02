"use client";

import { useEffect } from "react";
import Link from "next/link";
import { SiteNav } from "@/components/site-nav";
import { Button } from "@/components/ui/button";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Logged client-side only — no error-tracking service wired up yet
    // (see CLAUDE.md gaps), so this is the only record of what broke
    // until one exists.
    console.error(error);
  }, [error]);

  return (
    <>
      <SiteNav />
      <main className="mx-auto flex min-h-[calc(100vh-57px)] max-w-2xl flex-col items-center justify-center px-6 text-center">
        <p className="font-display text-sm text-danger">Something went wrong</p>
        <h1 className="mt-2 font-display text-3xl font-medium text-ink">
          That didn&apos;t work.
        </h1>
        <p className="mt-3 text-muted">
          Try again, or head back home if it keeps happening.
        </p>
        <div className="mt-6 flex gap-3">
          <Button onClick={reset}>Try again</Button>
          <Link href="/">
            <Button variant="secondary">Back to home</Button>
          </Link>
        </div>
      </main>
    </>
  );
}
