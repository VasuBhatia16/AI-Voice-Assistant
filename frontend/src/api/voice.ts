import axios from "axios";
const isDev = import.meta.env.DEV;
console.log(isDev);
export const BASE_URL = isDev
  ? "http://localhost:8000/api/v1/chat"
  : import.meta.env.VITE_API_URL;

export const processVoice = async (audioBase64: string, sessionId: string) => {
  const res = await axios.post(`${BASE_URL}/process`, { audio_base64: audioBase64, session_id: sessionId });
  return res.data;
};
