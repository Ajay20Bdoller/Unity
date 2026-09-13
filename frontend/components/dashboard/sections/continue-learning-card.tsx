"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api, type ContinueLearningItem } from "@/lib/api";
import { Card } from "@/components/ui/card";

export function ContinueLearningCard() {
  const [items, setItems] = useState<ContinueLearningItem[] | null>(null);

  useEffect(() => {
    api.continueLearning().then(setItems).catch(() => setItems([]));
  }, []);

  if (items === null) return null;
  if (items.length === 0) {
    return (
      <Card>
        <h2 className="font-medium text-ink">Continue learning</h2>
        <p className="mt-2 text-sm text-muted">
          You haven&apos;t enrolled in a course yet.{" "}
          <Link href="/courses" className="text-primary hover:underline">
            Browse courses
          </Link>
        </p>
      </Card>
    );
  }

  return (
    <Card>
      <h2 className="font-medium text-ink">Continue learning</h2>
      <div className="mt-3 space-y-3">
        {items.map((item) => (
          <Link
            key={item.course.id}
            href={`/courses/${item.course.slug}`}
            className="block rounded-md border border-border p-3 hover:bg-border/20"
          >
            <div className="flex items-center justify-between">
              <p className="text-sm font-medium text-ink">{item.course.title}</p>
              <span className="text-xs text-muted">{item.progress_percent}%</span>
            </div>
            <div className="mt-2 h-1.5 w-full rounded-full bg-border">
              <div
                className="h-1.5 rounded-full bg-primary"
                style={{ width: `${item.progress_percent}%` }}
              />
            </div>
            {item.next_lesson && (
              <p className="mt-2 text-xs text-muted">Next: {item.next_lesson.title}</p>
            )}
          </Link>
        ))}
      </div>
    </Card>
  );
}
