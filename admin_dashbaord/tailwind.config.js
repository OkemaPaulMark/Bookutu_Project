/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      boxShadow: {
        card: '0 12px 24px rgba(20, 30, 50, 0.08)'
      }
    }
  },
  plugins: []
}
