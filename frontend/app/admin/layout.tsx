"use client";

import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import { SiteNav } from "@/components/site-nav";

const ADMIN_LINKS = [
  { href: "/admin/users", label: "Users" },
  { href: "/admin/careers", label: "Careers" },
  { href: "/admin/courses", label: "Courses" },
  { href: "/admin/assessments", label: "Assessments" },
  { href: "/admin/campaigns", label: "Campaigns" },
  { href: "/admin/announcements", label: "Announcements" },
  { href: "/admin/dashboard-sections", label: "Dashboard sections" },
];

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();

  if (loading) return null;

  if (!user || user.role !== "admin") {
    return (
      <>
        <SiteNav />
        <main className="mx-auto max-w-2xl px-6 py-10">
          <p className="text-sm text-muted">This area is available to admins only.</p>
        </main>
      </>
    );
  }

  return (
    <>
      <SiteNav />
      <div className="mx-auto flex max-w-6xl gap-8 px-6 py-10">
        <aside className="w-48 shrink-0">
          <nav className="space-y-1">
            {ADMIN_LINKS.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className="block rounded-md px-3 py-2 text-sm text-ink hover:bg-border/30"
              >
                {link.label}
              </Link>
            ))}
          </nav>
        </aside>
        <div className="flex-1">{children}</div>
      </div>
    </>
  );
}
