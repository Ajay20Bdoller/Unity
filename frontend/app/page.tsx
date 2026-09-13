"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { SiteNav } from "@/components/site-nav";
import { useLanguage } from "@/lib/language-context";

const journeyKeys = [1, 2, 3, 4, 5, 6, 7] as const;

export default function LandingPage() {
  const { t } = useLanguage();

  return (
    <>
      <SiteNav />
      <main className="mx-auto flex max-w-5xl flex-col px-6 py-16 sm:py-24">
        <section className="max-w-2xl">
          <h1 className="font-display text-4xl font-medium leading-[1.1] tracking-tight text-ink sm:text-6xl">
            {t("home.heroTitle")}
          </h1>
          <p className="mt-6 max-w-xl text-lg leading-relaxed text-muted">
            {t("home.heroSubtitle")}
          </p>
          <div className="mt-8 flex items-center gap-4">
            <Link href="/register">
              <Button className="px-6 py-3 text-base">{t("home.startExploring")}</Button>
            </Link>
            <Link href="/careers" className="text-sm font-medium text-ink hover:text-primary">
              {t("home.browseCareersFirst")} →
            </Link>
          </div>
        </section>

        <section className="mt-28">
          <ol className="grid gap-x-8 gap-y-10 sm:grid-cols-2 lg:grid-cols-4">
            {journeyKeys.map((n) => (
              <li key={n} className="border-l-2 border-primary/30 pl-4">
                <span className="font-display text-2xl text-primary/70">
                  {String(n).padStart(2, "0")}
                </span>
                <h2 className="mt-2 font-medium text-ink">{t(`home.step${n}Title`)}</h2>
                <p className="mt-1 text-sm leading-relaxed text-muted">{t(`home.step${n}Detail`)}</p>
              </li>
            ))}
          </ol>
        </section>
      </main>
    </>
  );
}
