"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api, type CourseListItem } from "@/lib/api";
import { Card } from "@/components/ui/card";
import { SiteNav } from "@/components/site-nav";

export default function CoursesPage() {
  const [courses, setCourses] = useState<CourseListItem[] | null>(null);

  useEffect(() => {
    api.courses().then(setCourses).catch(() => setCourses([]));
  }, []);

  return (
    <>
      <SiteNav />
      <main className="mx-auto max-w-5xl px-6 py-10">
        <h1 className="font-display text-2xl font-medium text-ink">Free courses</h1>
        <p className="mt-1 text-sm text-muted">Learn at your own pace, no cost.</p>

        <div className="mt-6 grid gap-4 sm:grid-cols-2">
          {courses === null && <p className="text-sm text-muted">Loading...</p>}
          {courses?.length === 0 && (
            <p className="text-sm text-muted">No courses available yet — check back soon.</p>
          )}
          {courses?.map((course) => (
            <Link key={course.id} href={`/courses/${course.slug}`}>
              <Card className="h-full transition-shadow hover:shadow-sm">
                <h2 className="font-medium text-ink">{course.title}</h2>
                <p className="mt-2 text-sm text-muted line-clamp-3">{course.description}</p>
              </Card>
            </Link>
          ))}
        </div>
      </main>
    </>
  );
}
