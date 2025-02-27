import React, { useEffect, useState } from "react";
import "../../styles/chatSidebar.css";
import api from "../../services/api";

const ChatSidebar = ({
  user,
  chats,
  activeChat,
  onNewChat,
  onSelectChat,
  onLogout,
}) => {
  const [cachedUsername, setCachedUsername] = useState("");
  const [error, setError] = useState("");
  const [userChats, setUserChats] = useState([]);
  const [editingChatId, setEditingChatId] = useState(null);
  const [editTitle, setEditTitle] = useState("");

  useEffect(() => {
    const storedUsername = localStorage.getItem("nombre_usuario");
    if (storedUsername) {
      setCachedUsername(storedUsername.replace(/['"]+/g, ""));
    }
  }, []);

  useEffect(() => {
    const fetchUserChats = async () => {
      try {
        const userId = localStorage.getItem("user_id");
        const token = localStorage.getItem("token");

        if (!userId || !token) {
          setError("User session not found");
          return;
        }

        api.defaults.headers.common["Authorization"] = `Bearer ${token}`;
        const response = await api.get(`/chats/user/${JSON.parse(userId)}`);

        if (response.data) {
          setUserChats(response.data);
          setError("");
        }
      } catch (err) {
        setError("");
        console.error("Error fetching chats:", err);
      }
    };

    fetchUserChats();
  }, []);

  const handleNewChat = async () => {
    try {
      const userId = localStorage.getItem("user_id");
      const token = localStorage.getItem("token");

      if (!userId || !token) {
        setError("User session not found");
        return;
      }

      api.defaults.headers.common["Authorization"] = `Bearer ${token}`;

      const response = await api.post("/chats", {
        id_usuario: JSON.parse(userId),
      });

      if (response.data) {
        setUserChats([...userChats, response.data]);
        onNewChat(response.data);
        setError("");
      }
    } catch (err) {
      setError("Error creating new chat");
      console.error("Error creating chat:", err);
    }
  };

  const handleDeleteChat = async (chatId, e) => {
    e.stopPropagation();
    try {
      const token = localStorage.getItem("token");
      api.defaults.headers.common["Authorization"] = `Bearer ${token}`;

      const response = await api.delete(`/chats/${chatId}`);

      if (response.data) {
        setUserChats(userChats.filter((chat) => chat.id !== chatId));
        setError("");
      }
    } catch (err) {
      setError("Error deleting chat");
      console.error("Error deleting chat:", err);
    }
  };

  const handleUpdateTitle = async (chatId, newTitle) => {
    try {
      const token = localStorage.getItem("token");
      api.defaults.headers.common["Authorization"] = `Bearer ${token}`;

      const response = await api.put(`/chats/${chatId}`, {
        title: newTitle,
      });

      if (response.data) {
        setUserChats(
          userChats.map((chat) =>
            chat.id === chatId ? { ...chat, title: newTitle } : chat
          )
        );
      }
    } catch (err) {
      setError("Error updating chat title");
      console.error("Error updating title:", err);
    }
    setEditingChatId(null);
  };

  return (
    <div className="chat-sidebar">
      <div className="sidebar-header">
        <div className="user-info">
          <img
            src="https://i.pinimg.com/736x/3d/ab/e2/3dabe26fc314f91b958ab30ddcf628a1.jpg"
            alt="User Avatar"
            className="logo"
          />
          <span className="user-name">{cachedUsername || "Dara"}</span>
        </div>
      </div>

      <button className="new-chat-button" onClick={handleNewChat}>
        <span>+</span> Nuevo Chat
      </button>

      {error && <div className="error-message">{error}</div>}

      <div className="chat-list">
        {userChats.map((chat, index) => (
          <div
            key={chat.id}
            className={`chat-item ${chat.id === activeChat ? "active" : ""}`}
            onClick={() => onSelectChat(chat.id)}
            onDoubleClick={() => {
              setEditingChatId(chat.id);
              setEditTitle(`Chat ${index + 1}`);
            }}
          >
            <span className="chat-icon">📜</span>
            {editingChatId === chat.id ? (
              <input
                type="text"
                value={editTitle}
                onChange={(e) => setEditTitle(e.target.value)}
                onBlur={() => handleUpdateTitle(chat.id, editTitle)}
                onKeyPress={(e) => {
                  if (e.key === "Enter") {
                    handleUpdateTitle(chat.id, editTitle);
                  }
                }}
                autoFocus
                onClick={(e) => e.stopPropagation()}
              />
            ) : (
              <>
                <span className="chat-title">{`Chat ${chat.id}`}</span>
                <button
                  className="delete-chat-button"
                  onClick={(e) => handleDeleteChat(chat.id, e)}
                >
                  🗑️
                </button>
              </>
            )}
          </div>
        ))}
      </div>
      <button className="logout-button" onClick={onLogout}>
        Cerrar Sesión
      </button>
    </div>
  );
};

export default ChatSidebar;
