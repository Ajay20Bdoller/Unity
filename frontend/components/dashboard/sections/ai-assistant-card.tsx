"use client";

import { useState } from "react";
import ReactMarkdown from "react-markdown";
import { Sparkles } from "lucide-react";
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

// Keeps the AI's markdown (bold, bullet lists, paragraphs) looking like
// part of the app instead of raw browser-default <ul>/<strong> styling.
const markdownComponents = {
  p: ({ ...props }) => <p className="mb-2 last:mb-0" {...props} />,
  strong: ({ ...props }) => <strong className="font-semibold text-ink" {...props} />,
  ul: ({ ...props }) => <ul className="mb-2 ml-4 list-disc space-y-1 last:mb-0" {...props} />,
  ol: ({ ...props }) => <ol className="mb-2 ml-4 list-decimal space-y-1 last:mb-0" {...props} />,
  li: ({ ...props }) => <li className="leading-relaxed" {...props} />,
  a: ({ ...props }) => (
    <a className="text-primary underline hover:no-underline" target="_blank" rel="noreferrer" {...props} />
  ),
};

function ThinkingIndicator() {
  return (
    <div className="flex items-center gap-1 px-1 py-2">
      <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-muted [animation-delay:-0.3s]" />
      <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-muted [animation-delay:-0.15s]" />
      <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-muted" />
    </div>
  );
}

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
      <div className="flex items-center gap-2">
        <span className="flex h-7 w-7 items-center justify-center rounded-full bg-primary/10 text-primary">
          <Sparkles size={14} />
        </span>
        <h2 className="font-medium text-ink">Ask Career AI</h2>
      </div>
      <p className="mt-1 text-sm text-muted">
        Have a question about careers, education, skills or jobs? Ask here.
      </p>

      {history.length > 0 && (
        <div className="mt-4 max-h-96 space-y-4 overflow-y-auto rounded-lg bg-background p-3">
          {history.map((turn, i) => (
            <div key={i} className={`flex ${turn.role === "user" ? "justify-end" : "justify-start"}`}>
              <div
                className={
                  turn.role === "user"
                    ? "max-w-[85%] rounded-2xl rounded-br-sm bg-primary px-4 py-2.5 text-sm text-primary-foreground"
                    : "max-w-[90%] rounded-2xl rounded-bl-sm border border-border bg-surface px-4 py-2.5 text-sm text-ink"
                }
              >
                {turn.role === "assistant" ? (
                  <div className="prose-sm">
                    <ReactMarkdown components={markdownComponents}>{turn.content}</ReactMarkdown>
                  </div>
                ) : (
                  turn.content
                )}
              </div>
            </div>
          ))}
          {submitting && (
            <div className="flex justify-start">
              <div className="rounded-2xl rounded-bl-sm border border-border bg-surface px-2">
                <ThinkingIndicator />
              </div>
            </div>
          )}
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
