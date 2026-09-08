import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// edgeai.tsp.edu.rs се сервира из корена поддомена → base '/'.
// Ако се хостује у подфасцикли, промени base у нпр. '/edgeai/'.
export default defineConfig({
  base: '/',
  plugins: [react()],
  build: {
    outDir: 'dist',
    target: 'es2020',
    chunkSizeWarningLimit: 1200,
    rollupOptions: {
      output: {
        manualChunks: {
          three: ['three'],
          r3f: ['@react-three/fiber', '@react-three/drei'],
          router: ['react-router-dom'],
        },
      },
    },
  },
  server: {
    host: true,
    port: 5173,
  },
})
