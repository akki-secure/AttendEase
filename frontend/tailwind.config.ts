import type { Config } from "tailwindcss"

export default {
  content: [
    "./components/**/*.{js,vue,ts}",
    "./layouts/**/*.vue",
    "./pages/**/*.vue",
    "./composables/**/*.{js,ts}",
    "./plugins/**/*.{js,ts}",
    "./app.vue",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50:  "#edf8fb",
          100: "#d1eef5",
          200: "#a4dcea",
          300: "#76c9de",
          400: "#62b8cd",
          500: "#4ca5bd",
          600: "#3d8ea4",
          700: "#2e7288",
          800: "#1f5a6e",
        },
      },
    },
  },
} satisfies Config
