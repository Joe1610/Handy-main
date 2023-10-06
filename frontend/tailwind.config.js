/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: "#683AFF",
        dark: "#302277",
        gold: "#FFE090",
        grey: "#EDEDF7",
      },
      screens: {
        xs: "475px",
      },
      gridTemplateColumns: {
        fluid: "repeat(auto-fit, minmax(20rem, 1fr))",
      },
    },
    screens: {
      sm: "375px",
      // => @media (min-width: 640px) { ... }

      md: "768px",
      // => @media (min-width: 768px) { ... }

      lg: "1024px",
      // => @media (min-width: 1024px) { ... }

      xl: "1280px",
      // => @media (min-width: 1280px) { ... }

      "2xl": "1536px",
      // => @media (min-width: 1536px) { ... }
    },
    plugins: [],
    safelist: [
      {
        pattern: /^bg-/,
      },
      {
        pattern: /^text-/,
      },
      {
        pattern: /^border-/,
      },
      {
        pattern: /^opacity-/,
      },
    ],
  },
  plugins: [require("daisyui")],
};
