"use client";

import { useEffect, useState } from "react";
import { api, ApiError, type AdminCourse } from "@/lib/api";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export default function AdminCoursesPage() {
  const [courses, setCourses] = useState<AdminCourse[]>([]);
  const [slug, setSlug] = useState("");
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [error, setError] = useState<string | null>(null);

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
          <Card key={c.id} className="flex items-center justify-between py-3">
            <div>
              <p className="text-sm font-medium text-ink">{c.title}</p>
              <p className="text-xs text-muted">{c.published ? "published" : "draft"}</p>
            </div>
            <Button variant="secondary" onClick={() => togglePublish(c)}>
              {c.published ? "Unpublish" : "Publish"}
            </Button>
          </Card>
        ))}
      </div>
    </div>
  );
}
