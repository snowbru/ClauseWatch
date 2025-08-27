import { defineConfig } from "astro/config";
export default defineConfig({
  site: "https://snowbru.github.io/ClauseWatch",
  base: "/ClauseWatch",
  server: { host: true, port: 4321 }
});
