import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import path from 'path';


// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      '/ask': 'http://localhost:5000',
      '/status': 'http://localhost:5000',
      '/feedback': 'http://localhost:5000',
    }
  },
  build: {
    outDir: '../backend/static/react',
    emptyOutDir: true,
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  }
});
