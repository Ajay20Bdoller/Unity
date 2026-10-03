"use client";

import { useEffect, useState } from "react";
import {
  api,
  ApiError,
  type AdminDashboardSection,
  type DashboardMessage,
  type RoleDashboardSection,
} from "@/lib/api";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

const ROLES = ["student", "parent", "mentor", "school_admin", "admin"];

function MotivationalQuotesManager() {
  const [messages, setMessages] = useState<DashboardMessage[]>([]);
  const [text, setText] = useState("");
  const [attribution, setAttribution] = useState("");
  const [error, setError] = useState<string | null>(null);

  function load() {
    api.adminDashboardMessages().then(setMessages).catch(() => setMessages([]));
  }
  useEffect(load, []);

  async function add() {
    setError(null);
    try {
      await api.adminCreateDashboardMessage({
        message: text,
        attribution: attribution || undefined,
        display_order: messages.length,
      });
      setText("");
      setAttribution("");
      load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong.");
    }
  }

  async function toggleActive(m: DashboardMessage) {
    await api.adminUpdateDashboardMessage(m.id, { active: !m.active });
    load();
  }

  async function remove(id: string) {
    await api.adminDeleteDashboardMessage(id);
    load();
  }

  return (
    <Card className="mt-4">
      <p className="font-medium text-ink">Motivational Quotes</p>
      <p className="mt-1 text-xs text-muted">
        The actual content shown in the &quot;Motivational Quotes&quot; box below (on by default
        for every role) — write, retire, or remove messages here. Only active ones show.
      </p>
      <div className="mt-3 space-y-2">
        <Input value={text} onChange={(e) => setText(e.target.value)} placeholder="Quote / message" />
        <Input
          value={attribution}
          onChange={(e) => setAttribution(e.target.value)}
          placeholder="Attribution (optional)"
        />
        {error && <p className="text-sm text-danger">{error}</p>}
        <Button disabled={!text} onClick={add}>
          Add
        </Button>
      </div>
      <div className="mt-4 space-y-2">
        {messages.map((m) => (
          <div
            key={m.id}
            className="flex items-center justify-between rounded-md border border-border p-2"
          >
            <div>
              <p className={`text-sm ${m.active ? "text-ink" : "text-muted line-through"}`}>
                {m.message}
              </p>
              {m.attribution && <p className="text-xs text-muted">— {m.attribution}</p>}
            </div>
            <div className="flex shrink-0 gap-2">
              <Button variant="secondary" onClick={() => toggleActive(m)}>
                {m.active ? "Deactivate" : "Activate"}
              </Button>
              <Button variant="secondary" onClick={() => remove(m.id)}>
                Delete
              </Button>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}

export default function AdminDashboardSectionsPage() {
  const [sections, setSections] = useState<AdminDashboardSection[]>([]);
  const [roleConfigs, setRoleConfigs] = useState<Record<string, RoleDashboardSection[]>>({});

  function load() {
    api.adminDashboardSections().then((secs) => {
      setSections(secs);
      secs.forEach((s) => {
        api.adminSectionRoles(s.id).then((roles) =>
          setRoleConfigs((prev) => ({ ...prev, [s.id]: roles }))
        );
      });
    });
  }

  useEffect(load, []);

  async function setRole(sectionId: string, role: string, enabled: boolean, order: number) {
    await api.adminUpsertSectionRole(sectionId, role, { enabled, display_order: order });
    api.adminSectionRoles(sectionId).then((roles) =>
      setRoleConfigs((prev) => ({ ...prev, [sectionId]: roles }))
    );
  }

  return (
    <div>
      <h1 className="font-display text-xl font-medium text-ink">Dashboard sections</h1>
      <p className="mt-1 text-sm text-muted">
        Enable/disable and order each section per role. A role with no row for a section never
        sees it. Each row below is a fixed widget type — this is where you control whether it
        shows, to whom, and in what order; the Motivational Quotes box is the one exception where
        you also manage its actual text content, directly below.
      </p>

      <MotivationalQuotesManager />

      <div className="mt-4 space-y-4">
        {sections.map((section) => {
          const roles = roleConfigs[section.id] ?? [];
          return (
            <Card key={section.id}>
              <p className="font-medium text-ink">{section.name}</p>
              <p className="text-xs text-muted">{section.component_key}</p>
              <div className="mt-3 grid grid-cols-5 gap-2">
                {ROLES.map((role) => {
                  const existing = roles.find((r) => r.role === role);
                  return (
                    <div key={role} className="rounded-md border border-border p-2 text-center">
                      <p className="text-xs text-muted">{role}</p>
                      <Button
                        variant="secondary"
                        className="mt-1 w-full text-xs"
                        onClick={() =>
                          setRole(
                            section.id,
                            role,
                            !(existing?.enabled ?? false),
                            existing?.display_order ?? 0
                          )
                        }
                      >
                        {existing?.enabled ? "On" : "Off"}
                      </Button>
                      <Input
                        type="number"
                        className="mt-1 text-xs"
                        defaultValue={existing?.display_order ?? 0}
                        onBlur={(e) =>
                          setRole(
                            section.id,
                            role,
                            existing?.enabled ?? false,
                            Number(e.target.value)
                          )
                        }
                      />
                    </div>
                  );
                })}
              </div>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
