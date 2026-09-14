"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { Moon, Sun, Globe, ChevronDown } from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { useTheme } from "@/lib/theme-context";
import { useLanguage, SUPPORTED_LANGUAGES, type LanguageCode } from "@/lib/language-context";
import { api } from "@/lib/api";

function LanguagePicker() {
  const { user } = useAuth();
  const { language, setLanguage, t } = useLanguage();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function onClickOutside(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener("mousedown", onClickOutside);
    return () => document.removeEventListener("mousedown", onClickOutside);
  }, []);

  const current = SUPPORTED_LANGUAGES.find((l) => l.code === language);

  function pick(code: LanguageCode) {
    setOpen(false);
    // Switches the whole UI instantly, logged in or not. If logged in,
    // also best-effort persists it to the account (so career/course
    // content-language and a next login both pick it up too).
    setLanguage(code, user ? (c) => api.updateLanguage(c) : undefined);
  }

  return (
    <div className="relative" ref={ref}>
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="flex items-center gap-1 rounded-md px-2 py-1.5 text-sm text-ink hover:bg-border/30"
        aria-label={t("nav.changeLanguage")}
      >
        <Globe size={16} />
        <span className="hidden sm:inline">{current?.native_name ?? "EN"}</span>
        <ChevronDown size={14} />
      </button>
      {open && (
        <div className="absolute right-0 top-full mt-1 w-40 overflow-hidden rounded-md border border-border bg-surface shadow-md">
          {SUPPORTED_LANGUAGES.map((l) => (
            <button
              key={l.code}
              type="button"
              onClick={() => pick(l.code)}
              className={`block w-full px-3 py-2 text-left text-sm hover:bg-border/30 ${
                l.code === language ? "text-primary" : "text-ink"
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
  const { t } = useLanguage();
  return (
    <button
      type="button"
      onClick={toggleTheme}
      className="rounded-md p-2 text-ink hover:bg-border/30"
      aria-label={theme === "dark" ? t("nav.switchToLight") : t("nav.switchToDark")}
    >
      {theme === "dark" ? <Sun size={16} /> : <Moon size={16} />}
    </button>
  );
}

export function SiteNav() {
  const { user } = useAuth();
  const { t } = useLanguage();

  return (
    <nav className="sticky top-0 z-20 border-b border-border bg-background/80 backdrop-blur">
      <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-3">
        {/* Logged in: the logo goes straight to the dashboard, never
            back to the marketing landing page — that page's CTAs are
            aimed at someone who hasn't signed up yet ("Start
            exploring" -> /register), so landing there while already
            authenticated reads as being asked to log in again. */}
        <Link
          href={user ? "/dashboard" : "/"}
          className="font-display text-lg font-semibold text-ink"
        >
          {t("nav.brand")}
        </Link>
        <div className="flex items-center gap-1 text-sm text-ink sm:gap-2">
          {user && (
            <Link href="/dashboard" className="rounded-md px-2 py-1.5 hover:bg-border/30">
              {t("nav.dashboard")}
            </Link>
          )}
          <Link href="/careers" className="rounded-md px-2 py-1.5 hover:bg-border/30">
            {t("nav.careers")}
          </Link>
          <Link href="/courses" className="rounded-md px-2 py-1.5 hover:bg-border/30">
            {t("nav.courses")}
          </Link>
          {user?.role === "student" && (
            <>
              <Link href="/student/assessment" className="rounded-md px-2 py-1.5 hover:bg-border/30">
                {t("nav.assessment")}
              </Link>
              <Link href="/student/mentorship" className="rounded-md px-2 py-1.5 hover:bg-border/30">
                {t("nav.mentorship")}
              </Link>
            </>
          )}
          {user?.role === "mentor" && (
            <>
              <Link href="/mentor/requests" className="rounded-md px-2 py-1.5 hover:bg-border/30">
                {t("nav.requests")}
              </Link>
              <Link href="/mentor/sessions" className="rounded-md px-2 py-1.5 hover:bg-border/30">
                {t("nav.sessions")}
              </Link>
            </>
          )}
          {user?.role === "parent" && (
            <Link href="/parent/students" className="rounded-md px-2 py-1.5 hover:bg-border/30">
              {t("nav.myStudents")}
            </Link>
          )}
          {user?.role === "school_admin" && (
            <Link href="/school/students" className="rounded-md px-2 py-1.5 hover:bg-border/30">
              {t("nav.myStudents")}
            </Link>
          )}
          {user?.role === "admin" && (
            <Link href="/admin" className="rounded-md px-2 py-1.5 hover:bg-border/30">
              {t("nav.admin")}
            </Link>
          )}
          {user && (
            <Link href="/announcements" className="rounded-md px-2 py-1.5 hover:bg-border/30">
              {t("nav.announcements")}
            </Link>
          )}
          {/* Profile-type links always last, per explicit preference */}
          {user?.role === "student" && (
            <Link href="/student/profile" className="rounded-md px-2 py-1.5 hover:bg-border/30">
              {t("nav.myProfile")}
            </Link>
          )}
          {user?.role === "mentor" && (
            <Link href="/mentor/profile" className="rounded-md px-2 py-1.5 hover:bg-border/30">
              {t("nav.myProfile")}
            </Link>
          )}
          {!user && (
            <Link href="/login" className="rounded-md px-2 py-1.5 hover:bg-border/30">
              {t("nav.login")}
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
