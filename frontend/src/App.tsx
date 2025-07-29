import React, { useRef, useState } from 'react';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000'; // Update as needed

function App() {
  const [recording, setRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const [responseAudio, setResponseAudio] = useState<Blob | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunks = useRef<Blob[]>([]);

  // Start recording
  const startRecording = async () => {
    setError(null);
    setResponseAudio(null);
    setAudioBlob(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new window.MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunks.current = [];
      mediaRecorder.ondataavailable = (event: BlobEvent) => {
        if (event.data.size > 0) {
          audioChunks.current.push(event.data);
        }
      };
      mediaRecorder.onstop = () => {
        const blob = new Blob(audioChunks.current, { type: 'audio/wav' });
        setAudioBlob(blob);
      };
      mediaRecorder.start();
      setRecording(true);
    } catch (err) {
      setError('Microphone access denied or not available.');
    }
  };

  // Stop recording
  const stopRecording = () => {
    mediaRecorderRef.current?.stop();
    setRecording(false);
  };

  // Upload audio to backend
  const sendAudio = async () => {
    if (!audioBlob) return;
    setLoading(true);
    setError(null);
    setResponseAudio(null);
    try {
      const formData = new FormData();
      formData.append('audio', audioBlob, 'input.wav');
      // You may need to adjust the endpoint to match your backend REST/gRPC proxy
      const response = await fetch(`${BACKEND_URL}/api/voice`, {
        method: 'POST',
        body: formData,
      });
      if (!response.ok) throw new Error('Failed to get response from backend');
      const arrayBuffer = await response.arrayBuffer();
      setResponseAudio(new Blob([arrayBuffer], { type: 'audio/wav' }));
    } catch (err) {
      setError('Error sending audio to backend.');
    } finally {
      setLoading(false);
    }
  };

  // Play the response audio
  const playResponse = () => {
    if (responseAudio) {
      const url = URL.createObjectURL(responseAudio);
      const audio = new Audio(url);
      audio.play();
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Voice Assistant Demo</h1>
        <div style={{ margin: '1em' }}>
          {!recording ? (
            <button onClick={startRecording}>Start Recording</button>
          ) : (
            <button onClick={stopRecording}>Stop Recording</button>
          )}
        </div>
        {audioBlob && (
          <div style={{ margin: '1em' }}>
            <audio controls src={URL.createObjectURL(audioBlob)} />
            <button onClick={sendAudio} disabled={loading} style={{ marginLeft: '1em' }}>
              {loading ? 'Processing...' : 'Send to Assistant'}
            </button>
          </div>
        )}
        {responseAudio && (
          <div style={{ margin: '1em' }}>
            <audio controls src={URL.createObjectURL(responseAudio)} />
            <button onClick={playResponse} style={{ marginLeft: '1em' }}>Play Response</button>
          </div>
        )}
        {error && <div style={{ color: 'red', margin: '1em' }}>{error}</div>}
        <p style={{ marginTop: '2em' }}>
          Record your voice, send it to the assistant, and hear the LLM's response!
        </p>
      </header>
    </div>
  );
}

export default App;
