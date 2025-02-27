import React, { useState, useRef, useEffect } from "react";
import "../../styles/chatArea.css";
import api from "../../services/api";

const ChatArea = ({ chat }) => {
  const [message, setMessage] = useState("");
  const [chatMessages, setChatMessages] = useState({});
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const fileInputRef = useRef();
  const messagesEndRef = useRef(null);

  // Get messages for current chat
  const currentMessages = chat ? chatMessages[chat.id] || [] : [];

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
    if (!message.trim() && !file) return;

    try {
      setLoading(true);

      // Add message to UI immediately for current chat
      if (message.trim()) {
        const newMessage = {
          content: message,
          isUser: true,
          timestamp: new Date().toISOString(),
        };

        setChatMessages((prev) => ({
          ...prev,
          [chat.id]: [...(prev[chat.id] || []), newMessage],
        }));
      }

      // Handle file upload if present
      if (file) {
        const formData = new FormData();
        formData.append("file_upload", file);

        const token = localStorage.getItem("token");
        api.defaults.headers.common["Authorization"] = `Bearer ${token}`;

        try {
          await api.post("/documentos/uploadfile", formData, {
            headers: {
              "Content-Type": "multipart/form-data",
            },
          });

          // Add file confirmation message for current chat
          setChatMessages((prev) => ({
            ...prev,
            [chat.id]: [
              ...(prev[chat.id] || []),
              {
                content: `File uploaded: ${file.name}`,
                isUser: true,
                timestamp: new Date().toISOString(),
              },
            ],
          }));
        } catch (err) {
          setError("Error uploading PDF");
          console.error("Upload error:", err);
        }
      }

      setMessage("");
      setFile(null);
      setError("");
    } catch (err) {
      setError("Error sending message");
      console.error("Error:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = (e) => {
    const selectedFile = e.target.files[0];

    if (selectedFile) {
      if (selectedFile.type !== "application/pdf") {
        setError("Only PDF files are allowed");
        return;
      }

      if (selectedFile.size > 5000000) {
        // 5MB limit
        setError("File size should be less than 5MB");
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
          >
            📄
          </button>
          {file && <span className="file-name">{file.name}</span>}
        </div>
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Type a message..."
          className="message-input"
          disabled={loading}
        />
        <button type="submit" className="send-button" disabled={loading}>
          {loading ? "Sending..." : "Send"}
        </button>
      </form>
    </div>
  );
};

export default ChatArea;
