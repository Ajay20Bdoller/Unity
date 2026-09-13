"use client";

import { useEffect, useState } from "react";
import {
  api,
  ApiError,
  type ConsentType,
  type GuardianRelationship,
} from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { SiteNav } from "@/components/site-nav";

const CONSENT_TYPES: { value: ConsentType; label: string }[] = [
  { value: "mentorship", label: "Mentorship" },
  { value: "data_sharing", label: "Data sharing" },
];

function ConsentControl({ relationshipId, type }: { relationshipId: string; type: ConsentType }) {
  const [devOtp, setDevOtp] = useState<string | null>(null);
  const [otpInput, setOtpInput] = useState("");
  const [status, setStatus] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function requestOtp() {
    setBusy(true);
    setStatus(null);
    try {
      const res = await api.requestConsentOtp(relationshipId, type);
      setDevOtp(res.dev_otp);
      setStatus(res.message);
    } catch (err) {
      setStatus(err instanceof ApiError ? err.message : "Something went wrong.");
    } finally {
      setBusy(false);
    }
  }

  async function verifyOtp() {
    setBusy(true);
    setStatus(null);
    try {
      await api.verifyConsentOtp(relationshipId, type, otpInput);
      setStatus("Consent granted.");
      setDevOtp(null);
      setOtpInput("");
    } catch (err) {
      setStatus(err instanceof ApiError ? err.message : "Something went wrong.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="mt-2 rounded-md border border-border p-3">
      <p className="text-sm font-medium text-ink">
        {CONSENT_TYPES.find((c) => c.value === type)?.label}
      </p>
      {!devOtp && !status?.includes("granted") && (
        <Button variant="secondary" className="mt-2" disabled={busy} onClick={requestOtp}>
          Request consent code
        </Button>
      )}
      {devOtp && (
        <div className="mt-2 flex items-center gap-2">
          <p className="text-xs text-muted">
            Dev-mode code (no SMS yet): <span className="font-mono">{devOtp}</span>
          </p>
        </div>
      )}
      {devOtp && (
        <div className="mt-2 flex gap-2">
          <Input
            value={otpInput}
            onChange={(e) => setOtpInput(e.target.value)}
            placeholder="Enter code"
            className="max-w-[140px]"
          />
          <Button disabled={busy || !otpInput} onClick={verifyOtp}>
            Verify
          </Button>
        </div>
      )}
      {status && <p className="mt-2 text-xs text-muted">{status}</p>}
    </div>
  );
}

export default function ParentStudentsPage() {
  const { user, loading } = useAuth();
  const [relationships, setRelationships] = useState<GuardianRelationship[]>([]);

  function load() {
    api.parentGuardianRelationships().then(setRelationships).catch(() => setRelationships([]));
  }

  useEffect(() => {
    if (user?.role === "parent") load();
  }, [user]);

  async function verify(id: string) {
    await api.verifyGuardianRelationship(id);
    load();
  }

  async function reject(id: string) {
    await api.rejectGuardianRelationship(id);
    load();
  }

  if (loading) return null;
  if (!user || user.role !== "parent") {
    return (
      <>
        <SiteNav />
        <main className="mx-auto max-w-2xl px-6 py-10">
          <p className="text-sm text-muted">This page is available to parents only.</p>
        </main>
      </>
    );
  }

  return (
    <>
      <SiteNav />
      <main className="mx-auto max-w-2xl px-6 py-10">
        <h1 className="font-display text-2xl font-medium text-ink">My students</h1>
        <p className="mt-1 text-sm text-muted">
          Students who have linked you as their guardian. Verify a link to confirm it&apos;s
          really your child, then grant consent for specific features when you&apos;re ready.
        </p>

        <div className="mt-6 space-y-4">
          {relationships.length === 0 && (
            <p className="text-sm text-muted">No students have linked you yet.</p>
          )}
          {relationships.map((rel) => (
            <Card key={rel.id}>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-ink">
                    {rel.student_name ?? "A student"}
                  </p>
                  {rel.student_email && <p className="text-xs text-muted">{rel.student_email}</p>}
                </div>
                <span className="text-xs uppercase text-muted">{rel.status}</span>
              </div>

              {rel.status === "pending" && (
                <div className="mt-3 flex gap-2">
                  <Button onClick={() => verify(rel.id)}>Verify — this is my child</Button>
                  <Button variant="secondary" onClick={() => reject(rel.id)}>
                    Reject
                  </Button>
                </div>
              )}

              {rel.status === "verified" && (
                <div className="mt-3 space-y-2">
                  {CONSENT_TYPES.map((c) => (
                    <ConsentControl key={c.value} relationshipId={rel.id} type={c.value} />
                  ))}
                </div>
              )}
            </Card>
          ))}
        </div>
      </main>
    </>
  );
}
