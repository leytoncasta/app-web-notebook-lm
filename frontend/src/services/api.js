// -----------------------------------------------------------------------------
// Autor: Santiago Bobadilla Suarez
// -----------------------------------------------------------------------------

// -----------------------------------------------------------------------------
// Configuración de Cliente HTTP
// -----------------------------------------------------------------------------

// Axios: Cliente HTTP para realizar peticiones
import axios from "axios";

// Creación de instancia de axios con configuración base
// - baseURL: URL base del servidor
// - headers: Cabeceras por defecto
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// -----------------------------------------------------------------------------
// Interceptores de Peticiones
// -----------------------------------------------------------------------------

// Interceptor de peticiones salientes
// - Añade token de autenticación si existe
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor de respuestas
// - Maneja errores de autenticación
// - Redirecciona a login si el token expira
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export default api;
