import React, { useState, useRef } from "react";

const API_BASE = "http://localhost:8000/api/v1";

const WaveRecorder = ({
  onCandidates,
  onExplanationPatch,
  onError,
  setStep,
  distribution,
  recipientEmail,
}) => {
  const [recording, setRecording] = useState(false);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  // 🔥 prevent duplicate error spam
  const errorEmittedRef = useRef(false);

  // 🔥 SSE controller (important cleanup)
  const abortControllerRef = useRef(null);

  // ─────────────────────────────────────────────
  // START RECORDING
  // ─────────────────────────────────────────────
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

      const audioCtx = new AudioContext({ sampleRate: 16000 });
      const source = audioCtx.createMediaStreamSource(stream);
      const dest = audioCtx.createMediaStreamDestination();
      source.connect(dest);

      const mr = new MediaRecorder(dest.stream, {
        mimeType: "audio/webm;codecs=opus",
      });

      mediaRecorderRef.current = mr;
      audioChunksRef.current = [];

      mr.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunksRef.current.push(e.data);
      };

      mr.onstop = () => handleRecordingDone();

      mr.start();
      setRecording(true);
      setStep("Recording");

      // reset error state each session
      errorEmittedRef.current = false;
    } catch (err) {
      console.error("Microphone error:", err);
      onError?.("Microphone permission denied.");
    }
  };

  // ─────────────────────────────────────────────
  // STOP RECORDING
  // ─────────────────────────────────────────────
  const stopRecording = () => {
    mediaRecorderRef.current?.stop();
    setRecording(false);
  };

  // ─────────────────────────────────────────────
  // MAIN PIPELINE
  // ─────────────────────────────────────────────
  const handleRecordingDone = async () => {
    setStep("Transcribing");

    try {
      const blob = new Blob(audioChunksRef.current, {
        type: "audio/webm",
      });

      const form = new FormData();
      form.append("audio", blob, "recording.webm");

      let voiceUrl = `${API_BASE}/voice?output_channel=${distribution}`;
      if (distribution === "email" && recipientEmail) {
        voiceUrl += `&recipient_email=${encodeURIComponent(recipientEmail)}`;
      }

      const voiceResp = await fetch(voiceUrl, {
        method: "POST",
        body: form,
      });

      if (!voiceResp.ok) throw new Error("Voice processing failed");

      const voiceData = await voiceResp.json();

      if (!voiceData.transcription) {
        throw new Error("Empty transcription");
      }

      // ─────────────────────────────────────────────
      // HARD EXIT (invalid query)
      // ─────────────────────────────────────────────
      if (!voiceData.success) {
        if (!errorEmittedRef.current) {
          errorEmittedRef.current = true;
          onError?.(voiceData.warning || "Invalid query");
        }
        setStep("Idle");
        return;
      }

      setStep("Searching");

      // ─────────────────────────────────────────────
      // SSE STREAM
      // ─────────────────────────────────────────────
      abortControllerRef.current?.abort();
      abortControllerRef.current = new AbortController();

      const searchBody = JSON.stringify({
        query: voiceData.payload.query,
        top_k: voiceData.payload.top_k || 5,
        salary_range: voiceData.payload.salary_range ?? null,
        industry: voiceData.payload.industry ?? null,
        location_filter: voiceData.payload.location_filter ?? null,
        role_keywords: voiceData.payload.role_keywords ?? null,
        output_channel: distribution,
        recipient_email: distribution === "email" ? recipientEmail : null,
      });

      const streamResp = await fetch(`${API_BASE}/search/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: searchBody,
        signal: abortControllerRef.current.signal,
      });

      if (!streamResp.ok) throw new Error("Search stream failed");

      const reader = streamResp.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        const blocks = buffer.split("\n\n");
        buffer = blocks.pop() ?? "";

        for (const block of blocks) {
          const eventMatch = block.match(/^event:\s*(.+)/m);
          const dataMatch = block.match(/^data:\s*(.+)/ms);

          if (!eventMatch || !dataMatch) continue;

          const event = eventMatch[1].trim();

          let data;
          try {
            data = JSON.parse(dataMatch[1].trim());
          } catch {
            continue;
          }

          if (event === "candidates") {
            onCandidates?.({
              transcription: voiceData.transcription,
              ...data,
            });
            setStep("Complete");
          }

          if (event === "explanations") {
            onExplanationPatch?.(data.patches ?? {});
          }

          if (event === "error") {
            if (!errorEmittedRef.current) {
              errorEmittedRef.current = true;
              onError?.(data.detail || "No candidates found");
            }
            setStep("Idle");
            return;
          }
        }
      }
    } catch (err) {
      console.error("Pipeline error:", err);
      if (!errorEmittedRef.current) {
        errorEmittedRef.current = true;
        onError?.(err.message);
      }
      setStep("Idle");
    }
  };

  // ─────────────────────────────────────────────
  // UI
  // ─────────────────────────────────────────────
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
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
        {recording ? "⏹ Stop Recording" : "🎙 Start Recording"}
      </button>
    </div>
  );
};

export default WaveRecorder;
