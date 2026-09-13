"use client";

import { useEffect, useState } from "react";
import { api, ApiError, type AssessmentSummary } from "@/lib/api";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export default function AdminAssessmentsPage() {
  const [assessments, setAssessments] = useState<AssessmentSummary[]>([]);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [error, setError] = useState<string | null>(null);

  function load() {
    api.assessments().then(setAssessments).catch(() => setAssessments([]));
  }

  useEffect(load, []);

  async function create() {
    setError(null);
    try {
      await api.adminCreateAssessment({ title, description });
      setTitle("");
      setDescription("");
      load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong.");
    }
  }

  return (
    <div>
      <h1 className="font-display text-xl font-medium text-ink">Assessments</h1>
      <p className="mt-1 text-sm text-muted">
        Adding weighted questions isn&apos;t in this form yet — use the API directly for now
        (POST /admin/assessments/&#123;id&#125;/questions).
      </p>
      {error && <p className="mt-2 text-sm text-danger">{error}</p>}

      <Card className="mt-4">
        <h2 className="font-medium text-ink">New assessment</h2>
        <div className="mt-2 space-y-2">
          <Input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Title" />
          <Input
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Description"
          />
          <Button disabled={!title || !description} onClick={create}>
            Add
          </Button>
        </div>
      </Card>

      <div className="mt-6 space-y-2">
        {assessments.map((a) => (
          <Card key={a.id} className="py-3">
            <p className="text-sm font-medium text-ink">{a.title}</p>
            <p className="text-xs text-muted">{a.description}</p>
          </Card>
        ))}
      </div>
    </div>
  );
}
