/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html",
  ],
  theme: {
    extend: {
      colors: {
        // Unitasa Brand Colors
        'unitasa': {
          blue: '#1a365d',
          electric: '#3b82f6',
          purple: '#8b5cf6',
          light: '#f8fafc',
          gray: '#6b7280',
        },
        // Primary brand colors
        primary: '#3b82f6',
        secondary: '#8b5cf6',
        accent: '#1a365d',
      },
      fontFamily: {
        'sans': ['Inter', 'system-ui', 'sans-serif'],
        'display': ['Montserrat', 'system-ui', 'sans-serif'],
      },
      backgroundImage: {
        'gradient-primary': 'linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)',
        'gradient-secondary': 'linear-gradient(135deg, #1a365d 0%, #3b82f6 100%)',
      },
      boxShadow: {
        'brand': '0 4px 14px 0 rgba(59, 130, 246, 0.15)',
        'brand-lg': '0 10px 25px 0 rgba(59, 130, 246, 0.2)',
      },
      animation: {
        'pulse-brand': 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
      },
      keyframes: {
        glow: {
          '0%': { boxShadow: '0 0 5px rgba(59, 130, 246, 0.5)' },
          '100%': { boxShadow: '0 0 20px rgba(59, 130, 246, 0.8)' },
        },
      },
    },
  },
  plugins: [],
}