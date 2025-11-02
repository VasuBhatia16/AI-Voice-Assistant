import React from "react";
import "../styles/Message.css";

interface MessageProps {
  role: "user" | "assistant";
  content: string;
}

const Message: React.FC<MessageProps> = ({ role, content }) => {
  return (
    <div className={`message ${role}`}>
      <div className="message-bubble">
        <p>{content}</p>
      </div>
    </div>
  );
};

export default Message;
