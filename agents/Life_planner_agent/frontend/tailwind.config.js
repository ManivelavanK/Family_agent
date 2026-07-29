/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        kinnest: {
          navy: '#0A0E1A',
          card: '#12192C',
          lightNavy: '#1D263B',
          indigo: '#5D5FEF',
          purple: '#9B51E0',
          softWhite: '#F2F4F7',
          gray: '#828282'
        }
      }
    },
  },
  plugins: [],
}
