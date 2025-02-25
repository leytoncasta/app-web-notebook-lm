// -----------------------------------------------------------------------------
// Autor: Santiago Bobadilla Suarez
// -----------------------------------------------------------------------------

// -----------------------------------------------------------------------------
// Bibliotecas
// -----------------------------------------------------------------------------

// React y Material-UI
// - React: Biblioteca base
// - Box, Button, Typography, Paper: Componentes de Material-UI
import React from "react";
import { Box, Button, Typography, Paper } from "@mui/material";

// Navegación
// - useNavigate: Hook para navegación programática
import { useNavigate } from "react-router-dom";

// Estilos
import "../styles/home.css";

// -----------------------------------------------------------------------------
// Página Principal
// -----------------------------------------------------------------------------
// Componente que muestra la página de inicio
// - Título de la aplicación
// - Subtítulo descriptivo
// - Botón de acción principal
const HomePage = () => {
  // Hook de navegación
  const navigate = useNavigate();

  // Renderizado del componente
  return (
    // Contenedor principal con fondo y estilos
    <Box className="home-container">
      {/* Tarjeta de contenido principal */}
      <Paper className="content-card" elevation={0}>
        {/* Título de la aplicación */}
        <Typography
          variant="h1"
          className="title"
          sx={{
            fontSize: "clamp(2.5rem, 8vw, 4.5rem)",
            fontWeight: 800,
            color: "#2c3e50",
            mb: 2,
            textAlign: "center",
          }}
        >
          Sapiens
        </Typography>

        {/* Subtítulo descriptivo */}
        <Typography
          variant="h4"
          className="subtitle"
          sx={{
            fontSize: "clamp(1.2rem, 3vw, 1.8rem)",
            color: "#34495e",
            mb: 4,
            textAlign: "center",
          }}
        >
          Documentos inteligentes, decisiones sabias.
        </Typography>

        {/* Botón de acción principal */}
        <Button
          variant="contained"
          className="action-button"
          onClick={() => navigate("/login")}
          sx={{
            bgcolor: "#2B7781",
            fontSize: "1.2rem",
            py: 1.5,
            px: 4,
            borderRadius: "50px",
            "&:hover": {
              bgcolor: "#2B7781",
              transform: "translateY(-2px)",
              boxShadow: "0 6px 20px rgba(43, 119, 129, 0.4)",
            },
          }}
        >
          Comenzar Ahora
        </Button>
      </Paper>
    </Box>
  );
};

export default HomePage;
