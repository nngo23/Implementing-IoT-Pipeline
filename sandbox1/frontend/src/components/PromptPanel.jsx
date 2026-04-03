import React from "react";
import { Box, TextField, Alert } from "@mui/material";

const PromptPanel = ({ mainPrompt, setMainPrompt }) => {
  return (
    <Box sx={{ display: "flex", flexDirection: "column", gap: 2, p: 2 }}>
      <Alert severity="info" sx={{ mb: 1 }}>
        Please enter all job requirements and criteria in the box below
      </Alert>

      <TextField
        label="Job Description & Criteria"
        placeholder="Include location, experience, skills, education, salary, and must-have qualities..."
        multiline
        minRows={6}
        maxRows={12}
        value={mainPrompt}
        onChange={(e) => setMainPrompt(e.target.value)}
        fullWidth
      />
    </Box>
  );
};

export default PromptPanel;
