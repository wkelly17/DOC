module.exports = {
  content: ['./src/**/*.html', './src/**/*.svelte'],
  media: false, // or 'media' or 'class'
  theme: {
    screens: {
      mobile: '640px',
      // => @media (min-width: 640px) { ... }
      desktop: '1280px'
      // => @media (min-width: 1280px) { ... }
    },
    extend: {}
  },
  variants: {
    extend: {}
  },
  plugins: [require('daisyui')],
  daisyui: {
    themes: [
      {
        wa: {
          primary: '#FAA83C',
          'primary-content': '#1A130B',
          'secondary-content': '#140E08',
          'neutral-content': '#1A130BCC',
          secondary: '#140E08'
        }
      }
    ]
  }
}
