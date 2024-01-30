;(function (window) {
  window.env = window.env || {}

  // Environment variables
  window['env']['BACKEND_API_URL'] = '${BACKEND_API_URL}'
  window['env']['FILE_SERVER_URL'] = '${FILE_SERVER_URL}'
  window['env']['LOGROCKET_ID'] = '${LOGROCKET_ID}'
})(this)
