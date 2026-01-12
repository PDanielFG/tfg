module.exports = {
  devServer: {
    host: '0.0.0.0',
    port: 8080,
    hot: true,
    watchFiles: {
      options: {
        usePolling: true,
        interval: 1000
      }
    }
  }
}
