/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        navy: {
          50:  "#eef2f7",
          100: "#d5e0ed",
          200: "#abbfdb",
          300: "#7d9dc6",
          400: "#527aaf",
          500: "#2e5a96",
          600: "#1e3a5f",
          700: "#172d4a",
          800: "#102035",
          900: "#091422",
        },
        gold: {
          50:  "#fdf8ec",
          100: "#f9edcc",
          200: "#f2d98a",
          300: "#e8c04a",
          400: "#c9a84c",
          500: "#b8922e",
          600: "#9a7520",
          700: "#7a5a18",
        },
      },
      fontFamily: {
        sans: ["Inter", "IBM Plex Sans", "Source Sans Pro", "system-ui", "sans-serif"],
      },
      boxShadow: {
        card:  "0 1px 3px 0 rgba(30,58,95,0.08), 0 1px 2px -1px rgba(30,58,95,0.06)",
        "card-hover": "0 8px 24px -4px rgba(30,58,95,0.14), 0 4px 8px -2px rgba(30,58,95,0.08)",
        nav:   "0 2px 12px 0 rgba(30,58,95,0.18)",
      },
      borderRadius: {
        "2xl": "1rem",
        "3xl": "1.5rem",
      },
    },
  },
  plugins: [],
};
