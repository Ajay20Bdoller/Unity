"use client";

import { useEffect, useState } from "react";
import { api, ApiError, type GuardianRelationship } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Field } from "@/components/ui/field";
import { SiteNav } from "@/components/site-nav";

const STATUS_LABEL: Record<string, string> = {
  pending: "Waiting for your parent to verify",
  verified: "Verified",
  rejected: "Declined",
};

export default function StudentGuardiansPage() {
  const { user, loading } = useAuth();
  const [relationships, setRelationships] = useState<GuardianRelationship[]>([]);
  const [parentEmail, setParentEmail] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  function load() {
    api.myGuardians().then(setRelationships).catch(() => setRelationships([]));
  }

  useEffect(() => {
    if (user?.role === "student") load();
  }, [user]);

  async function invite(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await api.inviteGuardian(parentEmail);
      setParentEmail("");
      load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong.");
    } finally {
      setSubmitting(false);
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

  return (
    <>
      <SiteNav />
      <main className="mx-auto max-w-2xl px-6 py-10">
        <h1 className="font-display text-2xl font-medium text-ink">Parent / guardian</h1>
        <p className="mt-1 text-sm text-muted">
          Mentorship needs your parent or guardian&apos;s consent first. Invite them here using
          the email they registered with — they&apos;ll need to verify the link and grant
          consent from their own account.
        </p>

        <Card className="mt-6">
          <form onSubmit={invite} className="flex items-end gap-2">
            <div className="flex-1">
              <Field label="Parent's registered email" htmlFor="parent_email">
                <Input
                  id="parent_email"
                  type="email"
                  required
                  value={parentEmail}
                  onChange={(e) => setParentEmail(e.target.value)}
                  placeholder="parent@example.com"
                />
              </Field>
            </div>
            <Button type="submit" disabled={submitting || !parentEmail}>
              {submitting ? "Sending…" : "Invite"}
            </Button>
          </form>
          {error && <p className="mt-2 text-sm text-danger">{error}</p>}
          <p className="mt-2 text-xs text-muted">
            Your parent needs to already have a Unity account, registered as a parent, with this
            exact email.
          </p>
        </Card>

        <div className="mt-6 space-y-2">
          {relationships.length === 0 && (
            <p className="text-sm text-muted">You haven&apos;t invited a parent yet.</p>
          )}
          {relationships.map((rel) => (
            <Card key={rel.id} className="py-3">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-ink">
                    {rel.parent_name ?? "A parent"}
                  </p>
                  {rel.parent_email && <p className="text-xs text-muted">{rel.parent_email}</p>}
                </div>
                <span className="text-xs text-muted">
                  {STATUS_LABEL[rel.status] ?? rel.status}
                </span>
              </div>
            </Card>
          ))}
        </div>
      </main>
    </>
  );
}
