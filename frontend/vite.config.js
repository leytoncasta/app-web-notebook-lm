// -----------------------------------------------------------------------------
// Configuración de Vite
// -----------------------------------------------------------------------------

import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";

export default defineConfig({
  // Ruta base de la aplicación
  base: "/",

  // Plugins
  plugins: [react()],

  // Configuración del servidor de vista previa
  preview: {
    port: 3000,
    strictPort: true,
    host: "0.0.0.0",
  },

  // Configuración del servidor de desarrollo
  server: {
    port: 3000,
    strictPort: true,
    host: "0.0.0.0",
    origin: "http://0.0.0.0:3000",
  },

  // Directorio de archivos públicos
  publicDir: "public",
});
