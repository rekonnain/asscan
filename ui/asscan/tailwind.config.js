module.exports = {
  theme: {
    extend: {}
  },
  purge: [
    './src/**/*.vue',
  ],  
  variants: {
    backgroundColor: ['responsive', 'hover', 'focus', 'even', 'odd'],
  },
  minWidth: {
    '0': '0',
    '1/4': '25%',
    '1/2': '50%',
    '3/4': '75%',
    'full': '100%',
  },
  plugins: []
}
