import React, { useState } from "react";
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  Chip,
  TextField,
} from "@mui/material";
import { sendFeedbackAPI } from "../searchAPI";

const CandidateCard = ({ candidate }) => {
  const [feedbackReason, setFeedbackReason] = useState("");
  const [showExplanation, setShowExplanation] = useState(false);

  // Handle feedback
  const handleFeedback = async (type) => {
    if (!candidate || !candidate.id) return;
    try {
      await sendFeedbackAPI({
        candidateId: candidate.id,
        feedbackType: type,
        reason: feedbackReason || null,
      });
      alert("Feedback sent successfully!");
      setFeedbackReason("");
    } catch (err) {
      console.error(err);
      alert("Failed to send feedback");
    }
  };

  // Handle no candidate
  if (!candidate) {
    return (
      <Card sx={{ mb: 2, borderRadius: 2, boxShadow: 2 }}>
        <CardContent>
          <Typography variant="body2" color="text.secondary">
            No candidates found for this search.
          </Typography>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card sx={{ mb: 2, borderRadius: 2, boxShadow: 2 }}>
      <CardContent>
        <Typography variant="h6">{candidate.name}</Typography>
        <Typography variant="subtitle2" color="text.secondary">
          {candidate.role} ·{" "}
          {candidate.location?.city || candidate.location?.postal_code}
        </Typography>

        <Box sx={{ mt: 1, mb: 1, display: "flex", alignItems: "center" }}>
          <Typography variant="body2" color="primary" fontWeight="bold">
            Match Score: {candidate.match_score ?? "N/A"}%
          </Typography>
          {candidate.explanation && (
            <Button
              size="small"
              onClick={() => setShowExplanation(!showExplanation)}
              sx={{ ml: 1 }}
            >
              {showExplanation ? "Hide" : "Show"} Explanation
            </Button>
          )}
        </Box>

        {showExplanation && candidate.explanation && (
          <Box sx={{ mb: 1 }}>
            <Typography variant="body2">{candidate.explanation}</Typography>
          </Box>
        )}

        <Box sx={{ mb: 1 }}>
          {candidate.skills?.map((skill) => (
            <Chip
              key={skill}
              label={skill}
              color="info"
              size="small"
              sx={{ mr: 0.5, mb: 0.5 }}
            />
          ))}
        </Box>

        <Box sx={{ display: "flex", gap: 1, mb: 1 }}>
          <Button
            variant="contained"
            color="success"
            size="small"
            onClick={() => handleFeedback("up")}
          >
            👍
          </Button>
          <Button
            variant="contained"
            color="error"
            size="small"
            onClick={() => handleFeedback("down")}
          >
            👎
          </Button>
        </Box>

        <TextField
          fullWidth
          size="small"
          placeholder="Optional explanation for your feedback"
          value={feedbackReason}
          onChange={(e) => setFeedbackReason(e.target.value)}
        />
      </CardContent>
    </Card>
  );
};

export default CandidateCard;
