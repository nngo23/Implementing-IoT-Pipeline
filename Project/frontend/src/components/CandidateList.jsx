import React from "react";
import { Box, Typography } from "@mui/material";
import CandidateCard from "./CandidateCard";

const CandidateList = ({ candidates, loading, searched }) => {
  if (loading) {
    return (
      <Typography color="text.secondary" sx={{ mt: 1 }}>
        Loading candidates...
      </Typography>
    );
  }

  if (searched && candidates.length === 0) {
    return (
      <Typography color="text.secondary" sx={{ mt: 1 }}>
        No candidates found for this search.
      </Typography>
    );
  }

  return (
    <Box>
      {candidates.map((candidate) => (
        <CandidateCard key={candidate.id} candidate={candidate} />
      ))}
    </Box>
  );
};

export default CandidateList;
