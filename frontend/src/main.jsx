// -----------------------------------------------------------------------------
// Autor: Santiago Bobadilla Suarez
// -----------------------------------------------------------------------------

// -----------------------------------------------------------------------------
// Bibliotecas
// -----------------------------------------------------------------------------

// React: Biblioteca principal para construir interfaces de usuario
// - React: Funcionalidad core de React
// - ReactDOM: Renderizado de componentes en el DOM
import React from "react";
import ReactDOM from "react-dom/client";

// React-Toastify: Biblioteca para mostrar notificaciones
// - ToastContainer: Contenedor para las notificaciones
import { ToastContainer } from "react-toastify";

// Componentes y Estilos Locales
// - App: Componente principal de la aplicación
// - index.css: Estilos globales
// - ReactToastify.css: Estilos para las notificaciones
import App from "./App";
import "./index.css";
import "react-toastify/dist/ReactToastify.css";

// -----------------------------------------------------------------------------
// Renderizado de la Aplicación
// -----------------------------------------------------------------------------
// Renderiza la aplicación en el elemento root
// Usa StrictMode para detectar problemas potenciales
// Configura el proveedor de fechas y el contenedor de notificaciones
ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
    <ToastContainer />
  </React.StrictMode>
);
