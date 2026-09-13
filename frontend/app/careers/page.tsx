"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { api, type CareerCategory, type CareerListItem } from "@/lib/api";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { SiteNav } from "@/components/site-nav";

function CareersPageContent() {
  const searchParams = useSearchParams();
  const [categories, setCategories] = useState<CareerCategory[]>([]);
  const [careers, setCareers] = useState<CareerListItem[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(
    searchParams.get("category")
  );
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.careerCategories().then(setCategories).catch(() => setCategories([]));
  }, []);

  useEffect(() => {
    setLoading(true);
    const handle = setTimeout(() => {
      api
        .careers({ category: selectedCategory ?? undefined, q: search || undefined })
        .then(setCareers)
        .catch(() => setCareers([]))
        .finally(() => setLoading(false));
    }, 250); // debounce search typing
    return () => clearTimeout(handle);
  }, [selectedCategory, search]);

  return (
    <>
      <SiteNav />
      <main className="mx-auto max-w-5xl px-6 py-10">
        <h1 className="font-display text-2xl font-medium text-ink">Explore careers</h1>
        <p className="mt-1 text-sm text-muted">
          Browse career areas to understand what people in them actually do — not a test,
          just a way to explore.
        </p>

        <div className="mt-6 flex flex-wrap items-center gap-3">
          <Input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search careers..."
            className="max-w-xs"
          />
          <button
            type="button"
            onClick={() => setSelectedCategory(null)}
            className={`rounded-full border px-3 py-1.5 text-xs ${
              selectedCategory === null
                ? "border-primary bg-primary/10 text-primary"
                : "border-border text-ink hover:bg-border/30"
            }`}
          >
            All
          </button>
          {categories.map((c) => (
            <button
              key={c.key}
              type="button"
              onClick={() => setSelectedCategory(c.key)}
              className={`rounded-full border px-3 py-1.5 text-xs ${
                selectedCategory === c.key
                  ? "border-primary bg-primary/10 text-primary"
                  : "border-border text-ink hover:bg-border/30"
              }`}
            >
              {c.name}
            </button>
          ))}
        </div>

        <div className="mt-6 grid gap-4 sm:grid-cols-2">
          {loading && <p className="text-sm text-muted">Loading...</p>}
          {!loading && careers.length === 0 && (
            <p className="text-sm text-muted">No careers found. Try a different search.</p>
          )}
          {careers.map((career) => (
            <Link key={career.id} href={`/careers/${career.slug}`}>
              <Card className="h-full transition-shadow hover:shadow-sm">
                <h2 className="font-medium text-ink">{career.title}</h2>
                <p className="mt-2 text-sm text-muted line-clamp-3">{career.description}</p>
              </Card>
            </Link>
          ))}
        </div>
      </main>
    </>
  );
}

export default function CareersPage() {
  return (
    <Suspense fallback={null}>
      <CareersPageContent />
    </Suspense>
  );
}
