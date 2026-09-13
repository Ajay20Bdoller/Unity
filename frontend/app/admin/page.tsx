"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api, type AdminActivityStats } from "@/lib/api";
import { Card } from "@/components/ui/card";

function StatCard({ label, value }: { label: string; value: number }) {
  return (
    <Card className="py-4">
      <p className="text-2xl font-semibold text-ink">{value}</p>
      <p className="mt-1 text-xs text-muted">{label}</p>
    </Card>
  );
}

export default function AdminHomePage() {
  const [stats, setStats] = useState<AdminActivityStats | null>(null);

  useEffect(() => {
    api.adminActivityStats().then(setStats).catch(() => setStats(null));
  }, []);

  if (!stats) {
    return (
      <div>
        <h1 className="font-display text-2xl font-medium text-ink">Admin</h1>
        <p className="mt-1 text-sm text-muted">Loading activity...</p>
      </div>
    );
  }

  return (
    <div>
      <h1 className="font-display text-2xl font-medium text-ink">Admin overview</h1>
      <p className="mt-1 text-sm text-muted">Platform activity at a glance.</p>

      <div className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
        <StatCard label="Total users" value={stats.total_users} />
        <StatCard label="Careers" value={stats.total_careers} />
        <StatCard label="Courses" value={stats.total_courses} />
        <StatCard label="Enrollments" value={stats.total_enrollments} />
        <StatCard label="Career interests" value={stats.total_career_interests} />
        <StatCard label="Mentorship requests" value={stats.total_mentorship_requests} />
        <StatCard label="Campaigns" value={stats.total_campaigns} />
        <StatCard label="Campaign registrations" value={stats.total_campaign_registrations} />
      </div>

      <div className="mt-6 grid gap-4 sm:grid-cols-2">
        <Card>
          <h2 className="font-medium text-ink">Users by role</h2>
          <div className="mt-3 space-y-2">
            {Object.entries(stats.users_by_role).map(([role, count]) => (
              <div key={role} className="flex items-center justify-between text-sm">
                <span className="text-muted">{role}</span>
                <span className="font-medium text-ink">{count}</span>
              </div>
            ))}
          </div>
        </Card>

        <Card>
          <h2 className="font-medium text-ink">Mentorship requests by status</h2>
          <div className="mt-3 space-y-2">
            {Object.keys(stats.mentorship_requests_by_status).length === 0 && (
              <p className="text-sm text-muted">No requests yet.</p>
            )}
            {Object.entries(stats.mentorship_requests_by_status).map(([status, count]) => (
              <div key={status} className="flex items-center justify-between text-sm">
                <span className="text-muted">{status}</span>
                <span className="font-medium text-ink">{count}</span>
              </div>
            ))}
          </div>
        </Card>
      </div>

      <Card className="mt-4">
        <div className="flex items-center justify-between">
          <h2 className="font-medium text-ink">Recent registrations</h2>
          <Link href="/admin/users" className="text-xs text-primary hover:underline">
            View all users
          </Link>
        </div>
        <div className="mt-3 space-y-2">
          {stats.recent_users.map((u) => (
            <div key={u.id} className="flex items-center justify-between text-sm">
              <span className="text-ink">{u.full_name}</span>
              <span className="text-xs text-muted">
                {u.role} · {new Date(u.created_at).toLocaleDateString()}
              </span>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
