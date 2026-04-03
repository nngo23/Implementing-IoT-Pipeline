import React, { useState, useEffect } from "react";
import {
  Box,
  Typography,
  Select,
  MenuItem,
  CircularProgress,
  TextField,
  Card,
  CardContent,
  Grid,
  Chip,
  Button,
} from "@mui/material";
import WaveRecorder from "./components/WaveRecorder";

const App = () => {
  const [voiceText, setVoiceText] = useState("");
  const [step, setStep] = useState("Idle");
  const [distribution, setDistribution] = useState("slack");
  const [recipientEmail, setRecipientEmail] = useState("");
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleVoiceResponse = async (voiceResponse) => {
    setLoading(true);
    setStep("Evaluating");

    try {
      if (!voiceResponse.success) throw new Error("Voice processing failed");

      setVoiceText(voiceResponse.transcription);
      setCandidates(voiceResponse.results || []);
      setStep("Complete");
    } catch (err) {
      console.error(err);
      alert("Processing failed.");
      setStep("Idle");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const handler = (e) => {
      handleVoiceResponse(e.detail);
    };

    window.addEventListener("TEST_VOICE_RESPONSE", handler);
    return () => window.removeEventListener("TEST_VOICE_RESPONSE", handler);
  }, []);

  const handleReset = () => {
    setVoiceText("");
    setCandidates([]);
    setStep("Idle");
  };

  const isProcessing =
    step === "Recording" ||
    step === "Transcribing" ||
    step === "Searching" ||
    step === "Evaluating";

  // Build professional Gmail URL
  const buildGmailUrl = (candidate) => {
    if (!candidate.email) return null;

    const subject = encodeURIComponent(
      `Interview Invitation - ${candidate.role_en} Position`,
    );

    const body = encodeURIComponent(
      `Dear ${candidate.name},\n\n` +
        `Thank you for your interest in the ${candidate.role_en} position at our company.\n\n` +
        `We would like to invite you for an interview to discuss this opportunity further.\n\n` +
        `Interview Details:\n` +
        `───────────────────\n` +
        `Position: ${candidate.role_en}\n` +
        `Date: [Please specify date]\n` +
        `Time: [Please specify time]\n` +
        `Duration: Approximately 60 minutes\n` +
        `Location: [Please specify location or meeting link]\n\n` +
        `Interview Format:\n` +
        `The interview will be conducted by our HR team and hiring manager. ` +
        `We will discuss your experience, skills, and how you might contribute to our team.\n\n` +
        `Please confirm your availability by replying to this email.\n\n` +
        `If you have any questions or need to reschedule, please do not hesitate to contact us.\n\n` +
        `We look forward to meeting you.\n\n` +
        `Best regards,\n` +
        `HR Department\n` +
        `[Your Company Name]\n` +
        `[Contact Email]\n` +
        `[Phone Number]`,
    );

    return `https://mail.google.com/mail/?view=cm&fs=1&to=${candidate.email}&su=${subject}&body=${body}`;
  };

  return (
    <Box sx={{ p: 4, maxWidth: 1200, mx: "auto" }}>
      <Typography
        variant="h4"
        sx={{
          mb: 3,
          fontWeight: "bold",
          color: "#0077B6",
          textAlign: "center",
        }}
      >
        Candidate Voice Search
      </Typography>

      <Typography
        variant="body1"
        sx={{ mb: 3, color: "text.secondary", textAlign: "center" }}
      >
        Record a voice command to search candidates. Results will be sent via
        Slack or Email and displayed below.
      </Typography>

      {/* Controls */}
      <Box sx={{ maxWidth: 600, mx: "auto", mb: 4 }}>
        {/* Distribution Selector */}
        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" sx={{ mb: 1 }}>
            Distribution Channel:
          </Typography>
          <Select
            value={distribution}
            onChange={(e) => setDistribution(e.target.value)}
            disabled={isProcessing}
            fullWidth
          >
            <MenuItem value="slack">Slack – Team Channel</MenuItem>
            <MenuItem value="email">Email Distribution</MenuItem>
          </Select>
        </Box>

        {/* Email Field */}
        {distribution === "email" && (
          <Box sx={{ mb: 3 }}>
            <TextField
              label="Recipient Email"
              fullWidth
              value={recipientEmail}
              onChange={(e) => setRecipientEmail(e.target.value)}
              disabled={isProcessing}
              placeholder="recipient@example.com"
            />
          </Box>
        )}

        {/* Recorder */}
        <Box sx={{ textAlign: "center", mb: 2 }}>
          <WaveRecorder
            onVoiceProcessed={handleVoiceResponse}
            setStep={setStep}
            distribution={distribution}
            recipientEmail={recipientEmail}
          />
        </Box>

        {/* Status */}
        <Box sx={{ textAlign: "center" }}>
          <Typography variant="body2" sx={{ color: "text.secondary" }}>
            Status: <strong>{step}</strong>
          </Typography>
          {loading && (
            <Box sx={{ mt: 2 }}>
              <CircularProgress size={24} />
            </Box>
          )}
        </Box>

        {/* Transcription */}
        {voiceText && (
          <Box sx={{ mt: 3, p: 2, bgcolor: "#f5f5f5", borderRadius: 2 }}>
            <Typography variant="body2" sx={{ color: "text.secondary" }}>
              Transcription:
            </Typography>
            <Typography variant="body1" sx={{ fontStyle: "italic", mt: 1 }}>
              "{voiceText}"
            </Typography>
          </Box>
        )}
      </Box>

      {/* Candidate Results */}
      {candidates.length > 0 && (
        <Box sx={{ mt: 4 }}>
          <Typography variant="h5" sx={{ mb: 3, fontWeight: "bold" }}>
            Top {candidates.length} Candidates
          </Typography>

          <Grid container spacing={3}>
            {candidates.map((c, idx) => {
              const gmailUrl = buildGmailUrl(c);

              return (
                <Grid item xs={12} md={6} key={idx}>
                  <Card
                    sx={{
                      height: "100%",
                      border: "2px solid #ddd",
                      borderRadius: 2,
                      transition: "all 0.3s",
                      "&:hover": {
                        boxShadow: 6,
                        borderColor: "#667eea",
                      },
                    }}
                  >
                    <CardContent>
                      {/* Header */}
                      <Typography variant="h6" sx={{ color: "#667eea", mb: 1 }}>
                        {idx + 1}. {c.name}
                      </Typography>

                      <Typography
                        variant="body2"
                        color="text.secondary"
                        sx={{ mb: 1 }}
                      >
                        {c.role_en} ({c.role})
                      </Typography>

                      {/* Experience & Match */}
                      <Box
                        sx={{
                          bgcolor: "#d4edda",
                          p: 1.5,
                          borderRadius: 1,
                          mb: 2,
                        }}
                      >
                        <Typography variant="body2">
                          <strong>Experience:</strong> {c.experience_years}{" "}
                          years | <strong>Match:</strong> {c.match_score}%
                        </Typography>
                      </Box>

                      {/* Contact - Gmail Button */}
                      {gmailUrl ? (
                        <Box
                          sx={{
                            bgcolor: "#e3f2fd",
                            p: 2,
                            borderRadius: 1,
                            mb: 2,
                            borderLeft: "4px solid #667eea",
                          }}
                        >
                          <Typography variant="body2" sx={{ mb: 1 }}>
                            <strong>Contact:</strong> {c.email}
                          </Typography>
                          <Button
                            variant="contained"
                            href={gmailUrl}
                            target="_blank"
                            fullWidth
                            sx={{
                              background:
                                "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                              textTransform: "none",
                              fontWeight: "bold",
                            }}
                          >
                            Send Interview Invitation
                          </Button>
                          <Typography
                            variant="caption"
                            display="block"
                            sx={{ mt: 1, color: "text.secondary" }}
                          >
                            Click to compose professional interview email
                          </Typography>
                        </Box>
                      ) : (
                        <Typography
                          variant="body2"
                          sx={{ mb: 2, color: "error.main" }}
                        >
                          Email: Not provided
                        </Typography>
                      )}

                      {/* Details */}
                      <Typography variant="body2" sx={{ mb: 0.5 }}>
                        <strong>Industry:</strong> {c.industry} - {c.category}
                      </Typography>

                      {c.phone && (
                        <Typography variant="body2" sx={{ mb: 0.5 }}>
                          <strong>Phone:</strong>{" "}
                          <a
                            href={`tel:${c.phone}`}
                            style={{ color: "#0077B6" }}
                          >
                            {c.phone}
                          </a>
                        </Typography>
                      )}

                      <Typography variant="body2" sx={{ mb: 0.5 }}>
                        <strong>Salary:</strong> €{c.salary?.toLocaleString()}
                        /month
                      </Typography>

                      <Typography variant="body2" sx={{ mb: 0.5 }}>
                        <strong>Location:</strong> {c.location?.city} (
                        {c.location?.postal_code})
                      </Typography>

                      <Typography variant="body2" sx={{ mb: 0.5 }}>
                        <strong>Availability:</strong> {c.availability}
                      </Typography>

                      <Typography variant="body2" sx={{ mb: 1 }}>
                        <strong>Education:</strong> {c.education?.level} -{" "}
                        {c.education?.institution}
                      </Typography>

                      {/* Skills */}
                      <Typography variant="body2" sx={{ mb: 0.5 }}>
                        <strong>Skills:</strong>
                      </Typography>
                      <Box
                        sx={{
                          display: "flex",
                          flexWrap: "wrap",
                          gap: 0.5,
                          mb: 1,
                        }}
                      >
                        {c.skills?.map((s, i) => (
                          <Chip label={s} size="small" key={i} />
                        ))}
                      </Box>

                      <Typography variant="body2" sx={{ mb: 0.5 }}>
                        <strong>Licenses:</strong>{" "}
                        {c.licenses?.map((l) => l.name).join(", ") || "None"}
                      </Typography>

                      <Typography variant="body2" sx={{ mb: 1 }}>
                        <strong>Languages:</strong>{" "}
                        {c.languages
                          ?.map((l) => `${l.language} (${l.proficiency})`)
                          .join(", ") || "N/A"}
                      </Typography>

                      {/* Summary */}
                      <Typography
                        variant="body2"
                        sx={{
                          mb: 1,
                          fontStyle: "italic",
                          color: "text.secondary",
                        }}
                      >
                        <strong>Summary:</strong> {c.summary}
                      </Typography>

                      <Typography variant="body2" sx={{ mb: 1 }}>
                        <strong>TES:</strong> {c.applicable_tes || "N/A"}
                      </Typography>

                      {/* Qualification Issues */}
                      {c.qualification_issues &&
                      c.qualification_issues.length > 0 ? (
                        <Box
                          sx={{
                            p: 1.5,
                            bgcolor: "#fff3cd",
                            borderLeft: "4px solid #ffc107",
                            borderRadius: 1,
                            mb: 1,
                          }}
                        >
                          <Typography variant="body2">
                            <strong>Qualification Issues:</strong>{" "}
                            {c.qualification_issues.join(", ")}
                          </Typography>
                        </Box>
                      ) : (
                        <Box
                          sx={{
                            p: 1,
                            bgcolor: "#d4edda",
                            borderLeft: "4px solid #28a745",
                            borderRadius: 1,
                            mb: 1,
                          }}
                        >
                          <Typography variant="body2">
                            No qualification issues
                          </Typography>
                        </Box>
                      )}

                      {/* Match Analysis */}
                      {c.explanation && (
                        <Box
                          sx={{
                            p: 1.5,
                            bgcolor: "#fffbeb",
                            borderLeft: "4px solid #f59e0b",
                            borderRadius: 1,
                          }}
                        >
                          <Typography variant="body2">
                            <strong>Match Analysis:</strong> {c.explanation}
                          </Typography>
                        </Box>
                      )}
                    </CardContent>
                  </Card>
                </Grid>
              );
            })}
          </Grid>
        </Box>
      )}

      {/* Reset Button */}
      {step === "Complete" && (
        <Box sx={{ mt: 4, textAlign: "center" }}>
          <Button
            variant="outlined"
            onClick={handleReset}
            sx={{ textTransform: "none" }}
          >
            🔄 Start New Voice Search
          </Button>
        </Box>
      )}
    </Box>
  );
};

export default App;
