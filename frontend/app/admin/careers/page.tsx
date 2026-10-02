"use client";

import { useEffect, useState } from "react";
import {
  api,
  ApiError,
  type CareerCategory,
  type CareerDetail,
  type CareerListItem,
} from "@/lib/api";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

type EditForm = {
  title: string;
  description: string;
  eligibility: string;
  subjects: string; // comma-separated in the form, split into an array on save
  skills: string;
  entrance_exams: string;
  education_pathway: string;
  roadmap: string;
};

function toEditForm(d: CareerDetail): EditForm {
  return {
    title: d.title,
    description: d.description,
    eligibility: d.eligibility ?? "",
    subjects: (d.subjects ?? []).join(", "),
    skills: (d.skills ?? []).join(", "),
    entrance_exams: (d.entrance_exams ?? []).join(", "),
    education_pathway: d.education_pathway ?? "",
    roadmap: d.roadmap ?? "",
  };
}

function splitList(value: string): string[] {
  return value
    .split(",")
    .map((v) => v.trim())
    .filter(Boolean);
}

function EditCareerForm({
  career,
  onDone,
}: {
  career: CareerListItem;
  onDone: () => void;
}) {
  const [form, setForm] = useState<EditForm | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    api.career(career.slug).then((d) => setForm(toEditForm(d))).catch(() => setError("Couldn't load this career's content."));
  }, [career.slug]);

  async function save() {
    if (!form) return;
    setError(null);
    setSaving(true);
    try {
      await api.adminUpdateCareer(career.id, {
        title: form.title,
        description: form.description,
        eligibility: form.eligibility || undefined,
        subjects: splitList(form.subjects),
        skills: splitList(form.skills),
        entrance_exams: splitList(form.entrance_exams),
        education_pathway: form.education_pathway || undefined,
        roadmap: form.roadmap || undefined,
      });
      onDone();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong.");
    } finally {
      setSaving(false);
    }
  }

  if (!form) {
    return (
      <div className="mt-3 border-t border-border pt-3">
        {error ? <p className="text-sm text-danger">{error}</p> : <p className="text-sm text-muted">Loading...</p>}
      </div>
    );
  }

  return (
    <div className="mt-3 space-y-2 border-t border-border pt-3">
      <Input value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} placeholder="Title" />
      <textarea
        value={form.description}
        onChange={(e) => setForm({ ...form, description: e.target.value })}
        placeholder="Description"
        rows={2}
        className="w-full rounded-md border border-border bg-surface px-3 py-2 text-sm text-ink"
      />
      <textarea
        value={form.eligibility}
        onChange={(e) => setForm({ ...form, eligibility: e.target.value })}
        placeholder="Eligibility"
        rows={2}
        className="w-full rounded-md border border-border bg-surface px-3 py-2 text-sm text-ink"
      />
      <Input
        value={form.subjects}
        onChange={(e) => setForm({ ...form, subjects: e.target.value })}
        placeholder="Subjects (comma-separated)"
      />
      <Input
        value={form.skills}
        onChange={(e) => setForm({ ...form, skills: e.target.value })}
        placeholder="Skills (comma-separated)"
      />
      <Input
        value={form.entrance_exams}
        onChange={(e) => setForm({ ...form, entrance_exams: e.target.value })}
        placeholder="Entrance exams (comma-separated)"
      />
      <textarea
        value={form.education_pathway}
        onChange={(e) => setForm({ ...form, education_pathway: e.target.value })}
        placeholder="Education pathway"
        rows={2}
        className="w-full rounded-md border border-border bg-surface px-3 py-2 text-sm text-ink"
      />
      <textarea
        value={form.roadmap}
        onChange={(e) => setForm({ ...form, roadmap: e.target.value })}
        placeholder="Roadmap (explore / build / learn / apply)"
        rows={3}
        className="w-full rounded-md border border-border bg-surface px-3 py-2 text-sm text-ink"
      />
      {error && <p className="text-sm text-danger">{error}</p>}
      <div className="flex gap-2">
        <Button disabled={saving} onClick={save}>
          {saving ? "Saving…" : "Save changes"}
        </Button>
        <Button variant="secondary" onClick={onDone}>
          Cancel
        </Button>
      </div>
    </div>
  );
}

export default function AdminCareersPage() {
  const [categories, setCategories] = useState<CareerCategory[]>([]);
  const [careers, setCareers] = useState<CareerListItem[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [editingId, setEditingId] = useState<string | null>(null);

  const [catKey, setCatKey] = useState("");
  const [catName, setCatName] = useState("");

  const [careerCategoryId, setCareerCategoryId] = useState("");
  const [careerSlug, setCareerSlug] = useState("");
  const [careerTitle, setCareerTitle] = useState("");
  const [careerDescription, setCareerDescription] = useState("");

  function load() {
    api.careerCategories().then(setCategories).catch(() => setCategories([]));
    api.careers().then(setCareers).catch(() => setCareers([]));
  }

  useEffect(load, []);

  async function createCategory() {
    setError(null);
    try {
      await api.adminCreateCareerCategory({ key: catKey, name: catName });
      setCatKey("");
      setCatName("");
      load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong.");
    }
  }

  async function createCareer() {
    setError(null);
    try {
      await api.adminCreateCareer({
        category_id: careerCategoryId,
        slug: careerSlug,
        title: careerTitle,
        description: careerDescription,
      });
      setCareerSlug("");
      setCareerTitle("");
      setCareerDescription("");
      load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong.");
    }
  }

  return (
    <div>
      <h1 className="font-display text-xl font-medium text-ink">Careers</h1>
      {error && <p className="mt-2 text-sm text-danger">{error}</p>}

      <Card className="mt-4">
        <h2 className="font-medium text-ink">New category</h2>
        <div className="mt-2 flex gap-2">
          <Input value={catKey} onChange={(e) => setCatKey(e.target.value)} placeholder="key (e.g. arts)" />
          <Input value={catName} onChange={(e) => setCatName(e.target.value)} placeholder="Display name" />
          <Button disabled={!catKey || !catName} onClick={createCategory}>
            Add
          </Button>
        </div>
      </Card>

      <Card className="mt-4">
        <h2 className="font-medium text-ink">New career</h2>
        <div className="mt-2 space-y-2">
          <select
            value={careerCategoryId}
            onChange={(e) => setCareerCategoryId(e.target.value)}
            className="w-full rounded-md border border-border bg-surface px-3 py-2 text-sm text-ink"
          >
            <option value="">Select category</option>
            {categories.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
          <Input value={careerSlug} onChange={(e) => setCareerSlug(e.target.value)} placeholder="slug" />
          <Input value={careerTitle} onChange={(e) => setCareerTitle(e.target.value)} placeholder="Title" />
          <Input
            value={careerDescription}
            onChange={(e) => setCareerDescription(e.target.value)}
            placeholder="Description"
          />
          <Button
            disabled={!careerCategoryId || !careerSlug || !careerTitle || !careerDescription}
            onClick={createCareer}
          >
            Add career
          </Button>
        </div>
      </Card>

      <div className="mt-6 space-y-2">
        {careers.map((c) => (
          <Card key={c.id} className="py-3">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-ink">{c.title}</p>
                <p className="text-xs text-muted">{c.category_key}</p>
              </div>
              <Button
                variant="secondary"
                onClick={() => setEditingId(editingId === c.id ? null : c.id)}
              >
                {editingId === c.id ? "Close" : "Edit"}
              </Button>
            </div>
            {editingId === c.id && (
              <EditCareerForm
                career={c}
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
