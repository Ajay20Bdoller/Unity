// Static on purpose: registration used to fetch states from the
// backend (GET /states), which meant a slow cold start, a transient
// network blip, or a CORS misconfiguration could leave this REQUIRED
// dropdown empty and block registration entirely. States and
// countries are both small, essentially-never-changing lists, so
// there's no real benefit to fetching them live -- only a real risk.
// This list matches exactly what's seeded in the backend (migration
// 0012) for consistency, even though nothing here reads from the API
// anymore.
export const INDIAN_STATES = [
  "Andhra Pradesh",
  "Arunachal Pradesh",
  "Assam",
  "Bihar",
  "Chhattisgarh",
  "Goa",
  "Gujarat",
  "Haryana",
  "Himachal Pradesh",
  "Jharkhand",
  "Karnataka",
  "Kerala",
  "Madhya Pradesh",
  "Maharashtra",
  "Manipur",
  "Meghalaya",
  "Mizoram",
  "Nagaland",
  "Odisha",
  "Punjab",
  "Rajasthan",
  "Sikkim",
  "Tamil Nadu",
  "Telangana",
  "Tripura",
  "Uttar Pradesh",
  "Uttarakhand",
  "West Bengal",
  "Andaman and Nicobar Islands",
  "Chandigarh",
  "Dadra and Nagar Haveli and Daman and Diu",
  "Delhi",
  "Jammu and Kashmir",
  "Ladakh",
  "Lakshadweep",
  "Puducherry",
] as const;

// A short, commonly-needed list rather than all ~195 countries --
// this platform is India-focused (see CLAUDE.md), so India is first
// and the rest cover where students/mentors/parents realistically are.
// "Other" lets anyone not covered still complete the form.
export const COUNTRIES = [
  "India",
  "United States",
  "United Kingdom",
  "Canada",
  "Australia",
  "United Arab Emirates",
  "Saudi Arabia",
  "Singapore",
  "Germany",
  "Other",
] as const;
