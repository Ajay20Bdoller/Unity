"use client";

import { useState } from "react";
import { api, ApiError, type ChatMessage } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";

const SUGGESTED_QUESTIONS = [
  "What does an AI engineer do?",
  "What is an MBA?",
  "What does a scientist do?",
  "What is data science?",
  "What careers can I explore after Class 10?",
];

export function AIAssistantCard() {
  const [question, setQuestion] = useState("");
  const [history, setHistory] = useState<ChatMessage[]>([]);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function ask(text: string) {
    const trimmed = text.trim();
    if (!trimmed || submitting) return;

    setSubmitting(true);
    setError(null);
    const nextHistory: ChatMessage[] = [...history, { role: "user", content: trimmed }];
    setHistory(nextHistory);
    setQuestion("");

    try {
      // Only the last few turns are sent — the assistant doesn't keep
      // unlimited memory (see backend AIChatRequest).
      const priorTurns = history.slice(-6);
      const { answer } = await api.aiChat(trimmed, priorTurns);
      setHistory([...nextHistory, { role: "assistant", content: answer }]);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong.");
      setHistory(history); // roll back the optimistic user turn on failure
    } finally {
      setSubmitting(false);
    }
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    ask(question);
  }

  return (
    <Card>
      <h2 className="font-medium text-ink">Ask Career AI</h2>
      <p className="mt-1 text-sm text-muted">
        Have a question about careers, education, skills or jobs? Ask here.
      </p>

      {history.length > 0 && (
        <div className="mt-4 max-h-72 space-y-3 overflow-y-auto rounded-md border border-border p-3">
          {history.map((turn, i) => (
            <div key={i} className={turn.role === "user" ? "text-right" : "text-left"}>
              <p
                className={
                  turn.role === "user"
                    ? "inline-block rounded-md bg-primary/10 px-3 py-2 text-sm text-ink"
                    : "inline-block rounded-md bg-border/30 px-3 py-2 text-sm text-ink"
                }
              >
                {turn.content}
              </p>
            </div>
          ))}
          {submitting && <p className="text-sm text-muted">Thinking…</p>}
        </div>
      )}

      <form onSubmit={handleSubmit} className="mt-4 flex gap-2">
        <Input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="What is a software engineer?"
          disabled={submitting}
          aria-label="Ask Career AI a question"
        />
        <Button type="submit" disabled={submitting || !question.trim()}>
          {submitting ? "Asking…" : "Ask AI"}
        </Button>
      </form>

      {error && <p className="mt-2 text-sm text-danger">{error}</p>}

      {history.length === 0 && (
        <div className="mt-4 flex flex-wrap gap-2">
          {SUGGESTED_QUESTIONS.map((q) => (
            <button
              key={q}
              type="button"
              onClick={() => ask(q)}
              disabled={submitting}
              className="rounded-full border border-border px-3 py-1.5 text-xs text-ink hover:bg-border/30 disabled:opacity-50"
            >
              {q}
            </button>
          ))}
        </div>
      )}
    </Card>
  );
}
