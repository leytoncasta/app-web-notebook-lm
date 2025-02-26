// -----------------------------------------------------------------------------
// Autor: Santiago Bobadilla Suarez
// -----------------------------------------------------------------------------

// -----------------------------------------------------------------------------
// Bibliotecas
// -----------------------------------------------------------------------------

// React y Material-UI
import React, { useState } from "react";
import {
  Box,
  Button,
  TextField,
  Typography,
  Alert,
  Paper,
  Stack,
} from "@mui/material";

// Navegación y Servicios
import { useNavigate } from "react-router-dom";
import api from "../../services/api";

// Estilos
import "../../styles/auth.css";

// -----------------------------------------------------------------------------
// Componente de Login
// -----------------------------------------------------------------------------
// - Maneja la autenticación de usuarios
// - Gestiona el formulario de inicio de sesión
// - Almacena token y datos de usuario
// - Redirecciona según resultado
const Login = () => {
  // Estado y navegación
  const navigate = useNavigate();
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    usuario: "",
    contraseña: "",
  });

  // Manejo de cambios en el formulario
  const handleChange = (e) => {
    setError("");
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  // Envío del formulario
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await api.post("/usuarios/login", {
        username: formData.usuario,
        password: formData.contraseña,
      });

      if (response.data.access_token) {
        localStorage.setItem("token", response.data.access_token);
        localStorage.setItem("user", JSON.stringify(response.data.usuario_id));
        navigate("/dashboard");
      }
    } catch (err) {
      if (err.response?.status === 401) {
        setError("Usuario o contraseña inválidos");
      } else if (err.response?.data?.error) {
        setError(err.response.data.error);
      } else {
        setError("Error al intentar iniciar sesión");
      }
    } finally {
      setLoading(false);
    }
  };

  // -----------------------------------------------------------------------------
  // Renderizado del Componente
  // -----------------------------------------------------------------------------
  return (
    <Box className="auth-container">
      <Paper className="auth-card" elevation={0}>
        {/* Título y Subtítulo */}
        <Typography
          variant="h1"
          className="title"
          sx={{
            fontSize: "clamp(2rem, 6vw, 3.5rem)",
            fontWeight: 800,
            color: "#2c3e50",
            mb: 2,
            textAlign: "center",
          }}
        >
          Sapiens
        </Typography>
        <Typography
          variant="h4"
          className="subtitle"
          sx={{
            fontSize: "clamp(1rem, 2.5vw, 1.5rem)",
            color: "#34495e",
            mb: 4,
            textAlign: "center",
          }}
        >
          Inicia sesión para continuar
        </Typography>

        {/* Mensaje de Error */}
        {error && (
          <Alert severity="error" sx={{ mb: 2, width: "100%" }}>
            {error}
          </Alert>
        )}

        {/* Formulario de Login */}
        <form onSubmit={handleSubmit} className="auth-form">
          <TextField
            name="usuario"
            label="Usuario"
            variant="outlined"
            value={formData.usuario}
            onChange={handleChange}
            fullWidth
            required
            sx={{ mb: 2 }}
          />
          <TextField
            name="contraseña"
            label="Contraseña"
            type="password"
            variant="outlined"
            value={formData.contraseña}
            onChange={handleChange}
            fullWidth
            required
            sx={{ mb: 3 }}
          />
          {/* Botones de Acción */}
          <Stack spacing={2}>
            <Button
              type="submit"
              variant="contained"
              fullWidth
              sx={{
                bgcolor: "#2B7781",
                fontSize: "1.1rem",
                py: 1.5,
                borderRadius: "50px",
                "&:hover": {
                  bgcolor: "#2B7781",
                  transform: "translateY(-2px)",
                  boxShadow: "0 6px 20px rgba(43, 119, 129, 0.4)",
                },
              }}
            >
              Iniciar Sesión
            </Button>
            <Button
              variant="outlined"
              fullWidth
              onClick={() => navigate("/register")}
              sx={{
                color: "#2B7781",
                borderColor: "#2B7781",
                fontSize: "1.1rem",
                py: 1.5,
                borderRadius: "50px",
                "&:hover": {
                  borderColor: "#2980b9",
                  bgcolor: "rgba(52, 152, 219, 0.1)",
                  transform: "translateY(-2px)",
                  boxShadow: "0 6px 20px rgba(43, 119, 129, 0.4)",
                },
              }}
            >
              Crear Usuario
            </Button>
          </Stack>
        </form>
      </Paper>
    </Box>
  );
};

export default Login;
