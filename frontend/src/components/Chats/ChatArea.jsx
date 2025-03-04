import React, { useState, useRef, useEffect } from "react";
import "../../styles/chatArea.css";
import api from "../../services/api";

const ChatArea = ({ chat }) => {
  const [message, setMessage] = useState("");
  const [chatMessages, setChatMessages] = useState({});
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [hasDocuments, setHasDocuments] = useState({}); // Track documents per chat
  const [isAiTyping, setIsAiTyping] = useState(false); // Track AI typing state
  const fileInputRef = useRef();
  const messagesEndRef = useRef(null);

  // Obtener mensajes del chat actual
  const currentMessages = chat ? chatMessages[chat.id] || [] : [];
  const currentChatHasDocument = chat ? hasDocuments[chat.id] || false : false;

  useEffect(() => {
    scrollToBottom();
  }, [currentMessages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  if (!chat) {
    return (
      <div className="empty-chat-area">
        <div className="empty-state">
          <h2>Seleccione un chat para empezar</h2>
        </div>
      </div>
    );
  }

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (file) {
      await handleFileUploadSubmit();
    } else if (message.trim() && currentChatHasDocument) {
      await handleMessageSubmit();
    }
  };

  const handleFileUploadSubmit = async () => {
    try {
      setLoading(true);
      const formData = new FormData();
      formData.append("file_upload", file);
      formData.append("chat_id", chat.id);

      const token = localStorage.getItem("token");
      api.defaults.headers.common["Authorization"] = `Bearer ${token}`;

      await api.post("/documentos/uploadfile", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      setChatMessages((prev) => ({
        ...prev,
        [chat.id]: [
          ...(prev[chat.id] || []),
          {
            content: `Documento subido: ${file.name}`,
            isUser: true,
            timestamp: new Date().toISOString(),
          },
        ],
      }));

      setHasDocuments((prev) => ({
        ...prev,
        [chat.id]: true,
      }));
      setFile(null);
      setError("");
    } catch (err) {
      setError("Error al subir el PDF");
      console.error("Error de subida:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleMessageSubmit = async () => {
    try {
      setLoading(true);
      setIsAiTyping(true);

      // Agregar mensaje del usuario a la UI
      const newMessage = {
        content: message,
        isUser: true,
        timestamp: new Date().toISOString(),
      };

      setChatMessages((prev) => ({
        ...prev,
        [chat.id]: [...(prev[chat.id] || []), newMessage],
      }));

      api
        .post("/prompt/", {
          text: message,
          chat_id: chat.id,
        })
        .catch((error) => {
          console.error("Error sending prompt:", error);
          throw error;
        });

      let attempts = 0;
      const maxAttempts = 300; // 5 minutos máximo

      const pollResponse = async () => {
        try {
          const llmResponse = await api.get(`/LLM/response/${chat.id}`);

          if (llmResponse.data.status === "success" && llmResponse.data.data) {
            setChatMessages((prev) => ({
              ...prev,
              [chat.id]: [
                ...(prev[chat.id] || []),
                {
                  content: llmResponse.data.data,
                  isUser: false,
                  timestamp: new Date().toISOString(),
                },
              ],
            }));
            return true;
          }

          attempts++;
          if (attempts >= maxAttempts) {
            setError("Tiempo de espera agotado");
            return true;
          }

          await new Promise((resolve) => setTimeout(resolve, 1000));
          return false;
        } catch (error) {
          console.error("Error polling response:", error);
          setError("Error al obtener la respuesta");
          return true;
        }
      };

      while (!(await pollResponse())) {
        continue;
      }

      setMessage("");
      setError("");
    } catch (err) {
      setError("Error al enviar el mensaje");
      console.error("Error:", err);
    } finally {
      setLoading(false);
      setIsAiTyping(false);
    }
  };

  const handleFileUpload = (e) => {
    const selectedFile = e.target.files[0];

    if (selectedFile) {
      if (selectedFile.type !== "application/pdf") {
        setError("Solo se permiten archivos PDF");
        return;
      }

      if (selectedFile.size > 5000000) {
        setError("El archivo debe ser menor a 5MB");
        return;
      }

      setFile(selectedFile);
      setError("");
    }
  };

  return (
    <div className="chat-area">
      <div className="chat-header">
        <h2>{`Chat ${chat.id}`}</h2>
      </div>

      <div className="messages">
        {currentMessages.map((msg, index) => (
          <div key={index} className={`message ${msg.isUser ? "user" : "ai"}`}>
            <div className="message-content">{msg.content}</div>
            <div className="message-timestamp">
              {new Date(msg.timestamp).toLocaleTimeString([], {
                hour: "2-digit",
                minute: "2-digit",
              })}
            </div>
          </div>
        ))}
        {isAiTyping && (
          <div className="message ai">
            <div className="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {error && <div className="error-message">{error}</div>}

      <form className="input-area" onSubmit={handleSubmit}>
        <div className="file-upload">
          <input
            type="file"
            accept=".pdf"
            ref={fileInputRef}
            onChange={handleFileUpload}
            style={{ display: "none" }}
          />
          <button
            type="button"
            onClick={() => fileInputRef.current.click()}
            className="upload-button"
            disabled={currentChatHasDocument || loading}
          >
            📄
          </button>
          {file && <span className="file-name">{file.name}</span>}
        </div>
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder={
            currentChatHasDocument
              ? "Escribe un mensaje..."
              : "Sube un documento primero"
          }
          className="message-input"
          disabled={loading || !currentChatHasDocument}
        />
        <button
          type="submit"
          className="send-button"
          disabled={
            loading ||
            (!file && !currentChatHasDocument) ||
            (!message.trim() && !file)
          }
        >
          {loading ? "Procesando..." : "Enviar"}
        </button>
      </form>
    </div>
  );
};

export default ChatArea;
