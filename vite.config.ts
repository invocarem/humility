import { defineConfig } from "vite";
import { resolve } from "node:path";

export default defineConfig({
  base: "./",
  resolve: {
    alias: {
      "@content": resolve(__dirname, "content"),
      "@app": resolve(__dirname, "app/src"),
    },
  },
  build: {
    outDir: "dist",
    emptyOutDir: true,
  },
});
