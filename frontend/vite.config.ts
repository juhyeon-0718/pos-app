import react from '@vitejs/plugin-react'
import { defineConfig } from 'vitest/config'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // Prism 목 서버(docs/api/openapi.yaml 기준, npm run mock)로 전달한다.
      // BASE_URL(/api/v1) 접두사는 계약 경로에 없으므로 벗겨서 전달한다.
      '/api/v1': {
        target: 'http://127.0.0.1:4010',
        changeOrigin: true,
        rewrite: (path: string) => path.replace(/^\/api\/v1/, ''),
      },
    },
  },
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/setupTests.ts'],
  },
})
