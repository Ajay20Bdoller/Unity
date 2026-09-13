"use client";

import Link from "next/link";
import { useAuth } from "@/lib/auth-context";

export function SiteNav() {
  const { user } = useAuth();

  return (
    <nav className="border-b border-border bg-white">
      <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-3">
        <Link href="/" className="font-semibold text-ink">
          Unity
        </Link>
        <div className="flex items-center gap-4 text-sm text-ink">
          <Link href="/careers" className="hover:text-primary">
            Careers
          </Link>
          <Link href="/courses" className="hover:text-primary">
            Courses
          </Link>
          {user?.role === "student" && (
            <Link href="/student/assessment" className="hover:text-primary">
              Assessment
            </Link>
          )}
          {user ? (
            <Link href="/dashboard" className="hover:text-primary">
              Dashboard
            </Link>
          ) : (
            <Link href="/login" className="hover:text-primary">
              Log in
            </Link>
          )}
        </div>
      </div>
    </nav>
  );
}
