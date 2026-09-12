import type { ComponentType } from "react";
import { WelcomeSummary } from "./sections/welcome-summary";
import { AIAssistantCard } from "./sections/ai-assistant-card";

/**
 * The backend's `dashboard_sections.component_key` picks an entry here.
 * An unknown key must never crash the page — it's just skipped (see
 * DashboardSections below). New sections mean adding a new component
 * AND a new registry entry in the same change; the DB can toggle/order/
 * configure these, it can never introduce a new one.
 */
export const SECTION_REGISTRY: Record<string, ComponentType> = {
  welcome_summary: WelcomeSummary,
  ai_assistant_card: AIAssistantCard,
};
