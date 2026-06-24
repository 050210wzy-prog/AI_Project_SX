import { build } from 'vite'
import vue from '@vitejs/plugin-vue'

await build({
  root: '.',
  configFile: false,
  cacheDir: './.vite-cache',
  plugins: [vue()],
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    rollupOptions: {
      input: 'index.html'
    },
    chunkSizeWarningLimit: 1200
  }
})
