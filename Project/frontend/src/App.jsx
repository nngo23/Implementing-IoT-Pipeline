import React, { useState } from "react";
import { Box, Button, Typography, Paper } from "@mui/material";
import FilterPanel from "./components/FilterPanel";
import PromptPanel from "./components/PromptPanel";
import CandidateList from "./components/CandidateList";
import { searchCandidates } from "./searchAPI";
import SearchIcon from "@mui/icons-material/Search";

const App = () => {
  // Filters
  const [filters, setFilters] = useState({
    salary_range: [0, 10000],
    industry: "",
    location_filter: null,
  });

  // Main prompt
  const [mainPrompt, setMainPrompt] = useState("");

  // Candidates from backend
  const [candidates, setCandidates] = useState([]);
  const [warning, setWarning] = useState("");
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  // Handle Search
  const handleSearch = async () => {
    if (!mainPrompt.trim()) {
      setWarning(
        "⚠️ Please enter a job description or criteria in the prompt!",
      );
      return;
    }
    setWarning("");
    setLoading(true);
    setSearched(true);

    const salaryObj = filters.salary_range
      ? { min: filters.salary_range[0], max: filters.salary_range[1] }
      : undefined;

    const payload = {
      query: mainPrompt,
      top_k: 5,
      industry: filters.industry || undefined,
      salary_range: salaryObj,
      location_filter: filters.location_filter || undefined,
    };

    try {
      const results = await searchCandidates(payload);
      setCandidates(results.results || []);
    } catch (error) {
      console.error(error);
      setWarning("Error fetching candidates from backend.");
      setCandidates([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box
      sx={{
        p: 3,
        minHeight: "100vh",
        position: "relative",
        backgroundColor: "#f7fafc", // subtle light gray background
      }}
    >
      {/* Header */}
      <Typography
        variant="h4"
        align="center"
        sx={{
          mb: 3,
          fontWeight: "bold",
          color: "#005bb6",
          letterSpacing: 1,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <SearchIcon sx={{ fontSize: 40, mr: 1 }} />
        Adaptive AI Candidate Search System
      </Typography>

      {/* Panels */}
      <Box sx={{ display: "flex", gap: 3, mb: 2 }}>
        {/* Filter Panel */}
        <Paper
          elevation={3}
          sx={{
            flex: 1,
            p: 2,
            backgroundColor: "#ffffff",
            borderRadius: 2,
          }}
        >
          <FilterPanel filters={filters} setFilters={setFilters} />
        </Paper>

        {/* Prompt Panel */}
        <Paper
          elevation={3}
          sx={{
            flex: 2,
            p: 2,
            backgroundColor: "#ffffff",
            borderRadius: 2,
          }}
        >
          <PromptPanel mainPrompt={mainPrompt} setMainPrompt={setMainPrompt} />
        </Paper>
      </Box>

      {/* Warning */}
      {warning && (
        <Typography color="error" sx={{ mt: 1, mb: 1, textAlign: "center" }}>
          {warning}
        </Typography>
      )}

      {/* Search Button */}
      <Box sx={{ display: "flex", justifyContent: "center", mb: 3 }}>
        <Button
          variant="contained"
          color="primary"
          onClick={handleSearch}
          sx={{
            px: 5,
            py: 1.5,
            fontWeight: "bold",
            fontSize: "1rem",
            borderRadius: 2,
            boxShadow: 3,
            "&:hover": {
              backgroundColor: "#00238d",
              boxShadow: 6,
            },
          }}
        >
          Search Candidates
        </Button>
      </Box>

      {/* Candidate Results */}
      <Paper
        elevation={3}
        sx={{
          mt: 2,
          p: 2,
          height: "450px",
          overflowY: "auto",
          borderRadius: 2,
          backgroundColor: "#ffffff",
        }}
      >
        {searched ? (
          <CandidateList
            candidates={candidates}
            loading={loading}
            searched={searched}
          />
        ) : (
          <Typography
            color="text.secondary"
            sx={{ mt: 1, textAlign: "center" }}
          >
            Set filters and enter a job description, then press "Search
            Candidates" to see results.
          </Typography>
        )}
      </Paper>
    </Box>
  );
};

export default App;
