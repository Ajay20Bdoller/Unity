"use client";

import { useState } from "react";
import Link from "next/link";
import { useAuth, ApiError } from "@/lib/auth-context";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Field } from "@/components/ui/field";
import { Card } from "@/components/ui/card";
import { SiteNav } from "@/components/site-nav";

export default function LoginPage() {
  const { login } = useAuth();
  const [identifier, setIdentifier] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await login(identifier, password);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <>
      <SiteNav />
      <main className="flex min-h-[calc(100vh-57px)] items-center justify-center px-6 py-12">
        <Card className="w-full max-w-sm">
          <h1 className="font-display text-xl font-medium text-ink">Log in</h1>
          <form onSubmit={handleSubmit} className="mt-6 space-y-4">
            <Field label="Email or mobile number" htmlFor="identifier">
              <Input
                id="identifier"
                required
                value={identifier}
                onChange={(e) => setIdentifier(e.target.value)}
                placeholder="you@example.com or 9876543210"
              />
            </Field>
            <Field label="Password" htmlFor="password">
              <Input
                id="password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </Field>
            {error && <p className="text-sm text-danger">{error}</p>}
            <Button type="submit" disabled={submitting} className="w-full">
              {submitting ? "Logging in…" : "Log in"}
            </Button>
          </form>
          <p className="mt-5 text-sm text-muted">
            New here?{" "}
            <Link href="/register" className="font-medium text-primary">
              Create an account
            </Link>
          </p>
        </Card>
      </main>
    </>
  );
}
