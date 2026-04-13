/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        dark: "#0f172a",
        primary: "#4facfe",
        secondary: "#a18cd1",
      },
      fontFamily: {
        sans: ['Inter', 'Poppins', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
