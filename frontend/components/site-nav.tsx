"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { Moon, Sun, Globe, ChevronDown } from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { useTheme } from "@/lib/theme-context";
import { api, type Language } from "@/lib/api";

function LanguagePicker() {
  const { user } = useAuth();
  const [open, setOpen] = useState(false);
  const [languages, setLanguages] = useState<Language[]>([]);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    api.languages().then(setLanguages).catch(() => setLanguages([]));
  }, []);

  useEffect(() => {
    function onClickOutside(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener("mousedown", onClickOutside);
    return () => document.removeEventListener("mousedown", onClickOutside);
  }, []);

  const current = languages.find((l) => l.code === user?.preferred_language);

  async function pick(code: string) {
    setOpen(false);
    if (user) {
      await api.updateLanguage(code);
      // A full reload keeps this simple and correct everywhere, since
      // preferred_language isn't held in a lot of local component state.
      window.location.reload();
    }
  }

  return (
    <div className="relative" ref={ref}>
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="flex items-center gap-1 rounded-md px-2 py-1.5 text-sm text-ink hover:bg-border/30"
        aria-label="Change language"
      >
        <Globe size={16} />
        <span className="hidden sm:inline">{current?.native_name ?? "EN"}</span>
        <ChevronDown size={14} />
      </button>
      {open && (
        <div className="absolute right-0 top-full mt-1 w-40 overflow-hidden rounded-md border border-border bg-surface shadow-md">
          {languages.map((l) => (
            <button
              key={l.code}
              type="button"
              onClick={() => pick(l.code)}
              className={`block w-full px-3 py-2 text-left text-sm hover:bg-border/30 ${
                l.code === user?.preferred_language ? "text-primary" : "text-ink"
              }`}
            >
              {l.native_name}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();
  return (
    <button
      type="button"
      onClick={toggleTheme}
      className="rounded-md p-2 text-ink hover:bg-border/30"
      aria-label={theme === "dark" ? "Switch to light mode" : "Switch to dark mode"}
    >
      {theme === "dark" ? <Sun size={16} /> : <Moon size={16} />}
    </button>
  );
}

export function SiteNav() {
  const { user } = useAuth();

  return (
    <nav className="sticky top-0 z-20 border-b border-border bg-background/80 backdrop-blur">
      <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-3">
        <Link href="/" className="font-display text-lg font-semibold text-ink">
          Unity
        </Link>
        <div className="flex items-center gap-1 text-sm text-ink sm:gap-2">
          <Link href="/careers" className="rounded-md px-2 py-1.5 hover:bg-border/30">
            Careers
          </Link>
          <Link href="/courses" className="rounded-md px-2 py-1.5 hover:bg-border/30">
            Courses
          </Link>
          {user?.role === "student" && (
            <>
              <Link href="/student/assessment" className="rounded-md px-2 py-1.5 hover:bg-border/30">
                Assessment
              </Link>
              <Link href="/student/mentorship" className="rounded-md px-2 py-1.5 hover:bg-border/30">
                Mentorship
              </Link>
            </>
          )}
          {user?.role === "mentor" && (
            <>
              <Link href="/mentor/profile" className="rounded-md px-2 py-1.5 hover:bg-border/30">
                My Profile
              </Link>
              <Link href="/mentor/requests" className="rounded-md px-2 py-1.5 hover:bg-border/30">
                Requests
              </Link>
            </>
          )}
          {user?.role === "parent" && (
            <Link href="/parent/students" className="rounded-md px-2 py-1.5 hover:bg-border/30">
              My Students
            </Link>
          )}
          {user?.role === "admin" && (
            <Link href="/admin" className="rounded-md px-2 py-1.5 hover:bg-border/30">
              Admin
            </Link>
          )}
          {user ? (
            <Link href="/dashboard" className="rounded-md px-2 py-1.5 hover:bg-border/30">
              Dashboard
            </Link>
          ) : (
            <Link href="/login" className="rounded-md px-2 py-1.5 hover:bg-border/30">
              Log in
            </Link>
          )}

          <div className="ml-1 flex items-center gap-1 border-l border-border pl-2">
            <LanguagePicker />
            <ThemeToggle />
          </div>
        </div>
      </div>
    </nav>
  );
}
