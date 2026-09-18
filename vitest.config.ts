import { defineConfig } from 'vitest/config';
import vue from '@vitejs/plugin-vue';

export default defineConfig({
  plugins: [vue()],
  test: {
    environment: 'jsdom',
    include: ['apps/web/src/**/*.test.ts', 'packages/**/test/**/*.test.mjs'],
    setupFiles: ['./apps/web/src/test/setup.ts'],
  },
});
