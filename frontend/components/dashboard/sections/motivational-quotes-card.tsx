"use client";

import { useEffect, useState } from "react";
import { api, type DashboardMessage } from "@/lib/api";

export function MotivationalQuotesCard() {
  const [messages, setMessages] = useState<DashboardMessage[] | null>(null);

  useEffect(() => {
    api.dashboardMessages().then(setMessages).catch(() => setMessages([]));
  }, []);

  if (!messages || messages.length === 0) return null;

  // One at a time, picked fresh on each visit -- a stack of every
  // active message would clutter the dashboard more than it'd help.
  const pick = messages[Math.floor(Math.random() * messages.length)];

  return (
    <div className="rounded-3xl border border-accent/30 bg-accent/10 p-6">
      <p className="font-display text-xl leading-snug text-ink">&ldquo;{pick.message}&rdquo;</p>
      {pick.attribution && <p className="mt-3 text-sm text-muted">— {pick.attribution}</p>}
    </div>
  );
}
