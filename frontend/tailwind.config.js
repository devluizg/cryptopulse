/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        crypto: {
          dark: '#0d1117',
          darker: '#010409',
          card: '#161b22',
          border: '#30363d',
          text: '#c9d1d9',
          muted: '#8b949e',
        },
        score: {
          high: '#22c55e',
          attention: '#eab308',
          low: '#ef4444',
        },
        btc: '#f7931a',
        eth: '#627eea',
        sol: '#00ffa3',
      },
      fontFamily: {
        sans: ['var(--font-inter)', 'system-ui', 'sans-serif'],
        mono: ['var(--font-mono)', 'monospace'],
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
      },
      keyframes: {
        glow: {
          '0%': { boxShadow: '0 0 5px rgb(34 197 94 / 0.2)' },
          '100%': { boxShadow: '0 0 20px rgb(34 197 94 / 0.4)' },
        },
      },
    },
  },
  plugins: [],
};
