"use client";

import { useEffect, useState } from "react";
import { api, type MentorshipRequest } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { SiteNav } from "@/components/site-nav";

export default function MentorRequestsPage() {
  const { user, loading } = useAuth();
  const [requests, setRequests] = useState<MentorshipRequest[]>([]);
  const [sessionNotes, setSessionNotes] = useState<Record<string, string>>({});
  const [sessionCreated, setSessionCreated] = useState<Record<string, boolean>>({});
  const [busyId, setBusyId] = useState<string | null>(null);

  function load() {
    api.incomingMentorshipRequests().then(setRequests).catch(() => setRequests([]));
  }

  useEffect(() => {
    if (user?.role === "mentor") load();
  }, [user]);

  async function accept(id: string) {
    setBusyId(id);
    try {
      await api.acceptMentorshipRequest(id);
      load();
    } finally {
      setBusyId(null);
    }
  }

  async function decline(id: string) {
    setBusyId(id);
    try {
      await api.declineMentorshipRequest(id);
      load();
    } finally {
      setBusyId(null);
    }
  }

  async function scheduleSession(id: string) {
    setBusyId(id);
    try {
      await api.createMentorshipSession(id, sessionNotes[id]);
      setSessionCreated((prev) => ({ ...prev, [id]: true }));
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
        <h1 className="text-2xl font-semibold text-ink">Mentorship requests</h1>

        <div className="mt-6 space-y-4">
          {requests.length === 0 && <p className="text-sm text-muted">No requests yet.</p>}
          {requests.map((req) => (
            <Card key={req.id}>
              <div className="flex items-center justify-between">
                <p className="text-sm text-ink">{req.message}</p>
                <span className="text-xs uppercase text-muted">{req.status}</span>
              </div>

              {req.status === "pending" && (
                <div className="mt-3 flex gap-2">
                  <Button disabled={busyId === req.id} onClick={() => accept(req.id)}>
                    Accept
                  </Button>
                  <Button
                    variant="secondary"
                    disabled={busyId === req.id}
                    onClick={() => decline(req.id)}
                  >
                    Decline
                  </Button>
                </div>
              )}

              {req.status === "accepted" && !sessionCreated[req.id] && (
                <div className="mt-3 flex gap-2">
                  <Input
                    value={sessionNotes[req.id] ?? ""}
                    onChange={(e) =>
                      setSessionNotes((prev) => ({ ...prev, [req.id]: e.target.value }))
                    }
                    placeholder="Session notes (e.g. intro call scheduled)"
                  />
                  <Button disabled={busyId === req.id} onClick={() => scheduleSession(req.id)}>
                    Log session
                  </Button>
                </div>
              )}

              {sessionCreated[req.id] && (
                <p className="mt-3 text-xs text-primary">Session logged.</p>
              )}
            </Card>
          ))}
        </div>
      </main>
    </>
  );
}
