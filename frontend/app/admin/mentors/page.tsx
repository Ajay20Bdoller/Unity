"use client";

import { useEffect, useState } from "react";
import { api, type AdminMentor } from "@/lib/api";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export default function AdminMentorsPage() {
  const [mentors, setMentors] = useState<AdminMentor[]>([]);
  const [busyId, setBusyId] = useState<string | null>(null);

  function load() {
    api.adminMentors().then(setMentors).catch(() => setMentors([]));
  }

  useEffect(load, []);

  async function approve(userId: string) {
    setBusyId(userId);
    try {
      await api.adminApproveMentor(userId);
      load();
    } finally {
      setBusyId(null);
    }
  }

  async function unapprove(userId: string) {
    setBusyId(userId);
    try {
      await api.adminUnapproveMentor(userId);
      load();
    } finally {
      setBusyId(null);
    }
  }

  const pending = mentors.filter((m) => !m.is_approved);
  const approved = mentors.filter((m) => m.is_approved);

  return (
    <div>
      <h1 className="font-display text-xl font-medium text-ink">Mentors</h1>
      <p className="mt-1 text-sm text-muted">
        A mentor is invisible to students and can&apos;t receive requests until approved here.
      </p>

      <div className="mt-4">
        <h2 className="font-medium text-ink">
          Pending approval {pending.length > 0 && `(${pending.length})`}
        </h2>
        <div className="mt-2 space-y-2">
          {pending.length === 0 && <p className="text-sm text-muted">Nothing pending.</p>}
          {pending.map((m) => (
            <Card key={m.user_id} className="flex items-center justify-between py-3">
              <div>
                <p className="text-sm font-medium text-ink">{m.full_name}</p>
                <p className="text-xs text-muted">{m.email ?? m.mobile_number}</p>
                {m.bio && <p className="mt-1 text-xs text-muted">{m.bio}</p>}
              </div>
              <Button disabled={busyId === m.user_id} onClick={() => approve(m.user_id)}>
                Approve
              </Button>
            </Card>
          ))}
        </div>
      </div>

      <div className="mt-6">
        <h2 className="font-medium text-ink">Approved</h2>
        <div className="mt-2 space-y-2">
          {approved.length === 0 && <p className="text-sm text-muted">None yet.</p>}
          {approved.map((m) => (
            <Card key={m.user_id} className="flex items-center justify-between py-3">
              <div>
                <p className="text-sm font-medium text-ink">{m.full_name}</p>
                <p className="text-xs text-muted">{m.email ?? m.mobile_number}</p>
              </div>
              <Button
                variant="secondary"
                disabled={busyId === m.user_id}
                onClick={() => unapprove(m.user_id)}
              >
                Revoke
              </Button>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}
