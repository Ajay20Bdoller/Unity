"use client";

import { useAuth } from "@/lib/auth-context";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

const roleLabels: Record<string, string> = {
  student: "Student",
  parent: "Parent / Guardian",
  mentor: "Mentor",
  school: "School / Institution",
  admin: "Admin",
};

export default function DashboardPage() {
  const { user, loading, logout } = useAuth();

  if (loading) {
    return (
      <main className="flex min-h-screen items-center justify-center">
        <p className="text-sm text-muted">Loading your dashboard…</p>
      </main>
    );
  }

  if (!user) {
    return (
      <main className="flex min-h-screen items-center justify-center">
        <p className="text-sm text-muted">
          Session expired. Please log in again.
        </p>
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-4xl px-6 py-12">
      <header className="flex items-center justify-between">
        <div>
          <p className="text-sm text-muted">
            {roleLabels[user.role] ?? user.role}
          </p>
          <h1 className="text-2xl font-semibold text-ink">
            Welcome, {user.full_name}
          </h1>
        </div>
        <Button variant="secondary" onClick={logout}>
          Log out
        </Button>
      </header>

      <Card className="mt-10">
        <h2 className="font-medium text-ink">Your dashboard is being built</h2>
        <p className="mt-2 text-sm text-muted">
          This is the foundation phase — auth, roles, and profiles are live.
          The AI Career Assistant and your personalised sections land in the
          next build phase.
        </p>
      </Card>
    </main>
  );
}
