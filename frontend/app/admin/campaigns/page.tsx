"use client";

import { useEffect, useState } from "react";
import { api, ApiError, type Campaign, type CampaignRegistration, type CampaignType } from "@/lib/api";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

const TYPES: CampaignType[] = ["school", "coaching", "community", "online", "referral"];

export default function AdminCampaignsPage() {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [key, setKey] = useState("");
  const [name, setName] = useState("");
  const [type, setType] = useState<CampaignType>("school");
  const [error, setError] = useState<string | null>(null);
  const [registrations, setRegistrations] = useState<Record<string, CampaignRegistration[]>>({});

  function load() {
    api.adminCampaigns().then(setCampaigns).catch(() => setCampaigns([]));
  }

  useEffect(load, []);

  async function create() {
    setError(null);
    try {
      await api.adminCreateCampaign({ key, name, campaign_type: type });
      setKey("");
      setName("");
      load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong.");
    }
  }

  async function viewRegistrations(campaignId: string) {
    const regs = await api.adminCampaignRegistrations(campaignId);
    setRegistrations((prev) => ({ ...prev, [campaignId]: regs }));
  }

  return (
    <div>
      <h1 className="font-display text-xl font-medium text-ink">Campaigns</h1>
      {error && <p className="mt-2 text-sm text-danger">{error}</p>}

      <Card className="mt-4">
        <h2 className="font-medium text-ink">New campaign</h2>
        <div className="mt-2 space-y-2">
          <Input value={key} onChange={(e) => setKey(e.target.value)} placeholder="key" />
          <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="Name" />
          <select
            value={type}
            onChange={(e) => setType(e.target.value as CampaignType)}
            className="w-full rounded-md border border-border bg-surface px-3 py-2 text-sm text-ink"
          >
            {TYPES.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
          <Button disabled={!key || !name} onClick={create}>
            Add
          </Button>
        </div>
      </Card>

      <div className="mt-6 space-y-2">
        {campaigns.map((c) => (
          <Card key={c.id} className="py-3">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-ink">{c.name}</p>
                <p className="text-xs text-muted">
                  {c.key} · {c.campaign_type} · {c.active ? "active" : "inactive"}
                </p>
              </div>
              <Button variant="secondary" onClick={() => viewRegistrations(c.id)}>
                View registrations
              </Button>
            </div>
            {registrations[c.id] && (
              <p className="mt-2 text-xs text-muted">
                {registrations[c.id].length} registration(s)
                {registrations[c.id].length > 0 &&
                  ` — sources: ${[...new Set(registrations[c.id].map((r) => r.source ?? "unknown"))].join(", ")}`}
              </p>
            )}
          </Card>
        ))}
      </div>
    </div>
  );
}
