"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api, ApiError } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Field } from "@/components/ui/field";
import { Card } from "@/components/ui/card";
import { SiteNav } from "@/components/site-nav";

type Step = "mobile" | "reset" | "done";

export default function ForgotPasswordPage() {
  const router = useRouter();
  const [step, setStep] = useState<Step>("mobile");
  const [mobile, setMobile] = useState("");
  const [devOtp, setDevOtp] = useState<string | null>(null);
  const [otp, setOtp] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function requestOtp(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      const res = await api.requestPasswordResetOtp(mobile);
      setMessage(res.message);
      setDevOtp(res.dev_otp);
      setStep("reset");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong.");
    } finally {
      setSubmitting(false);
    }
  }

  async function resetPassword(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    if (newPassword !== confirmPassword) {
      setError("Passwords don't match.");
      return;
    }
    setSubmitting(true);
    try {
      await api.resetPassword(mobile, otp, newPassword);
      setStep("done");
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
          {step === "mobile" && (
            <>
              <h1 className="font-display text-xl font-medium text-ink">Reset password</h1>
              <p className="mt-1 text-sm text-muted">
                We&apos;ll send a code to your mobile number to reset your password.
              </p>
              <form onSubmit={requestOtp} className="mt-6 space-y-4">
                <Field label="Mobile number" htmlFor="mobile">
                  <Input
                    id="mobile"
                    required
                    value={mobile}
                    onChange={(e) => setMobile(e.target.value)}
                    placeholder="9876543210"
                  />
                </Field>
                {error && <p className="text-sm text-danger">{error}</p>}
                <Button type="submit" disabled={submitting || !mobile} className="w-full">
                  {submitting ? "Sending…" : "Send code"}
                </Button>
              </form>
            </>
          )}

          {step === "reset" && (
            <>
              <h1 className="font-display text-xl font-medium text-ink">Enter code</h1>
              {message && <p className="mt-1 text-sm text-muted">{message}</p>}
              {devOtp && (
                <p className="mt-2 text-xs text-muted">
                  Dev-mode code (no SMS yet): <span className="font-mono">{devOtp}</span>
                </p>
              )}
              <form onSubmit={resetPassword} className="mt-6 space-y-4">
                <Field label="Code" htmlFor="otp">
                  <Input id="otp" required value={otp} onChange={(e) => setOtp(e.target.value)} />
                </Field>
                <Field label="New password" htmlFor="new_password">
                  <Input
                    id="new_password"
                    type="password"
                    required
                    minLength={8}
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                  />
                </Field>
                <Field label="Confirm new password" htmlFor="confirm_password">
                  <Input
                    id="confirm_password"
                    type="password"
                    required
                    minLength={8}
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                  />
                </Field>
                {error && <p className="text-sm text-danger">{error}</p>}
                <Button type="submit" disabled={submitting} className="w-full">
                  {submitting ? "Resetting…" : "Reset password"}
                </Button>
              </form>
            </>
          )}

          {step === "done" && (
            <>
              <h1 className="font-display text-xl font-medium text-ink">Password reset</h1>
              <p className="mt-2 text-sm text-muted">
                Your password has been changed. Any other devices you were logged in on have been
                signed out, for safety.
              </p>
              <Button className="mt-6 w-full" onClick={() => router.push("/login")}>
                Log in
              </Button>
            </>
          )}

          {step !== "done" && (
            <p className="mt-5 text-sm text-muted">
              <Link href="/login" className="font-medium text-primary">
                Back to log in
              </Link>
            </p>
          )}
        </Card>
      </main>
    </>
  );
}
