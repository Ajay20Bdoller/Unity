"use client";

import { useEffect, useState } from "react";
import { api, ApiError, type TeamMember } from "@/lib/api";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

const emptyForm = {
  full_name: "",
  role_title: "",
  bio: "",
  photo_url: "",
  linkedin_url: "",
};

export default function AdminTeamPage() {
  const [members, setMembers] = useState<TeamMember[]>([]);
  const [form, setForm] = useState(emptyForm);
  const [error, setError] = useState<string | null>(null);
  const [editingId, setEditingId] = useState<string | null>(null);

  function load() {
    api.adminTeam().then(setMembers).catch(() => setMembers([]));
  }
  useEffect(load, []);

  function startEdit(m: TeamMember) {
    setEditingId(m.id);
    setForm({
      full_name: m.full_name,
      role_title: m.role_title,
      bio: m.bio ?? "",
      photo_url: m.photo_url ?? "",
      linkedin_url: m.linkedin_url ?? "",
    });
  }

  function cancelEdit() {
    setEditingId(null);
    setForm(emptyForm);
  }

  async function save() {
    setError(null);
    try {
      if (editingId) {
        await api.adminUpdateTeamMember(editingId, form);
      } else {
        await api.adminCreateTeamMember({ ...form, display_order: members.length });
      }
      cancelEdit();
      load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong.");
    }
  }

  async function remove(id: string) {
    await api.adminDeleteTeamMember(id);
    load();
  }

  return (
    <div>
      <h1 className="font-display text-xl font-medium text-ink">About Us — Team</h1>
      <p className="mt-1 text-sm text-muted">
        Profiles shown on the public /about page, in this order. The first one gets the
        featured, larger layout.
      </p>

      <Card className="mt-4">
        <h2 className="font-medium text-ink">{editingId ? "Edit profile" : "Add a profile"}</h2>
        <div className="mt-2 space-y-2">
          <div className="grid grid-cols-2 gap-2">
            <Input
              value={form.full_name}
              onChange={(e) => setForm({ ...form, full_name: e.target.value })}
              placeholder="Full name"
            />
            <Input
              value={form.role_title}
              onChange={(e) => setForm({ ...form, role_title: e.target.value })}
              placeholder="Role (e.g. Founder & CTO)"
            />
          </div>
          <textarea
            value={form.bio}
            onChange={(e) => setForm({ ...form, bio: e.target.value })}
            placeholder="Bio"
            rows={3}
            className="w-full rounded-md border border-border bg-surface px-3 py-2 text-sm text-ink"
          />
          <Input
            value={form.photo_url}
            onChange={(e) => setForm({ ...form, photo_url: e.target.value })}
            placeholder="Photo URL (optional)"
          />
          <Input
            value={form.linkedin_url}
            onChange={(e) => setForm({ ...form, linkedin_url: e.target.value })}
            placeholder="LinkedIn URL (optional)"
          />
          {error && <p className="text-sm text-danger">{error}</p>}
          <div className="flex gap-2">
            <Button disabled={!form.full_name || !form.role_title} onClick={save}>
              {editingId ? "Save changes" : "Add profile"}
            </Button>
            {editingId && (
              <Button variant="secondary" onClick={cancelEdit}>
                Cancel
              </Button>
            )}
          </div>
        </div>
      </Card>

      <div className="mt-6 space-y-2">
        {members.map((m) => (
          <Card key={m.id} className="flex items-center justify-between py-3">
            <div>
              <p className="text-sm font-medium text-ink">{m.full_name}</p>
              <p className="text-xs text-muted">{m.role_title}</p>
            </div>
            <div className="flex gap-2">
              <Button variant="secondary" onClick={() => startEdit(m)}>
                Edit
              </Button>
              <Button variant="secondary" onClick={() => remove(m.id)}>
                Delete
              </Button>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
