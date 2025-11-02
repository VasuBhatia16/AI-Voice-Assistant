import React, { useState, useEffect } from "react";
import Message from "./Message";
import Recorder from "./Recorder";
import { sendMessage } from "../api/chat";
import { processVoice } from "../api/voice";
import "../styles/ChatBox.css";

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

const ChatBox: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [sessionId] = useState(() => localStorage.getItem("session_id") || crypto.randomUUID());

  useEffect(() => {
    localStorage.setItem("session_id", sessionId);
  }, [sessionId]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const newMessages = [...messages, { role: "user" as const, content: input }];
    setMessages(newMessages);
    setInput("");

    const reply = await sendMessage(input, sessionId);
    setMessages([...newMessages, { role: "assistant" as const, content: reply.response }]);
  };

  const handleVoice = async (audioBase64: string) => {
    const reply = await processVoice(audioBase64, sessionId);
    setMessages((prev) => [
      ...prev,
      { role: "user" as const, content: "(🎙️ Voice Input)" },
      { role: "assistant" as const, content: reply.text },
    ]);
    if (reply.audio_base64) {
      const audio = new Audio(`data:audio/wav;base64,${reply.audio_base64}`);
      audio.play();
    }
  };

  return (
    <div className="chatbox-container">
      <div className="chatbox-messages">
        {messages.length === 0 ? (
          <div className="empty-state">Start a conversation or use the 🎙️ mic</div>
        ) : (
          messages.map((m, i) => <Message key={i} role={m.role} content={m.content} />)
        )}
      </div>

      <div className="chatbox-input">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
        />
        <button onClick={handleSend}>Send</button>
        <Recorder onSend={handleVoice} />
      </div>
    </div>
  );
};

export default ChatBox;
