import { sveltekit } from '@sveltejs/kit/vite'
import { defineConfig } from 'vitest/config'

export default defineConfig({
  plugins: [sveltekit()],
  build: {
    emptyOutDir: true // deletes the dist folder before building
  },
  test: {
    include: ['src/**/*.{test,spec}.{js,ts}']
  }
})
