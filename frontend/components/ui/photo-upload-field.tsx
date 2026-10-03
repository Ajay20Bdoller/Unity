"use client";

import { useRef, useState } from "react";
import { api, ApiError } from "@/lib/api";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { toDirectImageUrl } from "@/lib/image-url";

export function PhotoUploadField({
  value,
  onChange,
  previewClassName = "h-20 w-20 rounded-full",
}: {
  value: string;
  onChange: (url: string) => void;
  previewClassName?: string;
}) {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  async function handleFile(file: File | undefined) {
    if (!file) return;
    setError(null);
    setUploading(true);
    try {
      const url = await api.uploadImage(file);
      onChange(url);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Upload failed.");
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  }

  return (
    <div>
      {value && (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src={toDirectImageUrl(value)}
          alt=""
          className={`mb-2 border border-border object-cover ${previewClassName}`}
        />
      )}
      <div className="flex items-center gap-2">
        <input
          ref={fileInputRef}
          type="file"
          accept="image/jpeg,image/png,image/webp,image/gif"
          onChange={(e) => handleFile(e.target.files?.[0])}
          className="hidden"
          id="photo-upload-input"
        />
        <Button
          type="button"
          variant="secondary"
          disabled={uploading}
          onClick={() => fileInputRef.current?.click()}
        >
          {uploading ? "Uploading..." : value ? "Change photo" : "Upload photo"}
        </Button>
        {value && (
          <Button type="button" variant="secondary" onClick={() => onChange("")}>
            Remove
          </Button>
        )}
      </div>
      {error && <p className="mt-1 text-xs text-danger">{error}</p>}
      <details className="mt-2">
        <summary className="cursor-pointer text-xs text-muted">
          Or paste an image URL instead
        </summary>
        <Input
          className="mt-1"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder="https://..."
        />
      </details>
    </div>
  );
}
