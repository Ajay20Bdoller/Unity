"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Moon, Sun, Globe, ChevronDown, Bell, Settings as SettingsIcon } from "lucide-react";
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

type QuickLink = { href: string; label: string };

// What each role sees in the Settings dropdown, beyond the universal
// Change password / Log out at the bottom — the less-frequently-used
// pages that used to sit as permanent nav links. Admin is deliberately
// untouched (keeps its own plain Settings link, no dropdown) — its nav
// is already short and role-appropriate as is.
function useRoleQuickLinks(): QuickLink[] {
  const { user } = useAuth();
  const { t } = useLanguage();
  if (!user) return [];
  switch (user.role) {
    case "student":
      return [
        { href: "/student/assessment", label: t("nav.assessment") },
        { href: "/student/mentorship", label: t("nav.mentorship") },
        { href: "/student/guardians", label: t("nav.guardian") },
        { href: "/student/profile", label: t("nav.myProfile") },
      ];
    case "mentor":
      return [
        { href: "/mentor/requests", label: t("nav.requests") },
        { href: "/mentor/sessions", label: t("nav.sessions") },
        { href: "/mentor/profile", label: t("nav.myProfile") },
      ];
    case "parent":
      return [{ href: "/parent/students", label: t("nav.myStudents") }];
    case "school_admin":
      return [{ href: "/school/students", label: t("nav.myStudents") }];
    default:
      return [];
  }
}

function SettingsDropdown() {
  const { logout } = useAuth();
  const { t } = useLanguage();
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const quickLinks = useRoleQuickLinks();

  useEffect(() => {
    function onClickOutside(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener("mousedown", onClickOutside);
    return () => document.removeEventListener("mousedown", onClickOutside);
  }, []);

  return (
    <div className="relative" ref={ref}>
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="flex items-center gap-1 rounded-md px-2 py-1.5 text-sm text-ink hover:bg-border/30"
        aria-label={t("nav.settings")}
      >
        <SettingsIcon size={16} />
        <span className="hidden sm:inline">{t("nav.settings")}</span>
        <ChevronDown size={14} />
      </button>
      {open && (
        <div className="absolute right-0 top-full mt-1 w-48 overflow-hidden rounded-md border border-border bg-surface py-1 shadow-md">
          {quickLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              onClick={() => setOpen(false)}
              className="block px-3 py-2 text-left text-sm text-ink hover:bg-border/30"
            >
              {link.label}
            </Link>
          ))}
          {quickLinks.length > 0 && <div className="my-1 border-t border-border" />}
          <Link
            href="/settings"
            onClick={() => setOpen(false)}
            className="block px-3 py-2 text-left text-sm text-ink hover:bg-border/30"
          >
            {t("nav.changePassword")}
          </Link>
          <button
            type="button"
            onClick={() => {
              setOpen(false);
              logout();
              router.push("/login");
            }}
            className="block w-full px-3 py-2 text-left text-sm text-danger hover:bg-border/30"
          >
            {t("nav.logout")}
          </button>
        </div>
      )}
    </div>
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
            authenticated reads as being asked to log in again. This
            is also now the ONLY way to reach the dashboard — a
            separate "Dashboard" text link next to it was pure
            duplication of the exact same destination. */}
        <Link
          href={user ? "/dashboard" : "/"}
          className="font-display text-lg font-semibold text-ink"
        >
          {t("nav.brand")}
        </Link>
        <div className="flex items-center gap-1 text-sm text-ink sm:gap-2">
          <Link href="/careers" className="rounded-md px-2 py-1.5 hover:bg-border/30">
            {t("nav.careers")}
          </Link>
          <Link href="/courses" className="rounded-md px-2 py-1.5 hover:bg-border/30">
            {t("nav.courses")}
          </Link>
          <Link href="/about" className="rounded-md px-2 py-1.5 hover:bg-border/30">
            {t("nav.aboutUs")}
          </Link>
          {user?.role === "admin" && (
            <Link href="/admin" className="rounded-md px-2 py-1.5 hover:bg-border/30">
              {t("nav.admin")}
            </Link>
          )}
          {user && (
            <Link
              href="/announcements"
              className="rounded-md p-2 hover:bg-border/30"
              aria-label={t("nav.announcements")}
              title={t("nav.announcements")}
            >
              <Bell size={16} />
            </Link>
          )}
          {!user && (
            <Link href="/login" className="rounded-md px-2 py-1.5 hover:bg-border/30">
              {t("nav.login")}
            </Link>
          )}
          {/* Admin's own Settings stays a plain link, unchanged — its
              nav is already short; everyone else gets the dropdown
              that also holds what used to be permanent nav links. */}
          {user?.role === "admin" && (
            <Link href="/settings" className="rounded-md px-2 py-1.5 hover:bg-border/30">
              {t("nav.settings")}
            </Link>
          )}
          {user && user.role !== "admin" && <SettingsDropdown />}

          <div className="ml-1 flex items-center gap-1 border-l border-border pl-2">
            <LanguagePicker />
            <ThemeToggle />
          </div>
        </div>
      </div>
    </nav>
  );
}
