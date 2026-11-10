/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        darkBg: "#0f172a",
        cardBg: "#1e293b",
        accentCyan: "#06b6d4",
        accentAmber: "#f59e0b",
      },
    },
  },
  plugins: [],
};
