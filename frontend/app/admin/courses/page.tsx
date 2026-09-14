"use client";

import { useEffect, useState } from "react";
import {
  api,
  ApiError,
  type AdminCourse,
  type AdminCourseDetail,
  type LessonContentType,
} from "@/lib/api";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

const CONTENT_TYPES: { value: LessonContentType; label: string }[] = [
  { value: "article", label: "Article (write the text directly)" },
  { value: "external_resource", label: "External resource (link out)" },
  { value: "video", label: "Video (link)" },
  { value: "quiz", label: "Quiz" },
];

function AddModuleForm({ courseId, onAdded }: { courseId: string; onAdded: () => void }) {
  const [title, setTitle] = useState("");
  async function add() {
    if (!title) return;
    await api.adminAddModule(courseId, { title, display_order: 0 });
    setTitle("");
    onAdded();
  }
  return (
    <div className="flex gap-2">
      <Input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="New module title" />
      <Button variant="secondary" disabled={!title} onClick={add}>
        + Module
      </Button>
    </div>
  );
}

function AddLessonForm({ moduleId, onAdded }: { moduleId: string; onAdded: () => void }) {
  const [title, setTitle] = useState("");
  const [contentType, setContentType] = useState<LessonContentType>("article");
  const [contentUrl, setContentUrl] = useState("");
  const [contentBody, setContentBody] = useState("");
  const [error, setError] = useState<string | null>(null);

  const needsUrl = contentType === "external_resource" || contentType === "video";
  const needsBody = contentType === "article" || contentType === "quiz";

  async function add() {
    setError(null);
    try {
      await api.adminAddLesson(moduleId, {
        title,
        content_type: contentType,
        content_url: needsUrl ? contentUrl : undefined,
        content_body: needsBody ? contentBody : undefined,
        display_order: 0,
      });
      setTitle("");
      setContentUrl("");
      setContentBody("");
      onAdded();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong.");
    }
  }

  return (
    <div className="mt-2 rounded-md border border-border p-3">
      <div className="grid gap-2 sm:grid-cols-2">
        <Input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Lesson title" />
        <select
          value={contentType}
          onChange={(e) => setContentType(e.target.value as LessonContentType)}
          className="rounded-md border border-border bg-surface px-3 py-2 text-sm text-ink"
        >
          {CONTENT_TYPES.map((c) => (
            <option key={c.value} value={c.value}>
              {c.label}
            </option>
          ))}
        </select>
      </div>
      {needsUrl && (
        <Input
          className="mt-2"
          value={contentUrl}
          onChange={(e) => setContentUrl(e.target.value)}
          placeholder={
            contentType === "external_resource"
              ? "https://... (the external link students will open)"
              : "https://... (video link)"
          }
        />
      )}
      {needsBody && (
        <textarea
          className="mt-2 w-full rounded-md border border-border bg-surface p-3 text-sm text-ink"
          rows={4}
          value={contentBody}
          onChange={(e) => setContentBody(e.target.value)}
          placeholder="Lesson content..."
        />
      )}
      {error && <p className="mt-1 text-xs text-danger">{error}</p>}
      <Button
        variant="secondary"
        className="mt-2"
        disabled={!title || (needsUrl && !contentUrl) || (needsBody && !contentBody)}
        onClick={add}
      >
        + Lesson
      </Button>
    </div>
  );
}

function CourseEditor({ courseId }: { courseId: string }) {
  const [detail, setDetail] = useState<AdminCourseDetail | null>(null);

  function load() {
    api.adminCourseDetail(courseId).then(setDetail).catch(() => setDetail(null));
  }
  useEffect(load, [courseId]);

  if (!detail) return <p className="mt-3 text-sm text-muted">Loading...</p>;

  return (
    <div className="mt-3 space-y-3 border-t border-border pt-3">
      {detail.modules.map((m) => (
        <div key={m.id} className="rounded-md bg-background p-3">
          <p className="text-sm font-medium text-ink">{m.title}</p>
          <ul className="mt-2 space-y-1">
            {m.lessons.map((l) => (
              <li key={l.id} className="text-xs text-muted">
                {l.title} — {l.content_type}
                {l.content_url && (
                  <>
                    {" "}
                    (
                    <a href={l.content_url} target="_blank" rel="noreferrer" className="text-primary underline">
                      link
                    </a>
                    )
                  </>
                )}
              </li>
            ))}
            {m.lessons.length === 0 && <li className="text-xs text-muted">No lessons yet.</li>}
          </ul>
          <AddLessonForm moduleId={m.id} onAdded={load} />
        </div>
      ))}
      <AddModuleForm courseId={courseId} onAdded={load} />
    </div>
  );
}

export default function AdminCoursesPage() {
  const [courses, setCourses] = useState<AdminCourse[]>([]);
  const [slug, setSlug] = useState("");
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [expanded, setExpanded] = useState<string | null>(null);

  function load() {
    api.adminCourses().then(setCourses).catch(() => setCourses([]));
  }

  useEffect(load, []);

  async function create() {
    setError(null);
    try {
      await api.adminCreateCourse({ slug, title, description });
      setSlug("");
      setTitle("");
      setDescription("");
      load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong.");
    }
  }

  async function togglePublish(course: AdminCourse) {
    await api.adminUpdateCourse(course.id, { published: !course.published });
    load();
  }

  return (
    <div>
      <h1 className="font-display text-xl font-medium text-ink">Courses</h1>
      {error && <p className="mt-2 text-sm text-danger">{error}</p>}

      <Card className="mt-4">
        <h2 className="font-medium text-ink">New course</h2>
        <div className="mt-2 space-y-2">
          <Input value={slug} onChange={(e) => setSlug(e.target.value)} placeholder="slug" />
          <Input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Title" />
          <Input
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Description"
          />
          <Button disabled={!slug || !title || !description} onClick={create}>
            Add course (as draft)
          </Button>
        </div>
      </Card>

      <div className="mt-6 space-y-2">
        {courses.map((c) => (
          <Card key={c.id}>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-ink">{c.title}</p>
                <p className="text-xs text-muted">{c.published ? "published" : "draft"}</p>
              </div>
              <div className="flex gap-2">
                <Button
                  variant="secondary"
                  onClick={() => setExpanded(expanded === c.id ? null : c.id)}
                >
                  {expanded === c.id ? "Hide content" : "Manage content"}
                </Button>
                <Button variant="secondary" onClick={() => togglePublish(c)}>
                  {c.published ? "Unpublish" : "Publish"}
                </Button>
              </div>
            </div>
            {expanded === c.id && <CourseEditor courseId={c.id} />}
          </Card>
        ))}
      </div>
    </div>
  );
}
