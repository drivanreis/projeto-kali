import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5190,
    strictPort: true,
    host: true,
    cors: true,
    watch: {
      usePolling: true,
    },
  },
  build: {
    target: 'esnext',
    minify: 'esbuild',
    sourcemap: false,
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})
