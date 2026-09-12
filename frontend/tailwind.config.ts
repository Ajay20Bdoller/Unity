import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        background: "#F7F5F1",
        ink: "#1F2421",
        muted: "#6B7570",
        border: "#E1DDD3",
        primary: {
          DEFAULT: "#1E6F5C",
          foreground: "#FFFFFF",
        },
        accent: {
          DEFAULT: "#E8A33D",
          foreground: "#1F2421",
        },
        danger: "#C24A3F",
      },
      fontFamily: {
        sans: ["var(--font-manrope)", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};

export default config;
