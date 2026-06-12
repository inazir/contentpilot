import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],

  // If deployed under a sub-path, set base here.
  // For root domain deployment leave as "/".
  base: "/",

  build: {
    outDir:        "dist",
    emptyOutDir:   true,
    sourcemap:     false,
    chunkSizeWarningLimit: 800,
    rollupOptions: {
      output: {
        // Split jsPDF into its own chunk to keep main bundle lean
        manualChunks: {
          jspdf: ["jspdf"],
        },
      },
    },
  },

  server: {
    port: 5173,
    host: true,
  },
});
