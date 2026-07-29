/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        navy:    { dark: '#0B1F33', med: '#102A43', light: '#1E3A5F' },
        brand:   { indigo: '#6366F1', purple: '#7C3AED', gold: '#D4A72C' },
        surface: '#FFFFFF',
        bg:      '#F7F9FC',
        border:  '#D9E2EC',
        textMain:'#172B4D',
      },
      fontFamily: {
        sans: ['Plus Jakarta Sans', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        glow:    '0 0 20px rgba(99,102,241,0.4)',
        'glow-lg':'0 0 40px rgba(99,102,241,0.3)',
        card:    '0 2px 12px rgba(17,24,39,0.06)',
        'card-hover': '0 8px 28px rgba(99,102,241,0.14)',
      },
      backgroundImage: {
        'gradient-indigo': 'linear-gradient(135deg, #6366F1 0%, #7C3AED 100%)',
        'gradient-navy':   'linear-gradient(135deg, #0B1F33 0%, #102A43 100%)',
        'gradient-radial-indigo': 'radial-gradient(ellipse at center, rgba(99,102,241,0.15) 0%, transparent 70%)',
      },
      keyframes: {
        'float':       { '0%,100%': { transform:'translateY(0px)' }, '50%': { transform:'translateY(-10px)' } },
        'pulse-soft':  { '0%,100%': { opacity:'1', transform:'scale(1)' }, '50%': { opacity:'0.7', transform:'scale(1.06)' } },
        'spin-slow':   { '0%': { transform:'rotate(0deg)' }, '100%': { transform:'rotate(360deg)' } },
        'shimmer':     { '0%': { backgroundPosition:'200% 0' }, '100%': { backgroundPosition:'-200% 0' } },
        'fade-in':     { '0%': { opacity:'0', transform:'translateY(10px)' }, '100%': { opacity:'1', transform:'translateY(0)' } },
        'slide-in-left': { '0%': { opacity:'0', transform:'translateX(-20px)' }, '100%': { opacity:'1', transform:'translateX(0)' } },
        'scale-in':    { '0%': { opacity:'0', transform:'scale(0.94)' }, '100%': { opacity:'1', transform:'scale(1)' } },
      },
      animation: {
        'float':        'float 4s ease-in-out infinite',
        'pulse-soft':   'pulse-soft 2.5s ease-in-out infinite',
        'spin-slow':    'spin-slow 8s linear infinite',
        'shimmer':      'shimmer 1.5s infinite',
        'fade-in':      'fade-in 0.4s ease-out',
        'slide-in-left':'slide-in-left 0.4s ease-out',
        'scale-in':     'scale-in 0.3s ease-out',
      },
    },
  },
  plugins: [],
}
