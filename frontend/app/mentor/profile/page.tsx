"use client";

import { useEffect, useState } from "react";
import {
  api,
  type CareerCategory,
  type Language,
  type MentorPublicProfile,
} from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { SiteNav } from "@/components/site-nav";

export default function MentorProfilePage() {
  const { user, loading } = useAuth();
  const [profile, setProfile] = useState<MentorPublicProfile | null>(null);
  const [bio, setBio] = useState("");
  const [availability, setAvailability] = useState("");
  const [categories, setCategories] = useState<CareerCategory[]>([]);
  const [languages, setLanguages] = useState<Language[]>([]);
  const [saving, setSaving] = useState(false);

  function load() {
    if (!user) return;
    api
      .mentors()
      .then((all) => {
        const mine = all.find((m) => m.user_id === user.id);
        if (mine) {
          setProfile(mine);
          setBio(mine.bio ?? "");
          setAvailability(mine.availability_note ?? "");
        }
      })
      .catch(() => {});
  }

  useEffect(() => {
    if (user?.role !== "mentor") return;
    load();
    api.careerCategories().then(setCategories).catch(() => setCategories([]));
    api.languages().then(setLanguages).catch(() => setLanguages([]));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user]);

  async function saveProfile() {
    setSaving(true);
    try {
      await api.updateMentorProfile({ bio, availability_note: availability });
      load();
    } finally {
      setSaving(false);
    }
  }

  async function toggleExpertise(categoryId: string) {
    await api.addMentorExpertise(categoryId);
    load();
  }

  async function toggleLanguage(code: string) {
    await api.addMentorLanguage(code);
    load();
  }

  if (loading) return null;
  if (!user || user.role !== "mentor") {
    return (
      <>
        <SiteNav />
        <main className="mx-auto max-w-2xl px-6 py-10">
          <p className="text-sm text-muted">This page is available to mentors only.</p>
        </main>
      </>
    );
  }

  return (
    <>
      <SiteNav />
      <main className="mx-auto max-w-2xl px-6 py-10">
        <h1 className="font-display text-2xl font-medium text-ink">My mentor profile</h1>
        <p className="mt-1 text-sm text-muted">
          Students will see this when browsing mentors.
        </p>

        <Card className="mt-6">
          <label className="text-sm font-medium text-ink">Bio</label>
          <textarea
            value={bio}
            onChange={(e) => setBio(e.target.value)}
            rows={3}
            className="mt-1 w-full rounded-md border border-border bg-surface px-3 py-2 text-sm text-ink focus:outline-none focus:ring-2 focus:ring-primary/40"
          />
          <label className="mt-3 block text-sm font-medium text-ink">Availability</label>
          <Input
            value={availability}
            onChange={(e) => setAvailability(e.target.value)}
            placeholder="e.g. Weekday evenings IST"
            className="mt-1"
          />
          <Button className="mt-3" disabled={saving} onClick={saveProfile}>
            {saving ? "Saving..." : "Save"}
          </Button>
        </Card>

        <Card className="mt-4">
          <p className="text-sm font-medium text-ink">Expertise</p>
          <div className="mt-2 flex flex-wrap gap-2">
            {categories.map((c) => {
              const active = profile?.expertise.includes(c.key);
              return (
                <button
                  key={c.key}
                  type="button"
                  disabled={active}
                  onClick={() => toggleExpertise(c.id)}
                  className={`rounded-full border px-3 py-1.5 text-xs ${
                    active
                      ? "border-primary bg-primary/10 text-primary"
                      : "border-border text-ink hover:bg-border/30"
                  }`}
                >
                  {c.name}
                </button>
              );
            })}
          </div>
        </Card>

        <Card className="mt-4">
          <p className="text-sm font-medium text-ink">Languages</p>
          <div className="mt-2 flex flex-wrap gap-2">
            {languages.map((l) => {
              const active = profile?.languages.includes(l.code);
              return (
                <button
                  key={l.code}
                  type="button"
                  disabled={active}
                  onClick={() => toggleLanguage(l.code)}
                  className={`rounded-full border px-3 py-1.5 text-xs ${
                    active
                      ? "border-primary bg-primary/10 text-primary"
                      : "border-border text-ink hover:bg-border/30"
                  }`}
                >
                  {l.native_name}
                </button>
              );
            })}
          </div>
        </Card>
      </main>
    </>
  );
}
