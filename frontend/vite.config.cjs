const path = require('node:path')
const { defineConfig } = require('vite')
const vue = require('@vitejs/plugin-vue')

const rootDir = __dirname

module.exports = defineConfig({
  root: rootDir,
  cacheDir: path.join(rootDir, '.vite-cache'),
  plugins: [vue()],
  server: {
    proxy: {
      '/api': 'http://127.0.0.1:8000'
    }
  }
})
