"use client";

import { useEffect, useState } from "react";
import { api, type Announcement } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { Card } from "@/components/ui/card";
import { SiteNav } from "@/components/site-nav";

export default function AnnouncementsPage() {
  const { user, loading } = useAuth();
  const [announcements, setAnnouncements] = useState<Announcement[] | null>(null);

  useEffect(() => {
    if (user) {
      api.myAnnouncements().then(setAnnouncements).catch(() => setAnnouncements([]));
    }
  }, [user]);

  if (loading) return null;
  if (!user) {
    return (
      <>
        <SiteNav />
        <main className="mx-auto max-w-2xl px-6 py-10">
          <p className="text-sm text-muted">Log in to see announcements.</p>
        </main>
      </>
    );
  }

  return (
    <>
      <SiteNav />
      <main className="mx-auto max-w-2xl px-6 py-10">
        <h1 className="font-display text-2xl font-medium text-ink">Announcements</h1>

        <div className="mt-6 space-y-4">
          {announcements === null && <p className="text-sm text-muted">Loading...</p>}
          {announcements?.length === 0 && (
            <p className="text-sm text-muted">No announcements right now.</p>
          )}
          {announcements?.map((a) => (
            <Card key={a.id}>
              <h2 className="font-medium text-ink">{a.title}</h2>
              <p className="mt-2 text-sm text-muted">{a.content}</p>
              {a.published_at && (
                <p className="mt-3 text-xs text-muted">
                  {new Date(a.published_at).toLocaleDateString()}
                </p>
              )}
            </Card>
          ))}
        </div>
      </main>
    </>
  );
}
