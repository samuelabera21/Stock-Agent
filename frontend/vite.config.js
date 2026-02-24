import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/predict': 'http://127.0.0.1:5000',
      '/train': 'http://127.0.0.1:5000',
      '/health': 'http://127.0.0.1:5000',
    },
  },
})
