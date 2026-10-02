import Link from "next/link";
import { SiteNav } from "@/components/site-nav";
import { Button } from "@/components/ui/button";

export default function NotFound() {
  return (
    <>
      <SiteNav />
      <main className="mx-auto flex min-h-[calc(100vh-57px)] max-w-2xl flex-col items-center justify-center px-6 text-center">
        <p className="font-display text-sm text-primary">404</p>
        <h1 className="mt-2 font-display text-3xl font-medium text-ink">
          This page doesn&apos;t exist.
        </h1>
        <p className="mt-3 text-muted">
          The link might be broken, or the page may have moved.
        </p>
        <Link href="/" className="mt-6">
          <Button>Back to home</Button>
        </Link>
      </main>
    </>
  );
}
