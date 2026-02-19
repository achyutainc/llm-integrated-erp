import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    tailwindcss(),
  ],
  server: {
    proxy: {
      '/api': {
        // Use 'backend' service name for Docker, or fallback to localhost for local dev
        // Note: Vite runs in build/dev mode. In Docker, if using 'npm run dev', it proxies from container to backend container.
        // If accessed from host, the browser talks to vite (container), which proxies to backend (container).
        target: process.env.BACKEND_URL || 'http://backend:8000',
        changeOrigin: true,
      },
      '/ai': {
        target: process.env.AI_URL || 'http://ai_engine:8001',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/ai/, '')
      }
    }
  }
})
