import axios from "axios";

const BASE_URL = "http://localhost:8000/api/v1/voice";

export const processVoice = async (audioBase64: string, sessionId: string) => {
  const res = await axios.post(`${BASE_URL}/process`, { audio_base64: audioBase64, session_id: sessionId });
  return res.data;
};
