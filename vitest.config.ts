import { resolve } from "node:path";
import { defineConfig } from "vitest/config";

export default defineConfig({
  resolve: {
    alias: {
      "@content": resolve(__dirname, "content"),
    },
  },
  test: {
    include: ["tests/**/*.test.ts"],
  },
});
