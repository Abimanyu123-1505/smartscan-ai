/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'bg-base': '#0d1117',
        'bg-panel': '#161b22',
        'bg-raised': '#1c2128',
        'bg-input': '#0d1117',
        'border-subtle': '#21262d',
        'border-default': '#30363d',
        'text-main': '#e6edf3',
        'text-muted': '#8b949e',
        'text-faint': '#484f58',
        'accent': '#388bfd',
        'accent-dim': '#1f6feb',
        'accent-glow': 'rgba(56, 139, 253, 0.15)',
        'verified': '#3fb950',
        'amber-warn': '#d29922',
        'critical': '#f85149',
        'info': '#58a6ff',
        'purple-ai': '#bc8cff',
        'teal-timeline': '#39d353',
        'orange-net': '#e3b341',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Courier New', 'monospace'],
        display: ['Space Grotesk', 'Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
