"use client";

import { useEffect, useState } from "react";
import { api, ApiError, type AssessmentSummary, type AssessmentQuestion, type CareerCategory } from "@/lib/api";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

type DraftOption = {
  value: string;
  label: string;
  weights: Record<string, number>;
};

function emptyOption(letter: string): DraftOption {
  return { value: letter, label: "", weights: {} };
}

export default function AdminAssessmentsPage() {
  const [assessments, setAssessments] = useState<AssessmentSummary[]>([]);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [error, setError] = useState<string | null>(null);

  const [categories, setCategories] = useState<CareerCategory[]>([]);
  const [selectedAssessment, setSelectedAssessment] = useState<string | null>(null);
  const [questions, setQuestions] = useState<AssessmentQuestion[]>([]);
  const [questionText, setQuestionText] = useState("");
  const [options, setOptions] = useState<DraftOption[]>([emptyOption("a"), emptyOption("b")]);
  const [weightCategory, setWeightCategory] = useState("");
  const [weightValue, setWeightValue] = useState("1");

  function load() {
    api.assessments().then(setAssessments).catch(() => setAssessments([]));
  }

  useEffect(load, []);
  useEffect(() => {
    api.careerCategories().then(setCategories).catch(() => setCategories([]));
  }, []);

  function loadQuestions(assessmentId: string) {
    setSelectedAssessment(assessmentId);
    api.assessmentQuestions(assessmentId).then(setQuestions).catch(() => setQuestions([]));
  }

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

  function updateOption(index: number, field: "value" | "label", value: string) {
    setOptions((prev) => prev.map((o, i) => (i === index ? { ...o, [field]: value } : o)));
  }

  function addWeight(index: number) {
    if (!weightCategory || !weightValue) return;
    setOptions((prev) =>
      prev.map((o, i) =>
        i === index
          ? { ...o, weights: { ...o.weights, [weightCategory]: Number(weightValue) } }
          : o
      )
    );
    setWeightCategory("");
    setWeightValue("1");
  }

  function removeWeight(index: number, key: string) {
    setOptions((prev) =>
      prev.map((o, i) => {
        if (i !== index) return o;
        const { [key]: _removed, ...rest } = o.weights;
        return { ...o, weights: rest };
      })
    );
  }

  function addOption() {
    const nextLetter = String.fromCharCode("a".charCodeAt(0) + options.length);
    setOptions((prev) => [...prev, emptyOption(nextLetter)]);
  }

  function removeOption(index: number) {
    setOptions((prev) => prev.filter((_, i) => i !== index));
  }

  async function submitQuestion() {
    if (!selectedAssessment) return;
    setError(null);
    try {
      await api.adminAddAssessmentQuestion(selectedAssessment, {
        question_text: questionText,
        display_order: questions.length,
        options: options.filter((o) => o.label.trim()),
      });
      setQuestionText("");
      setOptions([emptyOption("a"), emptyOption("b")]);
      loadQuestions(selectedAssessment);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong.");
    }
  }

  return (
    <div>
      <h1 className="font-display text-xl font-medium text-ink">Assessments</h1>
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
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-ink">{a.title}</p>
                <p className="text-xs text-muted">{a.description}</p>
              </div>
              <Button variant="secondary" onClick={() => loadQuestions(a.id)}>
                Manage questions
              </Button>
            </div>
          </Card>
        ))}
      </div>

      {selectedAssessment && (
        <Card className="mt-6">
          <h2 className="font-medium text-ink">
            Questions ({questions.length})
          </h2>
          <ul className="mt-2 space-y-1">
            {questions.map((q) => (
              <li key={q.id} className="text-sm text-muted">
                {q.display_order + 1}. {q.question_text} ({q.options.length} options)
              </li>
            ))}
          </ul>

          <div className="mt-4 border-t border-border pt-4">
            <h3 className="text-sm font-medium text-ink">Add a question</h3>
            <Input
              className="mt-2"
              value={questionText}
              onChange={(e) => setQuestionText(e.target.value)}
              placeholder="Question text"
            />

            <div className="mt-3 space-y-3">
              {options.map((opt, i) => (
                <div key={i} className="rounded-md border border-border p-3">
                  <div className="flex items-center gap-2">
                    <Input
                      value={opt.value}
                      onChange={(e) => updateOption(i, "value", e.target.value)}
                      placeholder="value"
                      className="w-16"
                    />
                    <Input
                      value={opt.label}
                      onChange={(e) => updateOption(i, "label", e.target.value)}
                      placeholder="Option label"
                    />
                    {options.length > 2 && (
                      <Button variant="secondary" onClick={() => removeOption(i)}>
                        Remove
                      </Button>
                    )}
                  </div>
                  <div className="mt-2 flex flex-wrap items-center gap-2">
                    {Object.entries(opt.weights).map(([key, val]) => (
                      <span
                        key={key}
                        className="flex items-center gap-1 rounded-full bg-primary/10 px-2 py-1 text-xs text-primary"
                      >
                        {key}: {val}
                        <button type="button" onClick={() => removeWeight(i, key)}>
                          ×
                        </button>
                      </span>
                    ))}
                    <select
                      value={weightCategory}
                      onChange={(e) => setWeightCategory(e.target.value)}
                      className="rounded-md border border-border bg-surface px-2 py-1 text-xs text-ink"
                    >
                      <option value="">category</option>
                      {categories.map((c) => (
                        <option key={c.key} value={c.key}>
                          {c.key}
                        </option>
                      ))}
                    </select>
                    <Input
                      value={weightValue}
                      onChange={(e) => setWeightValue(e.target.value)}
                      className="w-14 text-xs"
                    />
                    <Button variant="secondary" onClick={() => addWeight(i)}>
                      + weight
                    </Button>
                  </div>
                </div>
              ))}
            </div>
            <div className="mt-3 flex gap-2">
              <Button variant="secondary" onClick={addOption}>
                + option
              </Button>
              <Button disabled={!questionText} onClick={submitQuestion}>
                Save question
              </Button>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
}
