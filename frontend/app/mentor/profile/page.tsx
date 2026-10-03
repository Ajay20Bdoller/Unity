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
import { PhotoUploadField } from "@/components/ui/photo-upload-field";

export default function MentorProfilePage() {
  const { user, loading } = useAuth();
  const [profile, setProfile] = useState<MentorPublicProfile | null>(null);
  const [bio, setBio] = useState("");
  const [availability, setAvailability] = useState("");
  const [photoUrl, setPhotoUrl] = useState("");
  const [categories, setCategories] = useState<CareerCategory[]>([]);
  const [languages, setLanguages] = useState<Language[]>([]);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  function load() {
    if (!user) return;
    api
      .myMentorProfile()
      .then((mine) => {
        setProfile(mine);
        setBio(mine.bio ?? "");
        setAvailability(mine.availability_note ?? "");
        setPhotoUrl(mine.photo_url ?? "");
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
    setSaved(false);
    try {
      await api.updateMentorProfile({ bio, availability_note: availability, photo_url: photoUrl });
      load();
      setSaved(true);
    } finally {
      setSaving(false);
    }
  }

  // Expertise/language picks save immediately on click (no data lost
  // if someone navigates away mid-edit) — the Save button below only
  // covers bio/availability/photo, which need a deliberate "done
  // editing this text" moment. Both live in one form, one flow, Save
  // positioned after everything so selecting expertise/languages
  // doesn't feel skippable or separate from "the form."
  async function toggleExpertise(categoryId: string, active: boolean) {
    if (active) {
      await api.removeMentorExpertise(categoryId);
    } else {
      await api.addMentorExpertise(categoryId);
    }
    load();
  }

  async function toggleLanguage(code: string, active: boolean) {
    if (active) {
      await api.removeMentorLanguage(code);
    } else {
      await api.addMentorLanguage(code);
    }
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
          Students will see this when browsing mentors, once an admin approves your profile.
        </p>

        <Card className="mt-6">
          <label className="text-sm font-medium text-ink">Photo</label>
          <div className="mt-1">
            <PhotoUploadField value={photoUrl} onChange={setPhotoUrl} />
          </div>

          <label className="mt-4 block text-sm font-medium text-ink">Bio</label>
          <textarea
            value={bio}
            onChange={(e) => setBio(e.target.value)}
            rows={3}
            className="mt-1 w-full rounded-md border border-border bg-surface px-3 py-2 text-sm text-ink focus:outline-none focus:ring-2 focus:ring-primary/40"
          />

          <label className="mt-4 block text-sm font-medium text-ink">Availability</label>
          <Input
            value={availability}
            onChange={(e) => setAvailability(e.target.value)}
            placeholder="e.g. Weekday evenings IST"
            className="mt-1"
          />

          <p className="mt-5 text-sm font-medium text-ink">Expertise</p>
          <p className="text-xs text-muted">Tap to select — saves as you go.</p>
          <div className="mt-2 flex flex-wrap gap-2">
            {categories.map((c) => {
              const active = Boolean(profile?.expertise.includes(c.key));
              return (
                <button
                  key={c.key}
                  type="button"
                  onClick={() => toggleExpertise(c.id, active)}
                  className={`rounded-full border px-3 py-1.5 text-xs ${
                    active
                      ? "border-primary bg-primary/10 text-primary"
                      : "border-border text-ink hover:bg-border/30"
                  }`}
                >
                  {c.name}
                  {active && " ×"}
                </button>
              );
            })}
          </div>

          <p className="mt-5 text-sm font-medium text-ink">Languages</p>
          <p className="text-xs text-muted">Tap to select — saves as you go.</p>
          <div className="mt-2 flex flex-wrap gap-2">
            {languages.map((l) => {
              const active = Boolean(profile?.languages.includes(l.code));
              return (
                <button
                  key={l.code}
                  type="button"
                  onClick={() => toggleLanguage(l.code, active)}
                  className={`rounded-full border px-3 py-1.5 text-xs ${
                    active
                      ? "border-primary bg-primary/10 text-primary"
                      : "border-border text-ink hover:bg-border/30"
                  }`}
                >
                  {l.native_name}
                  {active && " ×"}
                </button>
              );
            })}
          </div>

          <div className="mt-6 border-t border-border pt-4">
            <Button disabled={saving} onClick={saveProfile}>
              {saving ? "Saving..." : "Save"}
            </Button>
            {saved && <span className="ml-3 text-xs text-primary">Saved.</span>}
          </div>
        </Card>
      </main>
    </>
  );
}
