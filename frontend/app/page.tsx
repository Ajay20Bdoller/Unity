"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Sparkles, Users, Globe2, GraduationCap } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { SiteNav } from "@/components/site-nav";
import { useLanguage } from "@/lib/language-context";
import { useAuth } from "@/lib/auth-context";
import { api, type CareerListItem } from "@/lib/api";

const journeyKeys = [1, 2, 3, 4, 5, 6, 7] as const;

const WHY_ICONS = [Sparkles, Users, Globe2, GraduationCap];

export default function LandingPage() {
  const { t } = useLanguage();
  const { user } = useAuth();
  const [careers, setCareers] = useState<CareerListItem[]>([]);

  useEffect(() => {
    api.careers().then((list) => setCareers(list.slice(0, 3))).catch(() => setCareers([]));
  }, []);

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
            <Link href={user ? "/dashboard" : "/register"}>
              <Button className="px-6 py-3 text-base">
                {user ? t("home.goToDashboard") : t("home.startExploring")}
              </Button>
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

        {careers.length > 0 && (
          <section className="mt-28">
            <div className="flex items-baseline justify-between">
              <h2 className="font-display text-2xl font-medium text-ink">
                {t("home.featuredCareersTitle")}
              </h2>
              <Link href="/careers" className="text-sm font-medium text-primary hover:underline">
                {t("home.viewAllCareers")} →
              </Link>
            </div>
            <p className="mt-1 text-sm text-muted">{t("home.featuredCareersSubtitle")}</p>
            <div className="mt-6 grid gap-4 sm:grid-cols-3">
              {careers.map((c) => (
                <Link key={c.id} href={`/careers/${c.slug}`}>
                  <Card className="h-full hover:shadow-sm">
                    <h3 className="font-medium text-ink">{c.title}</h3>
                    <p className="mt-2 line-clamp-3 text-sm text-muted">{c.description}</p>
                  </Card>
                </Link>
              ))}
            </div>
          </section>
        )}

        <section className="mt-28">
          <h2 className="font-display text-2xl font-medium text-ink">{t("home.whyTitle")}</h2>
          <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {[1, 2, 3, 4].map((n) => {
              const Icon = WHY_ICONS[n - 1];
              return (
                <Card key={n}>
                  <span className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10 text-primary">
                    <Icon size={16} />
                  </span>
                  <h3 className="mt-3 font-medium text-ink">{t(`home.why${n}Title`)}</h3>
                  <p className="mt-1 text-sm leading-relaxed text-muted">
                    {t(`home.why${n}Detail`)}
                  </p>
                </Card>
              );
            })}
          </div>
        </section>
      </main>
    </>
  );
}
