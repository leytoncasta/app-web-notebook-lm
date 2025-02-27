import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import ChatSidebar from "./ChatSidebar";
import ChatArea from "./ChatArea";
import api from "../../services/api";
import "../../styles/dashboard.css";

const Dashboard = () => {
  const navigate = useNavigate();
  const [chats, setChats] = useState([]);
  const [activeChat, setActiveChat] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchChats = async () => {
      try {
        const userId = localStorage.getItem("user_id");
        const token = localStorage.getItem("token");

        if (!userId || !token) {
          navigate("/login");
          return;
        }

        api.defaults.headers.common["Authorization"] = `Bearer ${token}`;
        const response = await api.get(`/chats/user/${JSON.parse(userId)}`);

        if (response.data) {
          setChats(response.data);
        }
      } catch (err) {
        setError("Error loading chats");
        console.error("Error:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchChats();
  }, [navigate]);

  const handleNewChat = async (chat) => {
    setChats([chat, ...chats]);
    setActiveChat(chat.id);
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user_id");
    localStorage.removeItem("nombre_usuario");
    navigate("/login");
  };

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <div className="dashboard">
      <ChatSidebar
        chats={chats}
        activeChat={activeChat}
        onNewChat={handleNewChat}
        onSelectChat={setActiveChat}
        onLogout={handleLogout}
      />
      <ChatArea chat={chats.find((chat) => chat.id === activeChat)} />
      {error && <div className="error-message">{error}</div>}
    </div>
  );
};

export default Dashboard;
