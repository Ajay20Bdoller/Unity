"use client";

import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import { Card } from "@/components/ui/card";
import { SiteNav } from "@/components/site-nav";

export default function SchoolHomePage() {
  const { user, loading } = useAuth();

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
        <h1 className="font-display text-2xl font-medium text-ink">Welcome, {user.full_name}</h1>
        <div className="mt-6 grid gap-4 sm:grid-cols-2">
          <Link href="/school/students">
            <Card className="h-full hover:shadow-sm">
              <h2 className="font-medium text-ink">Students</h2>
              <p className="mt-1 text-sm text-muted">See students registered at your school.</p>
            </Card>
          </Link>
          <Link href="/announcements">
            <Card className="h-full hover:shadow-sm">
              <h2 className="font-medium text-ink">Announcements</h2>
              <p className="mt-1 text-sm text-muted">Platform updates relevant to you.</p>
            </Card>
          </Link>
        </div>
      </main>
    </>
  );
}
