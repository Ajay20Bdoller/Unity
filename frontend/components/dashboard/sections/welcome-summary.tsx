"use client";

import { useAuth } from "@/lib/auth-context";
import { Card } from "@/components/ui/card";

const roleLabels: Record<string, string> = {
  student: "Student",
  parent: "Parent / Guardian",
  mentor: "Mentor",
  school_admin: "School / Institution",
  admin: "Admin",
};

export function WelcomeSummary() {
  const { user } = useAuth();
  if (!user) return null;

  return (
    <Card>
      <p className="text-sm text-muted">{roleLabels[user.role] ?? user.role}</p>
      <h1 className="mt-1 font-display text-2xl font-medium text-ink">Welcome, {user.full_name}</h1>
    </Card>
  );
}
