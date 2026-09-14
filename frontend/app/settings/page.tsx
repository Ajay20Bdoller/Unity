"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api, ApiError } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Field } from "@/components/ui/field";
import { SiteNav } from "@/components/site-nav";

export default function SettingsPage() {
  const { user, loading } = useAuth();
  const router = useRouter();
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [done, setDone] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    if (newPassword !== confirmPassword) {
      setError("New passwords don't match.");
      return;
    }
    setSubmitting(true);
    try {
      await api.changePassword(currentPassword, newPassword);
      setDone(true);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong.");
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) return null;
  if (!user) {
    return (
      <>
        <SiteNav />
        <main className="mx-auto max-w-md px-6 py-10">
          <p className="text-sm text-muted">Log in to manage your settings.</p>
        </main>
      </>
    );
  }

  return (
    <>
      <SiteNav />
      <main className="mx-auto max-w-md px-6 py-10">
        <h1 className="font-display text-2xl font-medium text-ink">Settings</h1>
        <p className="mt-1 text-sm text-muted">{user.email ?? user.mobile_number}</p>

        <Card className="mt-6">
          <h2 className="font-medium text-ink">Change password</h2>

          {done ? (
            <div className="mt-3">
              <p className="text-sm text-primary">
                Password changed. For safety, you&apos;ve been logged out everywhere — log back
                in with your new password.
              </p>
              <Button className="mt-3" onClick={() => router.push("/login")}>
                Log in
              </Button>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="mt-3 space-y-3">
              <Field label="Current password" htmlFor="current_password">
                <Input
                  id="current_password"
                  type="password"
                  required
                  value={currentPassword}
                  onChange={(e) => setCurrentPassword(e.target.value)}
                />
              </Field>
              <Field label="New password" htmlFor="new_password">
                <Input
                  id="new_password"
                  type="password"
                  required
                  minLength={8}
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                />
              </Field>
              <Field label="Confirm new password" htmlFor="confirm_password">
                <Input
                  id="confirm_password"
                  type="password"
                  required
                  minLength={8}
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                />
              </Field>
              {error && <p className="text-sm text-danger">{error}</p>}
              <Button type="submit" disabled={submitting}>
                {submitting ? "Changing…" : "Change password"}
              </Button>
            </form>
          )}
        </Card>
      </main>
    </>
  );
}
