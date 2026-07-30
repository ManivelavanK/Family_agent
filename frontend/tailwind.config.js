/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      colors: {
        agent: {
          father: '#3b82f6',
          mother: '#ec4899',
          children: '#f59e0b',
          grandparent: '#10b981',
          baby: '#8b5cf6',
          planner: '#6366f1',
        }
      }
    },
  },
  plugins: [],
}
