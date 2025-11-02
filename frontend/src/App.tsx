import React from "react";
import ChatBox from "./components/ChatBox";

const App: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center">
      <ChatBox />
    </div>
  );
};

export default App;
