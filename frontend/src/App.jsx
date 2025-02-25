// -----------------------------------------------------------------------------
// Autor: Santiago Bobadilla Suarez
// -----------------------------------------------------------------------------

// -----------------------------------------------------------------------------
// Bibliotecas
// -----------------------------------------------------------------------------

// React Router: Biblioteca para manejo de rutas
// - BrowserRouter: Proveedor principal de enrutamiento
// - Routes: Contenedor de rutas
// - Route: Definición de una ruta individual
// - Navigate: Componente para redirección
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

// Componentes de Autenticación
import Login from "./components/Auth/Login";
import Register from "./components/Auth/Register";
import HomePage from "./views/HomePage";

// -----------------------------------------------------------------------------
// Componente de Ruta Privada
// -----------------------------------------------------------------------------
// Verifica si existe un token de autenticación
// Si existe, muestra el componente hijo
// Si no existe, redirige a la página de login
const PrivateRoute = ({ children }) => {
  const token = localStorage.getItem("token");
  return token ? children : <Navigate to="/login" />;
};

// -----------------------------------------------------------------------------
// Componente Principal App
// -----------------------------------------------------------------------------
// Define la estructura de rutas de la aplicación
// - /: Página principal
// - /login: Inicio de sesión
// - /register: Registro de usuario
// - /categorias: Vista de categorías (protegida)
// - /tareas: Vista de tareas (protegida)
function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/chats" element={<PrivateRoute></PrivateRoute>} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
