import { fileURLToPath } from "node:url";
const config = {
  turbopack: { root: fileURLToPath(new URL("..", import.meta.url)) },
  poweredByHeader: false,
  allowedDevOrigins: ["127.0.0.1"],
};
export default config;
