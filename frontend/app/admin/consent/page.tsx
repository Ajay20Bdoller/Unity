"use client";

import { useEffect, useState } from "react";
import { api, type AdminGuardianRelationship } from "@/lib/api";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

const CONSENT_TYPES: { value: "mentorship" | "data_sharing"; label: string }[] = [
  { value: "mentorship", label: "Mentorship" },
  { value: "data_sharing", label: "Data sharing" },
];

export default function AdminConsentPage() {
  const [relationships, setRelationships] = useState<AdminGuardianRelationship[]>([]);
  const [busyKey, setBusyKey] = useState<string | null>(null);

  function load() {
    api.adminGuardianRelationships().then(setRelationships).catch(() => setRelationships([]));
  }

  useEffect(load, []);

  async function grant(relationshipId: string, consentType: "mentorship" | "data_sharing") {
    const key = `${relationshipId}:${consentType}`;
    setBusyKey(key);
    try {
      await api.adminGrantConsent(relationshipId, consentType);
      load();
    } finally {
      setBusyKey(null);
    }
  }

  function statusFor(rel: AdminGuardianRelationship, type: string) {
    return rel.consents.find((c) => c.consent_type === type)?.status ?? "not requested";
  }

  return (
    <div>
      <h1 className="font-display text-xl font-medium text-ink">Guardian consent</h1>
      <p className="mt-1 text-sm text-muted">
        Grant a consent directly without the OTP flow — only for a relationship you&apos;ve
        personally verified some other way (phone call, in person). The guardian link itself
        still has to be verified by the parent&apos;s own account first.
      </p>

      <div className="mt-4 space-y-2">
        {relationships.length === 0 && (
          <p className="text-sm text-muted">No guardian relationships yet.</p>
        )}
        {relationships.map((rel) => (
          <Card key={rel.id} className="py-3">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-ink">
                  {rel.student_name} &harr; {rel.parent_name}
                </p>
                <p className="text-xs text-muted">
                  {rel.parent_contact} · relationship: {rel.status}
                </p>
              </div>
            </div>
            {rel.status === "verified" ? (
              <div className="mt-3 flex flex-wrap gap-2">
                {CONSENT_TYPES.map((c) => {
                  const status = statusFor(rel, c.value);
                  const key = `${rel.id}:${c.value}`;
                  return (
                    <div
                      key={c.value}
                      className="flex items-center gap-2 rounded-md border border-border px-2 py-1"
                    >
                      <span className="text-xs text-muted">
                        {c.label}: {status}
                      </span>
                      {status !== "granted" && (
                        <Button
                          variant="secondary"
                          disabled={busyKey === key}
                          onClick={() => grant(rel.id, c.value)}
                        >
                          Grant
                        </Button>
                      )}
                    </div>
                  );
                })}
              </div>
            ) : (
              <p className="mt-2 text-xs text-muted">
                Waiting on the parent to verify the relationship first.
              </p>
            )}
          </Card>
        ))}
      </div>
    </div>
  );
}
