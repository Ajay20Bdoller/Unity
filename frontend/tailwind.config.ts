import type { Config } from "tailwindcss";

function withOpacity(variable: string) {
  return `rgb(var(${variable}) / <alpha-value>)`;
}

const config: Config = {
  darkMode: "class",
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        background: withOpacity("--color-background"),
        surface: withOpacity("--color-surface"),
        "surface-raised": withOpacity("--color-surface-raised"),
        ink: withOpacity("--color-ink"),
        muted: withOpacity("--color-muted"),
        border: withOpacity("--color-border"),
        primary: {
          DEFAULT: withOpacity("--color-primary"),
          foreground: withOpacity("--color-primary-foreground"),
        },
        accent: {
          DEFAULT: withOpacity("--color-accent"),
          foreground: withOpacity("--color-accent-foreground"),
        },
        danger: {
          DEFAULT: withOpacity("--color-danger"),
          foreground: withOpacity("--color-danger-foreground"),
        },
      },
      fontFamily: {
        sans: ["var(--font-manrope)", "system-ui", "sans-serif"],
        display: ["var(--font-fraunces)", "Georgia", "serif"],
      },
    },
  },
  plugins: [],
};

export default config;
