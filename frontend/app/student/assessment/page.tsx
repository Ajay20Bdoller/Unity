"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  api,
  type AssessmentQuestion,
  type AssessmentResult,
  type AssessmentSummary,
} from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { SiteNav } from "@/components/site-nav";

type Step = "loading" | "intro" | "questions" | "submitting" | "result" | "unavailable";

export default function AssessmentPage() {
  const { user, loading: authLoading } = useAuth();
  const [step, setStep] = useState<Step>("loading");
  const [assessment, setAssessment] = useState<AssessmentSummary | null>(null);
  const [questions, setQuestions] = useState<AssessmentQuestion[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [result, setResult] = useState<AssessmentResult | null>(null);

  useEffect(() => {
    if (authLoading) return;
    if (!user || user.role !== "student") {
      setStep("unavailable");
      return;
    }
    api
      .assessments()
      .then((list) => {
        if (list.length === 0) {
          setStep("unavailable");
          return;
        }
        setAssessment(list[0]);
        setStep("intro");
      })
      .catch(() => setStep("unavailable"));
  }, [authLoading, user]);

  async function start() {
    if (!assessment) return;
    const qs = await api.assessmentQuestions(assessment.id);
    setQuestions(qs);
    setCurrentIndex(0);
    setAnswers({});
    setStep("questions");
  }

  function selectAnswer(questionId: string, value: string) {
    setAnswers((prev) => ({ ...prev, [questionId]: value }));
  }

  async function submit() {
    if (!assessment) return;
    setStep("submitting");
    const responses = Object.entries(answers).map(([question_id, selected_option_value]) => ({
      question_id,
      selected_option_value,
    }));
    const res = await api.submitAssessment(assessment.id, responses);
    setResult(res);
    setStep("result");
  }

  if (authLoading || step === "loading") {
    return (
      <>
        <SiteNav />
        <main className="mx-auto max-w-2xl px-6 py-10">
          <p className="text-sm text-muted">Loading...</p>
        </main>
      </>
    );
  }

  if (!user || user.role !== "student") {
    return (
      <>
        <SiteNav />
        <main className="mx-auto max-w-2xl px-6 py-10">
          <p className="text-sm text-muted">This assessment is available to students only.</p>
        </main>
      </>
    );
  }

  if (step === "unavailable") {
    return (
      <>
        <SiteNav />
        <main className="mx-auto max-w-2xl px-6 py-10">
          <p className="text-sm text-muted">No assessment is available right now.</p>
        </main>
      </>
    );
  }

  return (
    <>
      <SiteNav />
      <main className="mx-auto max-w-2xl px-6 py-10">
        {step === "intro" && assessment && (
          <Card>
            <h1 className="font-display text-xl font-medium text-ink">{assessment.title}</h1>
            <p className="mt-2 text-sm text-muted">{assessment.description}</p>
            <Button className="mt-6" onClick={start}>
              Start
            </Button>
          </Card>
        )}

        {step === "questions" && questions.length > 0 && (
          <Card>
            <p className="text-xs text-muted">
              Question {currentIndex + 1} of {questions.length}
            </p>
            <h2 className="mt-2 font-medium text-ink">
              {questions[currentIndex].question_text}
            </h2>
            <div className="mt-4 space-y-2">
              {questions[currentIndex].options.map((option) => (
                <label
                  key={option.value}
                  className={`block cursor-pointer rounded-md border px-3 py-2 text-sm ${
                    answers[questions[currentIndex].id] === option.value
                      ? "border-primary bg-primary/10"
                      : "border-border hover:bg-border/30"
                  }`}
                >
                  <input
                    type="radio"
                    name={questions[currentIndex].id}
                    value={option.value}
                    checked={answers[questions[currentIndex].id] === option.value}
                    onChange={() => selectAnswer(questions[currentIndex].id, option.value)}
                    className="mr-2"
                  />
                  {option.label}
                </label>
              ))}
            </div>
            <div className="mt-6 flex justify-between">
              <Button
                variant="secondary"
                disabled={currentIndex === 0}
                onClick={() => setCurrentIndex((i) => i - 1)}
              >
                Back
              </Button>
              {currentIndex < questions.length - 1 ? (
                <Button
                  disabled={!answers[questions[currentIndex].id]}
                  onClick={() => setCurrentIndex((i) => i + 1)}
                >
                  Next
                </Button>
              ) : (
                <Button
                  disabled={Object.keys(answers).length < questions.length}
                  onClick={submit}
                >
                  Submit
                </Button>
              )}
            </div>
          </Card>
        )}

        {step === "submitting" && <p className="text-sm text-muted">Scoring your answers...</p>}

        {step === "result" && result && (
          <Card>
            <h1 className="font-display text-xl font-medium text-ink">Areas to explore</h1>
            <p className="mt-2 text-sm text-muted">{result.note}</p>
            <div className="mt-4 space-y-2">
              {result.suggested_categories.map((cat) => (
                <Link
                  key={cat.key}
                  href={`/careers?category=${cat.key}`}
                  className="block rounded-md border border-border px-3 py-2 text-sm text-ink hover:bg-border/30"
                >
                  {cat.name}
                </Link>
              ))}
              {result.suggested_categories.length === 0 && (
                <p className="text-sm text-muted">
                  Your answers didn&apos;t point strongly toward a specific area — that&apos;s
                  okay, try exploring the career library directly.
                </p>
              )}
            </div>
          </Card>
        )}
      </main>
    </>
  );
}
