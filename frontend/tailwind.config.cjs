module.exports = {
  content: ['./src/**/*.html', './src/**/*.svelte'],
  media: false, // or 'media' or 'class'
  theme: {
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
          primary: '#FFFFFF',
          'primary-content': '#1A130B',
          'secondary-content': '#140E08',
          'neutral-content': '#1A130BCC',
          secondary: '#140E08'
        }
      }
    ]
  }
}
