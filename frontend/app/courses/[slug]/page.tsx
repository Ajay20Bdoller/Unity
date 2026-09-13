"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { api, ApiError, type CourseDetail, type CourseDetailWithProgress } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { SiteNav } from "@/components/site-nav";

function isProgressCourse(
  c: CourseDetail | CourseDetailWithProgress
): c is CourseDetailWithProgress {
  return "enrolled" in c;
}

export default function CourseDetailPage() {
  const { slug } = useParams<{ slug: string }>();
  const { user } = useAuth();
  const [course, setCourse] = useState<CourseDetail | CourseDetailWithProgress | null>(null);
  const [notFound, setNotFound] = useState(false);
  const [busyLessonId, setBusyLessonId] = useState<string | null>(null);
  const [enrolling, setEnrolling] = useState(false);

  function load() {
    const fetcher = user?.role === "student" ? api.courseWithMyProgress(slug) : api.course(slug);
    fetcher
      .then(setCourse)
      .catch((err) => {
        if (err instanceof ApiError && err.status === 404) setNotFound(true);
      });
  }

  useEffect(load, [slug, user?.role]);

  async function handleEnroll() {
    if (!course) return;
    setEnrolling(true);
    try {
      await api.enroll(course.id);
      load();
    } finally {
      setEnrolling(false);
    }
  }

  async function handleComplete(lessonId: string) {
    setBusyLessonId(lessonId);
    try {
      await api.completeLesson(lessonId);
      load();
    } finally {
      setBusyLessonId(null);
    }
  }

  if (notFound) {
    return (
      <>
        <SiteNav />
        <main className="mx-auto max-w-3xl px-6 py-10">
          <p className="text-sm text-muted">Course not found.</p>
        </main>
      </>
    );
  }

  if (!course) {
    return (
      <>
        <SiteNav />
        <main className="mx-auto max-w-3xl px-6 py-10">
          <p className="text-sm text-muted">Loading...</p>
        </main>
      </>
    );
  }

  const withProgress = isProgressCourse(course);

  return (
    <>
      <SiteNav />
      <main className="mx-auto max-w-3xl px-6 py-10">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h1 className="text-2xl font-semibold text-ink">{course.title}</h1>
            <p className="mt-1 text-sm text-muted">{course.description}</p>
          </div>
          {user?.role === "student" && withProgress && !course.enrolled && (
            <Button disabled={enrolling} onClick={handleEnroll}>
              {enrolling ? "Enrolling..." : "Enroll"}
            </Button>
          )}
        </div>

        <div className="mt-6 space-y-4">
          {course.modules.map((module) => (
            <Card key={module.id}>
              <h2 className="font-medium text-ink">{module.title}</h2>
              <ul className="mt-3 space-y-2">
                {module.lessons.map((lesson) => {
                  const completed = "completed" in lesson && lesson.completed;
                  return (
                    <li
                      key={lesson.id}
                      className="flex items-center justify-between rounded-md border border-border px-3 py-2 text-sm"
                    >
                      <div>
                        <span className={completed ? "text-muted line-through" : "text-ink"}>
                          {lesson.title}
                        </span>
                        <span className="ml-2 text-xs uppercase text-muted">
                          {lesson.content_type.replace("_", " ")}
                        </span>
                        {lesson.content_url && (
                          <a
                            href={lesson.content_url}
                            target="_blank"
                            rel="noreferrer"
                            className="ml-2 text-xs text-primary hover:underline"
                          >
                            open
                          </a>
                        )}
                        {lesson.content_body && (
                          <p className="mt-1 text-xs text-muted">{lesson.content_body}</p>
                        )}
                      </div>
                      {user?.role === "student" && withProgress && course.enrolled && !completed && (
                        <Button
                          variant="secondary"
                          disabled={busyLessonId === lesson.id}
                          onClick={() => handleComplete(lesson.id)}
                        >
                          Mark complete
                        </Button>
                      )}
                      {completed && <span className="text-xs text-primary">Done</span>}
                    </li>
                  );
                })}
              </ul>
            </Card>
          ))}
        </div>
      </main>
    </>
  );
}
