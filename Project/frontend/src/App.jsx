import React, { useState } from "react";
import { Box, Button, Typography } from "@mui/material";
import FilterPanel from "./components/FilterPanel";
import PromptPanel from "./components/PromptPanel";
import CandidateList from "./components/CandidateList";
import { searchCandidates } from "./searchAPI";
import SearchIcon from "@mui/icons-material/Search";

const App = () => {
  // Filters
  const [filters, setFilters] = useState({
    salary_range: [0, 10000], // min/max
    industry: "",
    location_filter: null,
  });

  // Single big prompt
  const [mainPrompt, setMainPrompt] = useState("");

  // Candidates from backend
  const [candidates, setCandidates] = useState([]);
  const [warning, setWarning] = useState("");
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false); // tracks if search button pressed

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
    <Box sx={{ p: 2, minHeight: "100vh", position: "relative" }}>
      {/* Header */}
      <Typography
        variant="h4"
        align="center"
        sx={{
          mb: 3,
          fontWeight: "bold",
          color: "#0077B6", // Ocean blue
          letterSpacing: 1,
        }}
      >
        <SearchIcon sx={{ fontSize: 40 }} /> Candidate Search System
      </Typography>

      {/* Panels */}
      <Box sx={{ display: "flex", gap: 2 }}>
        <Box sx={{ flex: 1 }}>
          <FilterPanel filters={filters} setFilters={setFilters} />
        </Box>
        <Box sx={{ flex: 2 }}>
          <PromptPanel mainPrompt={mainPrompt} setMainPrompt={setMainPrompt} />
        </Box>
      </Box>

      {/* Warning */}
      {warning && (
        <Typography color="error" sx={{ mt: 1 }}>
          {warning}
        </Typography>
      )}

      {/* Search button */}
      <Box sx={{ display: "flex", justifyContent: "center", mt: 2 }}>
        <Button variant="contained" onClick={handleSearch}>
          Search Candidates
        </Button>
      </Box>

      {/* Candidate results */}
      <Box sx={{ mt: 2, height: "400px", overflowY: "auto", pr: 1 }}>
        {searched ? (
          <CandidateList
            candidates={candidates}
            loading={loading}
            searched={searched}
          />
        ) : (
          <Typography color="text.secondary" sx={{ mt: 1 }}>
            Set filters and enter a job description and press "Search
            Candidates" to see results.
          </Typography>
        )}
      </Box>
    </Box>
  );
};

export default App;
