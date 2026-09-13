"use client";

import { useEffect, useState } from "react";
import { api, type AdminDashboardSection, type RoleDashboardSection } from "@/lib/api";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

const ROLES = ["student", "parent", "mentor", "school_admin", "admin"];

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
        sees it.
      </p>

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
