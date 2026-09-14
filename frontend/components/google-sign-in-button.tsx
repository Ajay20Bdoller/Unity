"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { api, ApiError } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";

// Google Identity Services attaches itself to window.google at
// runtime once the script below loads — there's no official npm
// package with types for this, so a minimal shape is declared here
// rather than pulling in `any` everywhere it's used.
interface GoogleCredentialResponse {
  credential: string;
}
declare global {
  interface Window {
    google?: {
      accounts: {
        id: {
          initialize: (config: {
            client_id: string;
            callback: (response: GoogleCredentialResponse) => void;
          }) => void;
          renderButton: (
            parent: HTMLElement,
            options: { theme?: string; size?: string; width?: number; text?: string }
          ) => void;
        };
      };
    };
  }
}

const SCRIPT_SRC = "https://accounts.google.com/gsi/client";

function loadGoogleScript(): Promise<void> {
  if (window.google?.accounts?.id) return Promise.resolve();
  const existing = document.querySelector(`script[src="${SCRIPT_SRC}"]`);
  if (existing) {
    return new Promise((resolve) => existing.addEventListener("load", () => resolve()));
  }
  return new Promise((resolve, reject) => {
    const script = document.createElement("script");
    script.src = SCRIPT_SRC;
    script.async = true;
    script.defer = true;
    script.onload = () => resolve();
    script.onerror = () => reject(new Error("Failed to load Google Sign-In"));
    document.body.appendChild(script);
  });
}

export function GoogleSignInButton() {
  const router = useRouter();
  const { loginWithGoogle } = useAuth();
  const containerRef = useRef<HTMLDivElement>(null);
  const [enabled, setEnabled] = useState<boolean | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function handleCredential(response: GoogleCredentialResponse) {
      setError(null);
      try {
        const outcome = await loginWithGoogle(response.credential);
        if (outcome.status === "new_user") {
          // Google can't supply the role-specific fields every role
          // here requires (mobile number at minimum, more for
          // students) — hand off to registration with identity
          // pre-filled instead of trying to skip it.
          const params = new URLSearchParams({
            google_id: outcome.google_id ?? "",
            email: outcome.email ?? "",
            name: outcome.full_name ?? "",
          });
          router.push(`/register?${params.toString()}`);
        }
        // "logged_in": loginWithGoogle already navigated to /dashboard.
      } catch (err) {
        setError(err instanceof ApiError ? err.message : "Google sign-in failed.");
      }
    }

    api
      .googleAuthConfig()
      .then(async (config) => {
        if (cancelled) return;
        setEnabled(config.enabled && !!config.client_id);
        if (!config.enabled || !config.client_id) return;
        await loadGoogleScript();
        if (cancelled || !window.google || !containerRef.current) return;
        window.google.accounts.id.initialize({
          client_id: config.client_id,
          callback: handleCredential,
        });
        window.google.accounts.id.renderButton(containerRef.current, {
          theme: "outline",
          size: "large",
          width: 320,
          text: "continue_with",
        });
      })
      .catch(() => setEnabled(false));

    return () => {
      cancelled = true;
    };
  }, [router, loginWithGoogle]);

  if (enabled === false) return null;

  return (
    <div className="flex flex-col items-center gap-2">
      <div ref={containerRef} />
      {error && <p className="text-xs text-danger">{error}</p>}
    </div>
  );
}
