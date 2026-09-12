"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { api, ApiError, type DashboardSection } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { SECTION_REGISTRY } from "@/components/dashboard/section-registry";

export default function DashboardPage() {
  const { user, loading, logout } = useAuth();
  const [sections, setSections] = useState<DashboardSection[] | null>(null);
  const [sectionsError, setSectionsError] = useState<string | null>(null);

  useEffect(() => {
    if (!user) return;
    api
      .dashboardSections()
      .then(setSections)
      .catch((err) => {
        setSectionsError(err instanceof ApiError ? err.message : "Couldn't load your dashboard.");
      });
  }, [user]);

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
        <p className="text-sm text-muted">Session expired. Please log in again.</p>
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-4xl px-6 py-12">
      <header className="flex items-center justify-end">
        <Button variant="secondary" onClick={logout}>
          Log out
        </Button>
      </header>

      <div className="mt-6 space-y-6">
        {sectionsError && <p className="text-sm text-danger">{sectionsError}</p>}
        {sections?.map((section) => {
          const SectionComponent = SECTION_REGISTRY[section.component_key];
          // Unknown component_key -> skip it silently. The DB can only
          // pick from known components, never inject new ones; a key
          // that doesn't match anything here must fail safe, not crash
          // the dashboard.
          if (!SectionComponent) return null;
          return <SectionComponent key={section.key} />;
        })}
      </div>
    </main>
  );
}
