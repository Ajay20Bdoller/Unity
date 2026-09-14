"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  api,
  ApiError,
  type MentorPublicProfile,
  type MentorshipRequest,
} from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { SiteNav } from "@/components/site-nav";

export default function StudentMentorshipPage() {
  const { user, loading } = useAuth();
  const [mentors, setMentors] = useState<MentorPublicProfile[]>([]);
  const [myRequests, setMyRequests] = useState<MentorshipRequest[]>([]);
  const [messageDrafts, setMessageDrafts] = useState<Record<string, string>>({});
  const [error, setError] = useState<string | null>(null);
  const [sendingTo, setSendingTo] = useState<string | null>(null);

  function loadRequests() {
    api.myMentorshipRequests().then(setMyRequests).catch(() => setMyRequests([]));
  }

  useEffect(() => {
    if (user?.role !== "student") return;
    api.mentors().then(setMentors).catch(() => setMentors([]));
    loadRequests();
  }, [user]);

  async function sendRequest(mentorId: string) {
    const message = messageDrafts[mentorId]?.trim();
    if (!message) return;
    setSendingTo(mentorId);
    setError(null);
    try {
      await api.requestMentorship(mentorId, message);
      setMessageDrafts((prev) => ({ ...prev, [mentorId]: "" }));
      loadRequests();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong.");
    } finally {
      setSendingTo(null);
    }
  }

  const requestedMentorIds = new Set(myRequests.map((r) => r.mentor_id));

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
      <main className="mx-auto max-w-3xl px-6 py-10">
        <h1 className="font-display text-2xl font-medium text-ink">Mentorship</h1>
        <p className="mt-1 text-sm text-muted">
          Requesting a mentor requires your parent/guardian to grant mentorship consent first.{" "}
          <Link href="/student/guardians" className="text-primary hover:underline">
            Invite your parent →
          </Link>
        </p>
        {error && <p className="mt-3 text-sm text-danger">{error}</p>}

        {myRequests.length > 0 && (
          <div className="mt-6">
            <h2 className="font-medium text-ink">Your requests</h2>
            <div className="mt-2 space-y-2">
              {myRequests.map((req) => (
                <Card key={req.id}>
                  <div className="flex items-center justify-between">
                    <p className="text-sm text-muted">{req.message}</p>
                    <span className="text-xs uppercase text-muted">{req.status}</span>
                  </div>
                </Card>
              ))}
            </div>
          </div>
        )}

        <div className="mt-6">
          <h2 className="font-medium text-ink">Available mentors</h2>
          <div className="mt-2 space-y-3">
            {mentors.length === 0 && <p className="text-sm text-muted">No mentors available yet.</p>}
            {mentors.map((mentor) => (
              <Card key={mentor.user_id}>
                <p className="font-medium text-ink">{mentor.full_name}</p>
                {mentor.bio && <p className="mt-1 text-sm text-muted">{mentor.bio}</p>}
                {mentor.availability_note && (
                  <p className="mt-1 text-xs text-muted">Availability: {mentor.availability_note}</p>
                )}
                {mentor.expertise.length > 0 && (
                  <p className="mt-1 text-xs text-muted">Expertise: {mentor.expertise.join(", ")}</p>
                )}

                {requestedMentorIds.has(mentor.user_id) ? (
                  <p className="mt-3 text-xs text-primary">Request already sent</p>
                ) : (
                  <div className="mt-3 flex gap-2">
                    <Input
                      value={messageDrafts[mentor.user_id] ?? ""}
                      onChange={(e) =>
                        setMessageDrafts((prev) => ({ ...prev, [mentor.user_id]: e.target.value }))
                      }
                      placeholder="Why would you like this mentor's guidance?"
                    />
                    <Button
                      disabled={sendingTo === mentor.user_id || !messageDrafts[mentor.user_id]?.trim()}
                      onClick={() => sendRequest(mentor.user_id)}
                    >
                      Request
                    </Button>
                  </div>
                )}
              </Card>
            ))}
          </div>
        </div>
      </main>
    </>
  );
}
