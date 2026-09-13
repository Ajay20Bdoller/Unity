"use client";

import { useState } from "react";
import Link from "next/link";
import { useAuth, ApiError } from "@/lib/auth-context";
import type { RegisterInput, UserRole } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Field } from "@/components/ui/field";
import { Card } from "@/components/ui/card";
import { SiteNav } from "@/components/site-nav";

const roles: { value: UserRole; label: string }[] = [
  { value: "student", label: "Student" },
  { value: "parent", label: "Parent / Guardian" },
  { value: "mentor", label: "Mentor" },
  { value: "school_admin", label: "School / Institution" },
];

const relationOptions = ["Mother", "Father", "Guardian", "Other"];

type FormState = {
  full_name: string;
  email: string;
  mobile_number: string;
  password: string;
  confirmPassword: string;
  date_of_birth: string;
  school_name: string;
  parent_name: string;
  parent_relation: string;
  address: string;
  district: string;
  state: string;
  country: string;
  student_name: string;
  relation_to_student: string;
  school_location: string;
};

const emptyForm: FormState = {
  full_name: "",
  email: "",
  mobile_number: "",
  password: "",
  confirmPassword: "",
  date_of_birth: "",
  school_name: "",
  parent_name: "",
  parent_relation: "",
  address: "",
  district: "",
  state: "",
  country: "India",
  student_name: "",
  relation_to_student: "",
  school_location: "",
};

