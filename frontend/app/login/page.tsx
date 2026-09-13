"use client";

import { useState } from "react";
import Link from "next/link";
import { useAuth, ApiError } from "@/lib/auth-context";
import { useLanguage } from "@/lib/language-context";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Field } from "@/components/ui/field";
import { Card } from "@/components/ui/card";
import { SiteNav } from "@/components/site-nav";

export default function LoginPage() {
  const { login } = useAuth();
  const { t } = useLanguage();
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
          <h1 className="font-display text-xl font-medium text-ink">{t("auth.loginTitle")}</h1>
          <form onSubmit={handleSubmit} className="mt-6 space-y-4">
            <Field label={t("auth.identifierLabel")} htmlFor="identifier">
              <Input
                id="identifier"
                required
                value={identifier}
                onChange={(e) => setIdentifier(e.target.value)}
                placeholder={t("auth.identifierPlaceholder")}
              />
            </Field>
            <Field label={t("auth.passwordLabel")} htmlFor="password">
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
              {submitting ? t("auth.loggingIn") : t("auth.loginButton")}
            </Button>
          </form>
          <p className="mt-5 text-sm text-muted">
            {t("auth.newHere")}{" "}
            <Link href="/register" className="font-medium text-primary">
              {t("auth.createAccountLink")}
            </Link>
          </p>
        </Card>
      </main>
    </>
  );
}
