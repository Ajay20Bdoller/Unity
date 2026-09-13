"use client";

import { createContext, useContext, useEffect, useState } from "react";
import en from "./i18n/en.json";
import hi from "./i18n/hi.json";
import bn from "./i18n/bn.json";
import te from "./i18n/te.json";
import pa from "./i18n/pa.json";

export const SUPPORTED_LANGUAGES = [
  { code: "en", name: "English", native_name: "English" },
  { code: "hi", name: "Hindi", native_name: "हिन्दी" },
  { code: "bn", name: "Bengali", native_name: "বাংলা" },
  { code: "te", name: "Telugu", native_name: "తెలుగు" },
  { code: "pa", name: "Punjabi", native_name: "ਪੰਜਾਬੀ" },
] as const;

export type LanguageCode = (typeof SUPPORTED_LANGUAGES)[number]["code"];

type Dictionary = typeof en;
const DICTIONARIES: Record<LanguageCode, Dictionary> = { en, hi, bn, te, pa };

interface LanguageContextValue {
  language: LanguageCode;
  setLanguage: (code: LanguageCode, persist?: (code: string) => Promise<unknown>) => void;
  t: (path: string) => string;
}

const LanguageContext = createContext<LanguageContextValue | undefined>(undefined);

function lookup(dict: Dictionary, path: string): string | undefined {
  const parts = path.split(".");
  let node: unknown = dict;
  for (const part of parts) {
    if (typeof node !== "object" || node === null) return undefined;
    node = (node as Record<string, unknown>)[part];
  }
  return typeof node === "string" ? node : undefined;
}

export function LanguageProvider({ children }: { children: React.ReactNode }) {
  const [language, setLanguageState] = useState<LanguageCode>("en");

  useEffect(() => {
    const stored = localStorage.getItem("language");
    if (stored && stored in DICTIONARIES) {
      setLanguageState(stored as LanguageCode);
    }
  }, []);

  function setLanguage(code: LanguageCode, persist?: (code: string) => Promise<unknown>) {
    setLanguageState(code);
    localStorage.setItem("language", code);
    if (persist) {
      persist(code).catch(() => {
        // Best-effort: the UI has already switched language locally even
        // if saving the preference to the account fails.
      });
    }
  }

  function t(path: string): string {
    return (
      lookup(DICTIONARIES[language], path) ?? lookup(DICTIONARIES.en, path) ?? path
    );
  }

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const ctx = useContext(LanguageContext);
  if (!ctx) throw new Error("useLanguage must be used within LanguageProvider");
  return ctx;
}
