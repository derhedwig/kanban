module.exports = {
  content: ["./**/*.py", "./*/templates/**/*.html", "./templates/**/*.html"],
  theme: {
    fontFamily: {
      sans: ["InterVariable", "sans-serif"],
    },
    extend: {
      colors: {
        background: "#F8F8F2",
        green: {
          50: "#fcfefb",
          100: "#f6fff1",
          200: "#d8f2d8",
          300: "#aee1a5",
          400: "#81c155",
          500: "#3a9d00",
          600: "#308701",
          700: "#2b7b03",
          800: "#236707",
          900: "#1a4614"
        },
      },
    },
  },
  plugins: [require('@tailwindcss/forms')],
}
