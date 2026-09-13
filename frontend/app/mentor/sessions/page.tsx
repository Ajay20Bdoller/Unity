"use client";

import { useEffect, useState } from "react";
import { api, type MentorshipSessionWithContext } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { SiteNav } from "@/components/site-nav";

export default function MentorSessionsPage() {
  const { user, loading } = useAuth();
  const [sessions, setSessions] = useState<MentorshipSessionWithContext[]>([]);
  const [busyId, setBusyId] = useState<string | null>(null);

  function load() {
    api.myMentorSessions().then(setSessions).catch(() => setSessions([]));
  }

  useEffect(() => {
    if (user?.role === "mentor") load();
  }, [user]);

  async function markComplete(sessionId: string) {
    setBusyId(sessionId);
    try {
      await api.completeMentorshipSession(sessionId);
      load();
    } finally {
      setBusyId(null);
    }
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
        <h1 className="font-display text-2xl font-medium text-ink">Sessions</h1>

        <div className="mt-6 space-y-3">
          {sessions.length === 0 && (
            <p className="text-sm text-muted">
              No sessions yet — log one from an accepted request on the Requests page.
            </p>
          )}
          {sessions.map((s) => (
            <Card key={s.id}>
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="text-sm text-ink">{s.notes ?? "No notes"}</p>
                  <p className="mt-1 text-xs text-muted">Re: {s.request_message}</p>
                  {s.scheduled_at && (
                    <p className="mt-1 text-xs text-muted">
                      Scheduled: {new Date(s.scheduled_at).toLocaleString()}
                    </p>
                  )}
                </div>
                {s.completed ? (
                  <span className="shrink-0 text-xs text-primary">Completed</span>
                ) : (
                  <Button
                    variant="secondary"
                    disabled={busyId === s.id}
                    onClick={() => markComplete(s.id)}
                  >
                    Mark complete
                  </Button>
                )}
              </div>
            </Card>
          ))}
        </div>
      </main>
    </>
  );
}
