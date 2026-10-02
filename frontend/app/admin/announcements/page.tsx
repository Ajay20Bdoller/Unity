"use client";

import { useEffect, useState } from "react";
import { api, ApiError, type AdminAnnouncement } from "@/lib/api";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

const ROLES = ["student", "parent", "mentor", "school_admin", "admin"];

function AudiencePicker({
  audience,
  onToggle,
}: {
  audience: string[];
  onToggle: (role: string) => void;
}) {
  return (
    <div className="flex flex-wrap gap-2">
      <span className="text-xs text-muted">Audience (none = everyone):</span>
      {ROLES.map((role) => (
        <button
          key={role}
          type="button"
          onClick={() => onToggle(role)}
          className={`rounded-full border px-2 py-1 text-xs ${
            audience.includes(role)
              ? "border-primary bg-primary/10 text-primary"
              : "border-border text-ink"
          }`}
        >
          {role}
        </button>
      ))}
    </div>
  );
}

function EditAnnouncementForm({
  announcement,
  onDone,
}: {
  announcement: AdminAnnouncement;
  onDone: () => void;
}) {
  const [title, setTitle] = useState(announcement.title);
  const [content, setContent] = useState(announcement.content);
  const [audience, setAudience] = useState<string[]>(announcement.audience ?? []);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  function toggle(role: string) {
    setAudience((prev) => (prev.includes(role) ? prev.filter((r) => r !== role) : [...prev, role]));
  }

  async function save() {
    setError(null);
    setSaving(true);
    try {
      await api.adminUpdateAnnouncement(announcement.id, {
        title,
        content,
        audience: audience.length > 0 ? audience : undefined,
      });
      onDone();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="mt-3 space-y-2 border-t border-border pt-3">
      <Input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Title" />
      <textarea
        value={content}
        onChange={(e) => setContent(e.target.value)}
        placeholder="Content"
        rows={3}
        className="w-full rounded-md border border-border bg-surface px-3 py-2 text-sm text-ink"
      />
      <AudiencePicker audience={audience} onToggle={toggle} />
      {error && <p className="text-sm text-danger">{error}</p>}
      <div className="flex gap-2">
        <Button disabled={saving || !title || !content} onClick={save}>
          {saving ? "Saving…" : "Save changes"}
        </Button>
        <Button variant="secondary" onClick={onDone}>
          Cancel
        </Button>
      </div>
    </div>
  );
}

export default function AdminAnnouncementsPage() {
  const [announcements, setAnnouncements] = useState<AdminAnnouncement[]>([]);
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [audience, setAudience] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [editingId, setEditingId] = useState<string | null>(null);

  function load() {
    api.adminAnnouncements().then(setAnnouncements).catch(() => setAnnouncements([]));
  }

  useEffect(load, []);

  function toggleAudience(role: string) {
    setAudience((prev) => (prev.includes(role) ? prev.filter((r) => r !== role) : [...prev, role]));
  }

  async function create() {
    setError(null);
    try {
      await api.adminCreateAnnouncement({
        title,
        content,
        audience: audience.length > 0 ? audience : undefined,
      });
      setTitle("");
      setContent("");
      setAudience([]);
      load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong.");
    }
  }

  async function publish(id: string) {
    await api.adminPublishAnnouncement(id);
    load();
  }

  return (
    <div>
      <h1 className="font-display text-xl font-medium text-ink">Announcements</h1>
      {error && <p className="mt-2 text-sm text-danger">{error}</p>}

      <Card className="mt-4">
        <h2 className="font-medium text-ink">New announcement</h2>
        <div className="mt-2 space-y-2">
          <Input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Title" />
          <Input value={content} onChange={(e) => setContent(e.target.value)} placeholder="Content" />
          <AudiencePicker audience={audience} onToggle={toggleAudience} />
          <Button disabled={!title || !content} onClick={create}>
            Save as draft
          </Button>
        </div>
      </Card>

      <div className="mt-6 space-y-2">
        {announcements.map((a) => (
          <Card key={a.id} className="py-3">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-ink">{a.title}</p>
                <p className="text-xs text-muted">
                  {a.publish_status} · audience: {a.audience?.join(", ") ?? "everyone"}
                </p>
              </div>
              <div className="flex gap-2">
                <Button
                  variant="secondary"
                  onClick={() => setEditingId(editingId === a.id ? null : a.id)}
                >
                  {editingId === a.id ? "Close" : "Manage"}
                </Button>
                {a.publish_status === "draft" && (
                  <Button variant="secondary" onClick={() => publish(a.id)}>
                    Publish
                  </Button>
                )}
              </div>
            </div>
            {editingId === a.id && (
              <EditAnnouncementForm
                announcement={a}
                onDone={() => {
                  setEditingId(null);
                  load();
                }}
              />
            )}
          </Card>
        ))}
      </div>
    </div>
  );
}
