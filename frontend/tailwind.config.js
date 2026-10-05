/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#0B1220",
        card: "#111827",
        border: "#1F2937",
        primary: "#3B82F6",
        success: "#22C55E",
        warning: "#F59E0B",
        danger: "#EF4444",
        text: "#F8FAFC",
        mutedText: "#94A3B8",
      },
      fontFamily: {
        sans: ["Inter", "sans-serif"],
        brand: ["'Abril Fatface'", "serif"],
      },
    },
  },
  plugins: [],
}
