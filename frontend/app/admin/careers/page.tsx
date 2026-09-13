"use client";

import { useEffect, useState } from "react";
import { api, ApiError, type CareerCategory, type CareerListItem } from "@/lib/api";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export default function AdminCareersPage() {
  const [categories, setCategories] = useState<CareerCategory[]>([]);
  const [careers, setCareers] = useState<CareerListItem[]>([]);
  const [error, setError] = useState<string | null>(null);

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
            <p className="text-sm font-medium text-ink">{c.title}</p>
            <p className="text-xs text-muted">{c.category_key}</p>
          </Card>
        ))}
      </div>
    </div>
  );
}
