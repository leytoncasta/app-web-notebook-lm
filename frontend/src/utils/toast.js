// -----------------------------------------------------------------------------
// Autor: Santiago Bobadilla Suarez
// -----------------------------------------------------------------------------

// -----------------------------------------------------------------------------
// Utilidad de Notificaciones Toast
// -----------------------------------------------------------------------------

// React-Toastify: Biblioteca para mostrar notificaciones
import { toast } from "react-toastify";

// Función para mostrar notificaciones toast
// Params:
//   - message: string (mensaje a mostrar)
//   - type: string (tipo de notificación: success, error, info, warning)
// Configuración:
//   - position: ubicación en la pantalla
//   - autoClose: tiempo de cierre automático (ms)
//   - hideProgressBar: muestra barra de progreso
//   - closeOnClick: permite cerrar al hacer clic
//   - pauseOnHover: pausa al pasar el mouse
//   - draggable: permite arrastrar la notificación
export const showToast = (message, type = "success") => {
  toast[type](message, {
    position: "top-right",
    autoClose: 3000,
    hideProgressBar: false,
    closeOnClick: true,
    pauseOnHover: true,
    draggable: true,
    style: {
      background: "#FFE5B4",
      color: "#000000",
    },
  });
};
