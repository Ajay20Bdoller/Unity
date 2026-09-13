const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

// Access tokens are short-lived (15 min). Rather than making every
// caller think about expiry, a 401 triggers one silent refresh attempt
// (via the httpOnly refresh_token cookie) and a single retry. If refresh
// also fails, the error surfaces normally and callers redirect to login
// as before. Concurrent 401s share one in-flight refresh call.
let refreshInFlight: Promise<boolean> | null = null;

function attemptRefresh(): Promise<boolean> {
  if (!refreshInFlight) {
    refreshInFlight = fetch(`${API_URL}/auth/refresh`, {
      method: "POST",
      credentials: "include",
    })
      .then((res) => res.ok)
      .catch(() => false)
      .finally(() => {
        refreshInFlight = null;
      });
  }
  return refreshInFlight;
}

async function request<T>(
  path: string,
  options: RequestInit = {},
  _isRetry = false
): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });

  if (res.status === 401 && !_isRetry && path !== "/auth/refresh" && path !== "/auth/login") {
    const refreshed = await attemptRefresh();
    if (refreshed) {
      return request<T>(path, options, true);
    }
  }

  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail ?? detail;
    } catch {
      // response had no JSON body
    }
    throw new ApiError(res.status, detail);
  }

  if (res.status === 204) {
    return undefined as T;
  }
  return res.json() as Promise<T>;
}

export type UserRole = "student" | "parent" | "mentor" | "school_admin" | "admin";

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  preferred_language: string;
  is_active: boolean;
  created_at: string;
}

export interface RegisterInput {
  email: string;
  password: string;
  full_name: string;
  role: UserRole;
}

export interface DashboardSection {
  key: string;
  component_key: string;
  name: string;
  config: Record<string, unknown>;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface AIChatResponse {
  answer: string;
  provider: string;
}

export interface CareerCategory {
  id: string;
  key: string;
  name: string;
  description: string | null;
  display_order: number;
}

export interface CareerListItem {
  id: string;
  slug: string;
  title: string;
  description: string;
  category_key: string;
}

export interface CareerDetail {
  id: string;
  slug: string;
  title: string;
  description: string;
  eligibility: string | null;
  subjects: string[] | null;
  skills: string[] | null;
  entrance_exams: string[] | null;
  education_pathway: string | null;
  roadmap: string | null;
  category: CareerCategory;
  related_careers: CareerListItem[];
  language: string;
}

export type LessonContentType = "video" | "article" | "quiz" | "external_resource";

export interface Lesson {
  id: string;
  title: string;
  content_type: LessonContentType;
  content_url: string | null;
  content_body: string | null;
  display_order: number;
}

export interface Module {
  id: string;
  title: string;
  display_order: number;
  lessons: Lesson[];
}

export interface CourseListItem {
  id: string;
  slug: string;
  title: string;
  description: string;
  thumbnail_url: string | null;
}

export interface CourseDetail extends CourseListItem {
  modules: Module[];
  language: string;
}

export interface LessonWithProgress extends Lesson {
  completed: boolean;
}

export interface ModuleWithProgress {
  id: string;
  title: string;
  display_order: number;
  lessons: LessonWithProgress[];
}

export interface CourseDetailWithProgress extends CourseListItem {
  modules: ModuleWithProgress[];
  enrolled: boolean;
}

export interface Enrollment {
  course: CourseListItem;
  enrolled_at: string;
  total_lessons: number;
  completed_lessons: number;
  progress_percent: number;
}

export interface ContinueLearningItem {
  course: CourseListItem;
  next_lesson: Lesson | null;
  progress_percent: number;
}

export interface AssessmentSummary {
  id: string;
  title: string;
  description: string;
}

export interface AssessmentOption {
  value: string;
  label: string;
}

export interface AssessmentQuestion {
  id: string;
  question_text: string;
  options: AssessmentOption[];
  display_order: number;
}

export interface SuggestedCategory {
  key: string;
  name: string;
}

export interface AssessmentResult {
  id: string;
  assessment_id: string;
  suggested_categories: SuggestedCategory[];
  submitted_at: string;
  note: string;
}

export const api = {
  register: (input: RegisterInput) =>
    request<User>("/auth/register", {
      method: "POST",
      body: JSON.stringify(input),
    }),
  login: (email: string, password: string) =>
    request<{ access_token: string }>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),
  logout: () => request<void>("/auth/logout", { method: "POST" }),
  me: () => request<User>("/auth/me"),
  updateLanguage: (preferred_language: string) =>
    request<User>("/users/me/language", {
      method: "PATCH",
      body: JSON.stringify({ preferred_language }),
    }),
  dashboardSections: () => request<DashboardSection[]>("/dashboard/sections"),
  aiChat: (message: string, history?: ChatMessage[]) =>
    request<AIChatResponse>("/ai/chat", {
      method: "POST",
      body: JSON.stringify({ message, history }),
    }),

  // careers
  careerCategories: () => request<CareerCategory[]>("/careers/categories"),
  careers: (params?: { category?: string; q?: string }) => {
    const qs = new URLSearchParams();
    if (params?.category) qs.set("category", params.category);
    if (params?.q) qs.set("q", params.q);
    const suffix = qs.toString() ? `?${qs.toString()}` : "";
    return request<CareerListItem[]>(`/careers${suffix}`);
  },
  career: (slug: string, lang?: string) =>
    request<CareerDetail>(`/careers/${slug}${lang ? `?lang=${lang}` : ""}`),
  myCareerInterests: () => request<CareerListItem[]>("/students/me/career-interests"),
  addCareerInterest: (careerId: string) =>
    request<void>(`/students/me/career-interests/${careerId}`, { method: "POST" }),
  removeCareerInterest: (careerId: string) =>
    request<void>(`/students/me/career-interests/${careerId}`, { method: "DELETE" }),

  // courses
  courses: () => request<CourseListItem[]>("/courses"),
  course: (slug: string) => request<CourseDetail>(`/courses/${slug}`),
  courseWithMyProgress: (slug: string) =>
    request<CourseDetailWithProgress>(`/students/me/courses/${slug}`),
  myEnrollments: () => request<Enrollment[]>("/students/me/enrollments"),
  enroll: (courseId: string) =>
    request<void>(`/students/me/enrollments/${courseId}`, { method: "POST" }),
  completeLesson: (lessonId: string) =>
    request<void>(`/students/me/lessons/${lessonId}/complete`, { method: "POST" }),
  continueLearning: () => request<ContinueLearningItem[]>("/students/me/continue-learning"),

  // assessment
  assessments: () => request<AssessmentSummary[]>("/assessments"),
  assessmentQuestions: (assessmentId: string) =>
    request<AssessmentQuestion[]>(`/assessments/${assessmentId}/questions`),
  submitAssessment: (
    assessmentId: string,
    responses: { question_id: string; selected_option_value: string }[]
  ) =>
    request<AssessmentResult>(`/students/me/assessments/${assessmentId}/submit`, {
      method: "POST",
      body: JSON.stringify({ responses }),
    }),
  myAssessmentResults: (assessmentId: string) =>
    request<AssessmentResult[]>(`/students/me/assessments/${assessmentId}/results`),
};
