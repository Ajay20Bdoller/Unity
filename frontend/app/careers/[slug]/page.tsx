"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { api, ApiError, type CareerDetail } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { SiteNav } from "@/components/site-nav";

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  if (!children) return null;
  return (
    <div className="mt-6">
      <h2 className="font-medium text-ink">{title}</h2>
      <div className="mt-1 text-sm text-muted">{children}</div>
    </div>
  );
}

export default function CareerDetailPage() {
  const { slug } = useParams<{ slug: string }>();
  const { user, loading: authLoading } = useAuth();
  const [career, setCareer] = useState<CareerDetail | null>(null);
  const [notFound, setNotFound] = useState(false);
  const [interested, setInterested] = useState(false);
  const [savingInterest, setSavingInterest] = useState(false);

  useEffect(() => {
    if (authLoading || !user) return;
    api
      .career(slug, user.preferred_language)
      .then(setCareer)
      .catch((err) => {
        if (err instanceof ApiError && err.status === 404) setNotFound(true);
      });
  }, [slug, user, authLoading]);

  useEffect(() => {
    if (user?.role !== "student" || !career) return;
    api
      .myCareerInterests()
      .then((list) => setInterested(list.some((c) => c.id === career.id)))
      .catch(() => {});
  }, [user, career]);

  async function toggleInterest() {
    if (!career) return;
    setSavingInterest(true);
    try {
      if (interested) {
        await api.removeCareerInterest(career.id);
      } else {
        await api.addCareerInterest(career.id);
      }
      setInterested(!interested);
    } finally {
      setSavingInterest(false);
    }
  }

  if (authLoading) return null;

  if (!user) {
    return (
      <>
        <SiteNav />
        <main className="mx-auto max-w-3xl px-6 py-10">
          <Card>
            <h1 className="font-display text-lg font-medium text-ink">
              Log in to see full details
            </h1>
            <p className="mt-2 text-sm text-muted">
              Browsing careers is free — an account (free, takes a minute) unlocks the full
              picture: subjects, eligibility, skills, exams, and pathways.
            </p>
            <div className="mt-4 flex gap-3">
              <Link href="/register">
                <Button>Create an account</Button>
              </Link>
              <Link href="/login">
                <Button variant="secondary">Log in</Button>
              </Link>
            </div>
          </Card>
        </main>
      </>
    );
  }

  if (notFound) {
    return (
      <>
        <SiteNav />
        <main className="mx-auto max-w-3xl px-6 py-10">
          <p className="text-sm text-muted">Career not found.</p>
        </main>
      </>
    );
  }

  if (!career) {
    return (
      <>
        <SiteNav />
        <main className="mx-auto max-w-3xl px-6 py-10">
          <p className="text-sm text-muted">Loading...</p>
        </main>
      </>
    );
  }

  return (
    <>
      <SiteNav />
      <main className="mx-auto max-w-3xl px-6 py-10">
        <p className="text-sm text-muted">{career.category.name}</p>
        <div className="mt-1 flex items-start justify-between gap-4">
          <h1 className="font-display text-2xl font-medium text-ink">{career.title}</h1>
          {user?.role === "student" && (
            <Button variant="secondary" disabled={savingInterest} onClick={toggleInterest}>
              {interested ? "Remove interest" : "I'm interested"}
            </Button>
          )}
        </div>

        <Card className="mt-4">
          <Section title="What is this career?">{career.description}</Section>
          <Section title="What should I study?">
            {career.subjects?.length ? career.subjects.join(", ") : null}
          </Section>
          <Section title="Who can pursue this?">{career.eligibility}</Section>
          <Section title="What skills help?">
            {career.skills?.length ? career.skills.join(", ") : null}
          </Section>
          <Section title="Which exams/pathways exist?">
            {career.entrance_exams?.length ? career.entrance_exams.join(", ") : null}
          </Section>
          <Section title="Education pathway">{career.education_pathway}</Section>
          <Section title="What can I explore next?">{career.roadmap}</Section>
        </Card>

        {career.related_careers.length > 0 && (
          <div className="mt-8">
            <h2 className="font-medium text-ink">Related careers</h2>
            <div className="mt-3 grid gap-3 sm:grid-cols-2">
              {career.related_careers.map((related) => (
                <Link key={related.id} href={`/careers/${related.slug}`}>
                  <Card className="hover:shadow-sm">
                    <p className="text-sm font-medium text-ink">{related.title}</p>
                  </Card>
                </Link>
              ))}
            </div>
          </div>
        )}
      </main>
    </>
  );
}