export default function RegisterPage() {
  const { register } = useAuth();
  const [role, setRole] = useState<UserRole>("student");
  const [form, setForm] = useState<FormState>(emptyForm);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  function set<K extends keyof FormState>(key: K, value: FormState[K]) {
    setForm((prev) => ({ ...prev, [key]: value }));
  }

  function switchRole(next: UserRole) {
    setRole(next);
    setError(null);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);

    if (form.password !== form.confirmPassword) {
      setError("Passwords don't match.");
      return;
    }
    if (role === "student" && !form.email && !form.mobile_number) {
      setError("Add an email or a mobile number so you can log back in.");
      return;
    }

    const payload: RegisterInput = {
      full_name: form.full_name,
      role,
      password: form.password,
      email: form.email || undefined,
      mobile_number: form.mobile_number || undefined,
    };

    if (role === "student") {
      Object.assign(payload, {
        date_of_birth: form.date_of_birth,
        school_name: form.school_name,
        parent_name: form.parent_name,
        parent_relation: form.parent_relation,
        address: form.address,
        district: form.district,
        state: form.state,
        country: form.country || "India",
      });
    } else if (role === "parent") {
      Object.assign(payload, {
        student_name: form.student_name,
        relation_to_student: form.relation_to_student,
      });
    } else if (role === "mentor") {
      Object.assign(payload, { date_of_birth: form.date_of_birth });
    } else if (role === "school_admin") {
      Object.assign(payload, {
        date_of_birth: form.date_of_birth,
        school_name: form.school_name,
        school_location: form.school_location,
      });
    }

    setSubmitting(true);
    try {
      await register(payload);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong.");
      setSubmitting(false);
    }
  }

  return (
    <>
      <SiteNav />
      <main className="flex min-h-[calc(100vh-57px)] items-center justify-center px-6 py-12">
        <Card className="w-full max-w-lg">
          <h1 className="font-display text-xl font-medium text-ink">Create an account</h1>

          <div className="mt-5 grid grid-cols-2 gap-2 sm:grid-cols-4">
            {roles.map((r) => (
              <button
                key={r.value}
                type="button"
                onClick={() => switchRole(r.value)}
                className={`rounded-md border px-3 py-2 text-sm ${
                  role === r.value
                    ? "border-primary bg-primary/10 text-primary"
                    : "border-border text-ink hover:bg-border/30"
                }`}
              >
                {r.label}
              </button>
            ))}
          </div>

          <form onSubmit={handleSubmit} className="mt-6 space-y-4">
            <Field label="Full name" htmlFor="full_name">
              <Input
                id="full_name"
                required
                value={form.full_name}
                onChange={(e) => set("full_name", e.target.value)}
              />
            </Field>

            <div className="grid grid-cols-2 gap-4">
              <Field label={role === "student" ? "Email (optional)" : "Email"} htmlFor="email">
                <Input
                  id="email"
                  type="email"
                  required={role !== "student"}
                  value={form.email}
                  onChange={(e) => set("email", e.target.value)}
                />
              </Field>
              <Field label="Mobile number" htmlFor="mobile_number">
                <Input
                  id="mobile_number"
                  required={role !== "student"}
                  value={form.mobile_number}
                  onChange={(e) => set("mobile_number", e.target.value)}
                  placeholder="9876543210"
                />
              </Field>
            </div>
            {role === "student" && (
              <p className="text-xs text-muted">
                Add at least an email or a mobile number — you&apos;ll use it to log in later.
              </p>
            )}

            {(role === "student" || role === "mentor" || role === "school_admin") && (
              <Field label="Date of birth" htmlFor="date_of_birth">
                <Input
                  id="date_of_birth"
                  type="date"
                  required
                  value={form.date_of_birth}
                  onChange={(e) => set("date_of_birth", e.target.value)}
                />
              </Field>
            )}

            {role === "student" && (
              <>
                <Field label="School name" htmlFor="school_name">
                  <Input
                    id="school_name"
                    required
                    value={form.school_name}
                    onChange={(e) => set("school_name", e.target.value)}
                  />
                </Field>
                <div className="grid grid-cols-2 gap-4">
                  <Field label="Parent/guardian name" htmlFor="parent_name">
                    <Input
                      id="parent_name"
                      required
                      value={form.parent_name}
                      onChange={(e) => set("parent_name", e.target.value)}
                    />
                  </Field>
                  <Field label="Relation" htmlFor="parent_relation">
                    <select
                      id="parent_relation"
                      required
                      value={form.parent_relation}
                      onChange={(e) => set("parent_relation", e.target.value)}
                      className="w-full rounded-md border border-border bg-surface px-3 py-2 text-sm text-ink focus:outline-none focus:ring-2 focus:ring-primary/40"
                    >
                      <option value="">Select</option>
                      {relationOptions.map((r) => (
                        <option key={r} value={r}>
                          {r}
                        </option>
                      ))}
                    </select>
                  </Field>
                </div>
                <Field label="Home address" htmlFor="address">
                  <Input
                    id="address"
                    required
                    value={form.address}
                    onChange={(e) => set("address", e.target.value)}
                  />
                </Field>
                <div className="grid grid-cols-3 gap-4">
                  <Field label="District" htmlFor="district">
                    <Input
                      id="district"
                      required
                      value={form.district}
                      onChange={(e) => set("district", e.target.value)}
                    />
                  </Field>
                  <Field label="State" htmlFor="state">
                    <Input
                      id="state"
                      required
                      value={form.state}
                      onChange={(e) => set("state", e.target.value)}
                    />
                  </Field>
                  <Field label="Country" htmlFor="country">
                    <Input
                      id="country"
                      required
                      value={form.country}
                      onChange={(e) => set("country", e.target.value)}
                    />
                  </Field>
                </div>
              </>
            )}

            {role === "parent" && (
              <div className="grid grid-cols-2 gap-4">
                <Field label="Student's name" htmlFor="student_name">
                  <Input
                    id="student_name"
                    required
                    value={form.student_name}
                    onChange={(e) => set("student_name", e.target.value)}
                  />
                </Field>
                <Field label="Relation to student" htmlFor="relation_to_student">
                  <select
                    id="relation_to_student"
                    required
                    value={form.relation_to_student}
                    onChange={(e) => set("relation_to_student", e.target.value)}
                    className="w-full rounded-md border border-border bg-surface px-3 py-2 text-sm text-ink focus:outline-none focus:ring-2 focus:ring-primary/40"
                  >
                    <option value="">Select</option>
                    {relationOptions.map((r) => (
                      <option key={r} value={r}>
                        {r}
                      </option>
                    ))}
                  </select>
                </Field>
              </div>
            )}
            {role === "parent" && (
              <p className="-mt-2 text-xs text-muted">
                You&apos;ll confirm this link with your child from your dashboard after signing up.
              </p>
            )}

            {role === "school_admin" && (
              <div className="grid grid-cols-2 gap-4">
                <Field label="School name" htmlFor="school_name_admin">
                  <Input
                    id="school_name_admin"
                    required
                    value={form.school_name}
                    onChange={(e) => set("school_name", e.target.value)}
                  />
                </Field>
                <Field label="School location" htmlFor="school_location">
                  <Input
                    id="school_location"
                    required
                    value={form.school_location}
                    onChange={(e) => set("school_location", e.target.value)}
                  />
                </Field>
              </div>
            )}

            <div className="grid grid-cols-2 gap-4">
              <Field label="Password" htmlFor="password">
                <Input
                  id="password"
                  type="password"
                  required
                  minLength={8}
                  value={form.password}
                  onChange={(e) => set("password", e.target.value)}
                />
              </Field>
              <Field label="Confirm password" htmlFor="confirmPassword">
                <Input
                  id="confirmPassword"
                  type="password"
                  required
                  minLength={8}
                  value={form.confirmPassword}
                  onChange={(e) => set("confirmPassword", e.target.value)}
                />
              </Field>
            </div>

            {error && <p className="text-sm text-danger">{error}</p>}
            <Button type="submit" disabled={submitting} className="w-full">
              {submitting ? "Creating account…" : "Create account"}
            </Button>
          </form>

          <p className="mt-5 text-sm text-muted">
            Already have an account?{" "}
            <Link href="/login" className="font-medium text-primary">
              Log in
            </Link>
          </p>
        </Card>
      </main>
    </>
  );
}
