import React, { useState, useCallback } from "react";
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
  Skeleton,
} from "@mui/material";
import WaveRecorder from "./components/WaveRecorder";

// ── Gmail compose helper ─────────────────────────────────────────────────────

const buildGmailUrl = (candidate) => {
  if (!candidate.email) return null;
  const subject = encodeURIComponent(
    `Interview Invitation - ${candidate.role_en} Position`,
  );
  const body = encodeURIComponent(
    `Dear ${candidate.name},\n\n` +
      `Thank you for your interest in the ${candidate.role_en} position.\n\n` +
      `We would like to invite you for an interview.\n\n` +
      `Position: ${candidate.role_en}\n` +
      `Date: [Please specify]\nTime: [Please specify]\n\n` +
      `Best regards,\nHR Department`,
  );
  return `https://mail.google.com/mail/?view=cm&fs=1&to=${candidate.email}&su=${subject}&body=${body}`;
};

// ── Candidate card ───────────────────────────────────────────────────────────

const CandidateCard = React.memo(({ candidate, rank, explanationLoading }) => {
  const gmailUrl = buildGmailUrl(candidate);

  return (
    <Card
      sx={{
        height: "100%",
        border: "2px solid #ddd",
        borderRadius: 2,
        transition: "box-shadow 0.3s, border-color 0.3s",
        "&:hover": { boxShadow: 6, borderColor: "#667eea" },
      }}
    >
      <CardContent>
        <Typography variant="h6" sx={{ color: "#667eea", mb: 1 }}>
          {rank}. {candidate.name}
        </Typography>

        <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
          {candidate.role_en} ({candidate.role})
        </Typography>

        {/* Score + experience */}
        <Box sx={{ bgcolor: "#d4edda", p: 1.5, borderRadius: 1, mb: 2 }}>
          <Typography variant="body2">
            <strong>Experience:</strong> {candidate.experience_years} yrs
            &nbsp;|&nbsp;
            <strong>Match:</strong> {candidate.match_score}%
          </Typography>
        </Box>

        {/* Gmail button */}
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
              <strong>Contact:</strong> {candidate.email}
            </Typography>
            <Button
              variant="contained"
              href={gmailUrl}
              target="_blank"
              fullWidth
              sx={{
                background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                textTransform: "none",
                fontWeight: "bold",
              }}
            >
              Send interview invitation
            </Button>
          </Box>
        ) : (
          <Typography variant="body2" sx={{ mb: 2, color: "error.main" }}>
            Email: Not provided
          </Typography>
        )}

        {/* Details */}
        <Typography variant="body2" sx={{ mb: 0.5 }}>
          <strong>Industry:</strong> {candidate.industry} — {candidate.category}
        </Typography>
        <Typography variant="body2" sx={{ mb: 0.5 }}>
          <strong>Salary:</strong> €{candidate.salary?.toLocaleString()}/month
        </Typography>
        <Typography variant="body2" sx={{ mb: 0.5 }}>
          <strong>Location:</strong> {candidate.location?.city} (
          {candidate.location?.postal_code})
        </Typography>
        <Typography variant="body2" sx={{ mb: 0.5 }}>
          <strong>Availability:</strong> {candidate.availability}
        </Typography>
        <Typography variant="body2" sx={{ mb: 1 }}>
          <strong>Education:</strong> {candidate.education?.level} —{" "}
          {candidate.education?.institution}
        </Typography>

        {/* Skills */}
        <Typography variant="body2" sx={{ mb: 0.5 }}>
          <strong>Skills:</strong>
        </Typography>
        <Box sx={{ display: "flex", flexWrap: "wrap", gap: 0.5, mb: 1 }}>
          {candidate.skills?.map((s, i) => (
            <Chip key={i} label={s} size="small" />
          ))}
        </Box>

        <Typography variant="body2" sx={{ mb: 0.5 }}>
          <strong>Licenses:</strong>{" "}
          {candidate.licenses?.map((l) => l.name).join(", ") || "None"}
        </Typography>
        <Typography variant="body2" sx={{ mb: 1 }}>
          <strong>Languages:</strong>{" "}
          {candidate.languages
            ?.map((l) => `${l.language} (${l.proficiency})`)
            .join(", ") || "N/A"}
        </Typography>

        {/* Qualification issues */}
        {candidate.qualification_issues?.length > 0 ? (
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
              <strong>Qualification issues:</strong>{" "}
              {candidate.qualification_issues.join(", ")}
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
            <Typography variant="body2">No qualification issues</Typography>
          </Box>
        )}

        {/* AI explanation — skeleton while loading */}
        <Box
          sx={{
            p: 1.5,
            bgcolor: "#fffbeb",
            borderLeft: "4px solid #f59e0b",
            borderRadius: 1,
          }}
        >
          <Typography variant="body2" sx={{ mb: 0.5 }}>
            <strong>Match analysis:</strong>
          </Typography>
          {explanationLoading ? (
            <>
              <Skeleton variant="text" width="100%" />
              <Skeleton variant="text" width="90%" />
              <Skeleton variant="text" width="80%" />
            </>
          ) : (
            <Typography variant="body2">
              {candidate.explanation || "AI explanation unavailable."}
            </Typography>
          )}
        </Box>
      </CardContent>
    </Card>
  );
});

// ── App ──────────────────────────────────────────────────────────────────────

