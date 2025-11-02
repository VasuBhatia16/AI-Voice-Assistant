import React, { useState, useRef } from "react";
import "../styles/Recorder.css";

interface RecorderProps {
  onSend: (audioBase64: string) => void;
}

const Recorder: React.FC<RecorderProps> = ({ onSend }) => {
  const [recording, setRecording] = useState(false);
  const mediaRecorder = useRef<MediaRecorder | null>(null);
  const audioChunks = useRef<Blob[]>([]);

  const startRecording = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder.current = new MediaRecorder(stream, { mimeType: "audio/webm" });

    audioChunks.current = [];
    mediaRecorder.current.ondataavailable = (e) => audioChunks.current.push(e.data);

    mediaRecorder.current.onstop = async () => {
      const blob = new Blob(audioChunks.current, { type: "audio/webm" });

      const arrayBuffer = await blob.arrayBuffer();
      const audioCtx = new AudioContext();
      const audioBuffer = await audioCtx.decodeAudioData(arrayBuffer); // Webm -> 64
      const wavBlob = await audioBufferToWavBlob(audioBuffer); // 64->wav

      const reader = new FileReader();
      reader.onloadend = () => {
        const base64 = (reader.result as string).split(",")[1];
        onSend(base64);
      };
      reader.readAsDataURL(wavBlob);
    };

    mediaRecorder.current.start();
    setRecording(true);
  };

  const stopRecording = () => {
    mediaRecorder.current?.stop();
    setRecording(false);
  };

  return (
    <button
      className={`recorder-btn ${recording ? "recording" : ""}`}
      onClick={recording ? stopRecording : startRecording}
    >
      {recording ? "Stop 🔴" : "🎙️ Record"}
    </button>
  );
};
async function audioBufferToWavBlob(audioBuffer: AudioBuffer): Promise<Blob> {
  const numOfChan = audioBuffer.numberOfChannels;
  const length = audioBuffer.length * numOfChan * 2 + 44;
  const buffer = new ArrayBuffer(length);
  const view = new DataView(buffer);
  const channels: Float32Array[] = [];

  let pos = 0;

  const setUint16 = (data: number) => { view.setUint16(pos, data, true); pos += 2; };
  const setUint32 = (data: number) => { view.setUint32(pos, data, true); pos += 4; };

  // WAV header
  setUint32(0x46464952);
  setUint32(length - 8);
  setUint32(0x45564157);
  setUint32(0x20746d66);
  setUint32(16);
  setUint16(1);
  setUint16(numOfChan);
  setUint32(audioBuffer.sampleRate);
  setUint32(audioBuffer.sampleRate * 2 * numOfChan);
  setUint16(numOfChan * 2);
  setUint16(16);
  setUint32(0x61746164);
  setUint32(length - pos - 4);

  for (let i = 0; i < numOfChan; i++) channels.push(audioBuffer.getChannelData(i));
  const interleaved = interleave(channels);
  const len = interleaved.length;
  for (let i = 0; i < len; i++, pos += 2) {
    const s = Math.max(-1, Math.min(1, interleaved[i]));
    view.setInt16(pos, s < 0 ? s * 0x8000 : s * 0x7fff, true);
  }

  return new Blob([buffer], { type: "audio/wav" });
}

function interleave(channels: Float32Array[]): Float32Array {
  const length = channels[0].length;
  const result = new Float32Array(length * channels.length);
  let index = 0;
  for (let i = 0; i < length; i++) {
    for (let j = 0; j < channels.length; j++) {
      result[index++] = channels[j][i];
    }
  }
  return result;
}

export default Recorder;
