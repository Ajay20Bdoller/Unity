"use client";

import { useEffect, useRef } from "react";
import { useAuth } from "@/lib/auth-context";
import { useLanguage, SUPPORTED_LANGUAGES, type LanguageCode } from "@/lib/language-context";

export function LanguageSync() {
  const { user } = useAuth();
  const { setLanguage } = useLanguage();
  const synced = useRef(false);

  useEffect(() => {
    if (synced.current || !user) return;
    const hasLocalChoice = typeof window !== "undefined" && localStorage.getItem("language");
    if (hasLocalChoice) {
      synced.current = true;
      return;
    }
    const accountLanguage = SUPPORTED_LANGUAGES.find((l) => l.code === user.preferred_language);
    if (accountLanguage) {
      setLanguage(accountLanguage.code as LanguageCode);
    }
    synced.current = true;
  }, [user, setLanguage]);

  return null;
}
