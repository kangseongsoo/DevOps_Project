const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  // API 요청을 백엔드로 프록시
  app.use(
    '/api',
    createProxyMiddleware({
      target: 'http://backend:7000',
      changeOrigin: true,
      pathRewrite: {
        '^/api': '', // /api 제거
      },
    })
  );

  // 백엔드 직접 경로들을 프록시
  app.use(
    ['/auth', '/chat', '/simple-chat', '/conversation', '/sessions', '/health'],
    createProxyMiddleware({
      target: 'http://backend:7000',
      changeOrigin: true,
    })
  );
}; 