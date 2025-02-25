// -----------------------------------------------------------------------------
// Autor: Santiago Bobadilla Suarez
// -----------------------------------------------------------------------------

// -----------------------------------------------------------------------------
// Bibliotecas
// -----------------------------------------------------------------------------

// React y Material-UI
import React, { useState } from "react";
import {
  TextField,
  Button,
  Box,
  Typography,
  Alert,
  Paper,
  Stack,
} from "@mui/material";

// Navegación y Servicios
import { useNavigate } from "react-router-dom";
import api from "../../services/api";
import { showToast } from "../../utils/toast";

// Estilos
import "../../styles/auth.css";

// -----------------------------------------------------------------------------
// Componente de Registro
// -----------------------------------------------------------------------------
// - Maneja el registro de nuevos usuarios
// - Validación de campos y contraseñas
// - Gestión de imagen de perfil
// - Redirección post-registro
const Register = () => {
  // Estado y navegación
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    nombre_usuario: "",
    contrasenia: "",
    confirmar_contrasenia: "",
  });
  const [error, setError] = useState("");

  // Manejo de cambios en el formulario
  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  // Envío del formulario
  // - Valida coincidencia de contraseñas
  // - Establece imagen por defecto si no se provee
  // - Registra usuario y maneja respuesta
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (formData.contrasenia !== formData.confirmar_contrasenia) {
      setError("Las contraseñas no coinciden");
      return;
    }

    try {
      await api.post("/usuarios", {
        nombre_usuario: formData.nombre_usuario,
        contraseña: formData.contrasenia,
      });
      showToast("Usuario creado exitosamente", "success");
      navigate("/login");
    } catch (err) {
      setError(err.response?.data?.error || "Error al crear el usuario");
    }
  };

  // -----------------------------------------------------------------------------
  // Renderizado del Componente
  // -----------------------------------------------------------------------------
  return (
    // Contenedor principal con estilos de autenticación
    <Box className="auth-container">
      {/* Tarjeta contenedora del formulario */}
      <Paper className="auth-card" elevation={0}>
        {/* Título de la aplicación */}
        <Typography
          variant="h1"
          className="title"
          sx={{
            fontSize: "clamp(2rem, 6vw, 3.5rem)", // Tamaño responsivo
            fontWeight: 800,
            color: "#2c3e50",
            mb: 2,
            textAlign: "center",
          }}
        >
          Sapiens
        </Typography>

        {/* Subtítulo de registro */}
        <Typography
          variant="h4"
          className="subtitle"
          sx={{
            fontSize: "clamp(1rem, 2.5vw, 1.5rem)", // Tamaño responsivo
            color: "#34495e",
            mb: 4,
            textAlign: "center",
          }}
        >
          Crea tu cuenta
        </Typography>

        {/* Alerta de error condicional */}
        {error && (
          <Alert severity="error" sx={{ mb: 2, width: "100%" }}>
            {error}
          </Alert>
        )}

        {/* Formulario de registro */}
        <form onSubmit={handleSubmit} className="auth-form">
          {/* Campo: Nombre de Usuario */}
          <TextField
            name="nombre_usuario"
            label="Nombre de Usuario"
            value={formData.nombre_usuario}
            onChange={handleChange}
            fullWidth
            required
            sx={{ mb: 2 }}
          />

          {/* Campo: Contraseña */}
          <TextField
            name="contrasenia"
            label="Contraseña"
            type="password"
            value={formData.contrasenia}
            onChange={handleChange}
            fullWidth
            required
            sx={{ mb: 2 }}
          />

          {/* Campo: Confirmar Contraseña */}
          <TextField
            name="confirmar_contrasenia"
            label="Confirmar Contraseña"
            type="password"
            value={formData.confirmar_contrasenia}
            onChange={handleChange}
            fullWidth
            required
            sx={{ mb: 2 }}
          />

          {/* Contenedor de botones */}
          <Stack spacing={1}>
            {/* Botón de Registro */}
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
              Registrarse
            </Button>

            {/* Botón para volver al Login */}
            <Button
              variant="outlined"
              fullWidth
              onClick={() => navigate("/login")}
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
              Volver al Login
            </Button>
          </Stack>
        </form>
      </Paper>
    </Box>
  );
};

export default Register;
