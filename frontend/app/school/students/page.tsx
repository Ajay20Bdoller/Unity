"use client";

import { useEffect, useState } from "react";
import { api, ApiError, type SchoolAdminStudent } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { Card } from "@/components/ui/card";
import { SiteNav } from "@/components/site-nav";

export default function SchoolStudentsPage() {
  const { user, loading } = useAuth();
  const [students, setStudents] = useState<SchoolAdminStudent[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (user?.role !== "school_admin") return;
    api
      .mySchoolStudents()
      .then(setStudents)
      .catch((err) => {
        setError(err instanceof ApiError ? err.message : "Something went wrong.");
        setStudents([]);
      });
  }, [user]);

  if (loading) return null;
  if (!user || user.role !== "school_admin") {
    return (
      <>
        <SiteNav />
        <main className="mx-auto max-w-2xl px-6 py-10">
          <p className="text-sm text-muted">This area is available to school admins only.</p>
        </main>
      </>
    );
  }

  return (
    <>
      <SiteNav />
      <main className="mx-auto max-w-2xl px-6 py-10">
        <h1 className="font-display text-2xl font-medium text-ink">Students</h1>
        <p className="mt-1 text-sm text-muted">
          Matched by the school name on each student&apos;s profile — a spelling mismatch means
          a student may not show up here yet.
        </p>
        {error && <p className="mt-3 text-sm text-danger">{error}</p>}

        <div className="mt-6 space-y-2">
          {students === null && <p className="text-sm text-muted">Loading...</p>}
          {students?.length === 0 && !error && (
            <p className="text-sm text-muted">No students matched to your school yet.</p>
          )}
          {students?.map((s) => (
            <Card key={s.user_id} className="py-3">
              <p className="text-sm font-medium text-ink">{s.full_name}</p>
              <p className="text-xs text-muted">
                {s.class_level ? `Class ${s.class_level} · ` : ""}
                {[s.district, s.state].filter(Boolean).join(", ")}
              </p>
              <p className="text-xs text-muted">{s.email ?? s.mobile_number}</p>
            </Card>
          ))}
        </div>
      </main>
    </>
  );
}
