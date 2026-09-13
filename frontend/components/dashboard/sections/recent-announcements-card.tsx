"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api, type Announcement } from "@/lib/api";
import { Card } from "@/components/ui/card";

export function RecentAnnouncementsCard() {
  const [announcements, setAnnouncements] = useState<Announcement[] | null>(null);

  useEffect(() => {
    api.myAnnouncements().then(setAnnouncements).catch(() => setAnnouncements([]));
  }, []);

  if (announcements === null || announcements.length === 0) return null;

  return (
    <Card>
      <div className="flex items-center justify-between">
        <h2 className="font-medium text-ink">Announcements</h2>
        <Link href="/announcements" className="text-xs text-primary hover:underline">
          View all
        </Link>
      </div>
      <div className="mt-3 space-y-2">
        {announcements.slice(0, 3).map((a) => (
          <div key={a.id} className="rounded-md border border-border p-3">
            <p className="text-sm font-medium text-ink">{a.title}</p>
            <p className="mt-1 line-clamp-2 text-xs text-muted">{a.content}</p>
          </div>
        ))}
      </div>
    </Card>
  );
}
