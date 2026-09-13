"use client";

import { useEffect, useState } from "react";
import { api, type AdminUser } from "@/lib/api";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export default function AdminUsersPage() {
  const [users, setUsers] = useState<AdminUser[]>([]);

  function load() {
    api.adminUsers().then(setUsers).catch(() => setUsers([]));
  }

  useEffect(load, []);

  async function toggle(user: AdminUser) {
    await api.adminSetUserActive(user.id, !user.is_active);
    load();
  }

  return (
    <div>
      <h1 className="font-display text-xl font-medium text-ink">Users</h1>
      <div className="mt-4 space-y-2">
        {users.map((u) => (
          <Card key={u.id} className="flex items-center justify-between py-3">
            <div>
              <p className="text-sm font-medium text-ink">{u.full_name}</p>
              <p className="text-xs text-muted">
                {u.email ?? u.mobile_number ?? "no contact info"} · {u.role} ·{" "}
                {u.is_active ? "active" : "inactive"}
              </p>
            </div>
            <Button variant="secondary" onClick={() => toggle(u)}>
              {u.is_active ? "Deactivate" : "Activate"}
            </Button>
          </Card>
        ))}
      </div>
    </div>
  );
}
