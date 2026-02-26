/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,jsx,ts,tsx}",
    "./components/**/*.{js,jsx,ts,tsx}",
  ],
  presets: [require("nativewind/preset")],
  theme: {
    extend: {
      colors: {
        affirm: {
          blue: "#3B6BF5",
          "blue-light": "#E8EEFF",
          mint: "#34C77B",
          "mint-light": "#E6F9EF",
          amber: "#E5A83B",
          "amber-light": "#FFF6E5",
          bg: "#F8FAFB",
          surface: "#FFFFFF",
          text: "#1A1D23",
          "text-secondary": "#6B7280",
          "text-tertiary": "#9CA3AF",
          border: "#E5E7EB",
        },
      },
      fontFamily: {
        sans: ["Inter", "System"],
      },
    },
  },
  plugins: [],
};
