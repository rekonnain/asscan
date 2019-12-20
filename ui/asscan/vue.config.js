module.exports = {
    devServer: {
	host: '127.0.0.1',
      proxy: {
        '/api': {
          pathRewrite: {'^/api/': ''},
            target: 'http://localhost:8888/',
          changeOrigin: true
        }
      }
    },
  }
