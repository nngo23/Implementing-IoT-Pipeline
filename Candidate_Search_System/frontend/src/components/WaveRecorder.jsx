import React, { useState, useRef } from "react";

const WaveRecorder = ({
  onVoiceProcessed,
  setStep,
  distribution,
  recipientEmail,
}) => {
  const [recording, setRecording] = useState(false);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

      // Force mono 16kHz using AudioContext
      const audioContext = new AudioContext({ sampleRate: 16000 });
      const source = audioContext.createMediaStreamSource(stream);
      const destination = audioContext.createMediaStreamDestination();
      source.connect(destination);

      mediaRecorderRef.current = new MediaRecorder(destination.stream, {
        mimeType: "audio/webm;codecs=opus",
      });

      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) audioChunksRef.current.push(event.data);
      };

      mediaRecorderRef.current.onstop = async () => {
        setStep("Transcribing");

        try {
          const webmBlob = new Blob(audioChunksRef.current, {
            type: "audio/webm",
          });

          const formData = new FormData();
          formData.append("audio", webmBlob, "recording.webm");

          let voiceUrl = `http://localhost:8000/api/v1/voice?output_channel=${distribution}`;
          if (distribution === "email" && recipientEmail) {
            voiceUrl += `&recipient_email=${encodeURIComponent(recipientEmail)}`;
          }

          const voiceResponse = await fetch(voiceUrl, {
            method: "POST",
            body: formData,
          });
          if (!voiceResponse.ok) throw new Error("Voice processing failed");
          const voiceData = await voiceResponse.json();
          if (!voiceData.transcription) throw new Error("Empty transcription");

          setStep("Searching");

          const searchResponse = await fetch(
            "http://localhost:8000/api/v1/search",
            {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                query: voiceData.payload.query,
                top_k: voiceData.payload.top_k || 5,
                salary_range: voiceData.payload.salary_range,
                industry: voiceData.payload.industry,
                location_filter: voiceData.payload.location_filter,
              }),
            },
          );
          if (!searchResponse.ok) throw new Error("Search failed");

          const searchData = await searchResponse.json();
          onVoiceProcessed({ ...voiceData, results: searchData.results || [] });
        } catch (error) {
          console.error("Voice Error:", error);
          alert(`Error: ${error.message}`);
          setStep("Idle");
        }
      };

      mediaRecorderRef.current.start();
      setRecording(true);
      setStep("Recording");
    } catch (error) {
      console.error("Microphone Error:", error);
      alert("Microphone permission denied.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current) mediaRecorderRef.current.stop();
    setRecording(false);
  };

  return (
    <button
      onClick={recording ? stopRecording : startRecording}
      style={{
        padding: "12px 20px",
        fontSize: "16px",
        backgroundColor: recording ? "#e53935" : "#0077B6",
        color: "white",
        border: "none",
        borderRadius: "8px",
        cursor: "pointer",
      }}
    >
      {recording ? "Stop Recording" : "Start Recording"}
    </button>
  );
};

export default WaveRecorder;
