import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";
export default defineConfig(({ mode }) => ({
  plugins: [react(), {
    name: "local-map-config",
    configureServer(server) {
      const clientId = loadEnv(mode, process.cwd(), "NAVER_").NAVER_MAP_CLIENT_ID;
      server.middlewares.use("/api/maps-config", (_request, response) => {
        response.setHeader("Content-Type", "application/json");
        response.setHeader("Cache-Control", "no-store");
        response.statusCode = clientId ? 200 : 503;
        // Web SDK requires the domain-restricted Client ID. Never return Client Secret.
        response.end(JSON.stringify(clientId ? { clientId } : { error: "missing_client_id" }));
      });
    },
  }],
  server: { port: 5173, strictPort: true, proxy: { "/api/runs": "http://127.0.0.1:8000" } },
}));
