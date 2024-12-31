module.exports = {
  content: [
    './src/**/*.{html,js}',
    './components/**/*.{html,js}',
    './templates/**/*.html',
  ],
  theme: {
    extend: {
      colors: {
        green: {
          DEFAULT: '#10B981',
          light: '#6EE7B7',
          dark: '#064E3B',
        },
        dark: {
          background: '#1A202C',
          text: '#E2E8F0',
        },
      },
    },
  },
  plugins: [],
}
