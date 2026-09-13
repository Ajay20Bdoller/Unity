"use client";

import { useEffect, useState } from "react";
import { api, ApiError, type State, type StudentProfile } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Field } from "@/components/ui/field";
import { SiteNav } from "@/components/site-nav";

type EditableField = keyof Omit<StudentProfile, "user_id">;

export default function StudentProfilePage() {
  const { user, loading } = useAuth();
  const [profile, setProfile] = useState<StudentProfile | null>(null);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [states, setStates] = useState<State[]>([]);

  useEffect(() => {
    api.states().then(setStates).catch(() => setStates([]));
  }, []);

  useEffect(() => {
    if (user?.role === "student") {
      api.myStudentProfile().then(setProfile).catch(() => {});
    }
  }, [user]);

  function set(field: EditableField, value: string) {
    setProfile((prev) => (prev ? { ...prev, [field]: value } : prev));
    setSaved(false);
  }

  async function save() {
    if (!profile) return;
    setSaving(true);
    setError(null);
    try {
      const updated = await api.updateMyStudentProfile({
        date_of_birth: profile.date_of_birth ?? undefined,
        class_level: profile.class_level ?? undefined,
        school_name: profile.school_name ?? undefined,
        address: profile.address ?? undefined,
        district: profile.district ?? undefined,
        state: profile.state ?? undefined,
        country: profile.country ?? undefined,
        parent_name: profile.parent_name ?? undefined,
        parent_relation: profile.parent_relation ?? undefined,
        gender: profile.gender ?? undefined,
      });
      setProfile(updated);
      setSaved(true);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong.");
    } finally {
      setSaving(false);
    }
  }

  if (loading) return null;
  if (!user || user.role !== "student") {
    return (
      <>
        <SiteNav />
        <main className="mx-auto max-w-2xl px-6 py-10">
          <p className="text-sm text-muted">This page is available to students only.</p>
        </main>
      </>
    );
  }
  if (!profile) {
    return (
      <>
        <SiteNav />
        <main className="mx-auto max-w-2xl px-6 py-10">
          <p className="text-sm text-muted">Loading...</p>
        </main>
      </>
    );
  }

  return (
    <>
      <SiteNav />
      <main className="mx-auto max-w-2xl px-6 py-10">
        <h1 className="font-display text-2xl font-medium text-ink">My profile</h1>

        <Card className="mt-6 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <Field label="Date of birth" htmlFor="dob">
              <Input
                id="dob"
                type="date"
                value={profile.date_of_birth ?? ""}
                onChange={(e) => set("date_of_birth", e.target.value)}
              />
            </Field>
            <Field label="Class" htmlFor="class_level">
              <Input
                id="class_level"
                value={profile.class_level ?? ""}
                onChange={(e) => set("class_level", e.target.value)}
                placeholder="e.g. 10"
              />
            </Field>
          </div>
          <Field label="School name" htmlFor="school_name">
            <Input
              id="school_name"
              value={profile.school_name ?? ""}
              onChange={(e) => set("school_name", e.target.value)}
            />
          </Field>
          <div className="grid grid-cols-2 gap-4">
            <Field label="Parent/guardian name" htmlFor="parent_name">
              <Input
                id="parent_name"
                value={profile.parent_name ?? ""}
                onChange={(e) => set("parent_name", e.target.value)}
              />
            </Field>
            <Field label="Relation" htmlFor="parent_relation">
              <Input
                id="parent_relation"
                value={profile.parent_relation ?? ""}
                onChange={(e) => set("parent_relation", e.target.value)}
              />
            </Field>
          </div>
          <Field label="Home address" htmlFor="address">
            <Input
              id="address"
              value={profile.address ?? ""}
              onChange={(e) => set("address", e.target.value)}
            />
          </Field>
          <div className="grid grid-cols-3 gap-4">
            <Field label="District" htmlFor="district">
              <Input
                id="district"
                value={profile.district ?? ""}
                onChange={(e) => set("district", e.target.value)}
              />
            </Field>
            <Field label="State" htmlFor="state">
              <select
                id="state"
                value={profile.state ?? ""}
                onChange={(e) => set("state", e.target.value)}
                className="w-full rounded-md border border-border bg-surface px-3 py-2 text-sm text-ink focus:outline-none focus:ring-2 focus:ring-primary/40"
              >
                <option value="">Select</option>
                {states.map((s) => (
                  <option key={s.id} value={s.name}>
                    {s.name}
                  </option>
                ))}
              </select>
            </Field>
            <Field label="Country" htmlFor="country">
              <Input
                id="country"
                value={profile.country ?? ""}
                onChange={(e) => set("country", e.target.value)}
              />
            </Field>
          </div>
          <Field label="Gender (optional)" htmlFor="gender">
            <Input
              id="gender"
              value={profile.gender ?? ""}
              onChange={(e) => set("gender", e.target.value)}
            />
          </Field>

          {error && <p className="text-sm text-danger">{error}</p>}
          <div className="flex items-center gap-3">
            <Button disabled={saving} onClick={save}>
              {saving ? "Saving…" : "Save changes"}
            </Button>
            {saved && <span className="text-sm text-primary">Saved.</span>}
          </div>
        </Card>
      </main>
    </>
  );
}