const App = () => {
  const [voiceText, setVoiceText] = useState("");
  const [step, setStep] = useState("Idle");
  const [distribution, setDistribution] = useState("slack");
  const [recipientEmail, setRecipientEmail] = useState("");
  const [candidates, setCandidates] = useState([]);
  const [explanationsReady, setExplanationsReady] = useState(false);
  const [error, setError] = useState(null);

  const isProcessing = ["Recording", "Transcribing", "Searching"].includes(
    step,
  );
  const isLoadingExplanations = step === "Complete" && !explanationsReady;

  // ── Handlers ───────────────────────────────────────────────────────────────

  const handleCandidates = useCallback(({ transcription, results }) => {
    setVoiceText(transcription ?? "");
    setCandidates(results ?? []);
    setExplanationsReady(false);
    setError(null);
  }, []);

  const handleExplanationPatch = useCallback((patches) => {
    // patches: { [candidateId]: explanationString }
    setCandidates((prev) =>
      prev.map((c) =>
        patches[c.id] ? { ...c, explanation: patches[c.id] } : c,
      ),
    );
    setExplanationsReady(true);
  }, []);

  const handleError = useCallback((msg) => {
    setError(msg);
  }, []);

  const handleReset = () => {
    setVoiceText("");
    setCandidates([]);
    setExplanationsReady(false);
    setError(null);
    setStep("Idle");
  };

  // ── Render ─────────────────────────────────────────────────────────────────

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
        <div>
          {" "}
          Record a voice command to search candidates. For best results, clearly
          mention:
        </div>
        <div>
          • A specific role (e.g. "welder", "nurse", "software developer")
        </div>
        <div>• Optional filters like salary or distance from Lahti 15520</div>
        <div>Examples:</div>
        <div>• "Show software developers within 20 km"</div>
        <div>• "Top nurses between 2500 to 3500"</div>
        <div>
          Results will be sent via Slack or Email and displayed below.
          Candidates appear in about 1 min; AI analysis follows automatically.
        </div>
      </Typography>

      {/* Controls */}
      <Box sx={{ maxWidth: 600, mx: "auto", mb: 4 }}>
        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" sx={{ mb: 1 }}>
            Distribution channel:
          </Typography>
          <Select
            value={distribution}
            onChange={(e) => setDistribution(e.target.value)}
            disabled={isProcessing}
            fullWidth
          >
            <MenuItem value="slack">Slack – Team channel</MenuItem>
            <MenuItem value="email">Email distribution</MenuItem>
          </Select>
        </Box>

        {distribution === "email" && (
          <Box sx={{ mb: 3 }}>
            <TextField
              label="Recipient email"
              fullWidth
              value={recipientEmail}
              onChange={(e) => setRecipientEmail(e.target.value)}
              disabled={isProcessing}
              placeholder="recipient@example.com"
            />
          </Box>
        )}

        <Box sx={{ textAlign: "center", mb: 2 }}>
          <WaveRecorder
            onCandidates={handleCandidates}
            onExplanationPatch={handleExplanationPatch}
            onError={handleError}
            setStep={setStep}
            distribution={distribution}
            recipientEmail={recipientEmail}
          />
        </Box>

        {/* Status row */}
        <Box sx={{ textAlign: "center" }}>
          <Typography variant="body2" color="text.secondary">
            Status:{" "}
            <strong>
              {isLoadingExplanations ? "Generating AI analysis…" : step}
            </strong>
          </Typography>
          {(isProcessing || isLoadingExplanations) && (
            <Box sx={{ mt: 2 }}>
              <CircularProgress size={24} />
            </Box>
          )}
        </Box>

        {/* Error / warning */}
        {error && (
          <Box
            sx={{
              mt: 3,
              p: 2.5,
              bgcolor: "#fff3f3",
              border: "1px solid #ffcdd2",
              borderRadius: 2,
              textAlign: "center",
            }}
          >
            <Typography variant="body1" color="error">
              {error}
            </Typography>
          </Box>
        )}

        {/* Transcription */}
        {voiceText && (
          <Box sx={{ mt: 3, p: 2, bgcolor: "#f5f5f5", borderRadius: 2 }}>
            <Typography variant="body2" color="text.secondary">
              Transcription:
            </Typography>
            <Typography variant="body1" sx={{ fontStyle: "italic", mt: 1 }}>
              "{voiceText}"
            </Typography>
          </Box>
        )}
      </Box>

      {/* Candidate grid */}
      {candidates.length > 0 && (
        <Box sx={{ mt: 4 }}>
          <Typography variant="h5" sx={{ mb: 1, fontWeight: "bold" }}>
            Top {candidates.length} candidates
          </Typography>
          {isLoadingExplanations && (
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Candidate data is ready. AI match analysis is generating…
            </Typography>
          )}

          <Grid container spacing={3}>
            {candidates.map((c, idx) => (
              <Grid item xs={12} md={6} key={c.id ?? idx}>
                <CandidateCard
                  candidate={c}
                  rank={idx + 1}
                  explanationLoading={isLoadingExplanations}
                />
              </Grid>
            ))}
          </Grid>
        </Box>
      )}

      {(step === "Complete" || (step === "Idle" && error)) && (
        <Box sx={{ mt: 4, textAlign: "center" }}>
          <Button
            variant="outlined"
            onClick={handleReset}
            sx={{ textTransform: "none" }}
          >
            🔄 Start new voice search
          </Button>
        </Box>
      )}
    </Box>
  );
};

export default App;
