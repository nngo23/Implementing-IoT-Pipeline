import React from "react";
import { Box, Typography, Slider, TextField, MenuItem } from "@mui/material";

const industries = [
  "Teollisuus",
  "Logistiikka",
  "HoReCa",
  "Rakennusala",
  "Turvallisuusala",
  "Terveydenhuolto",
  "Satama-ala",
  "ICT / Teknologia",
  "Kemia / Labra",
  "Ilmailu",
  "Opetusala",
  "Puhtausala",
];

const FilterPanel = ({ filters, setFilters }) => {
  return (
    <Box sx={{ border: "1px solid #ccc", p: 2, borderRadius: 1 }}>
      <Typography variant="h6">Filters</Typography>

      {/* Salary Slider */}
      <Typography sx={{ mt: 2 }}>Salary (€ / month)</Typography>
      <Slider
        value={filters.salary_range || [0, 10000]}
        onChange={(_, newValue) =>
          setFilters({ ...filters, salary_range: newValue })
        }
        valueLabelDisplay="auto"
        min={0}
        max={10000}
      />

      {/* Industry Dropdown */}
      <TextField
        select
        label="Industry"
        fullWidth
        sx={{ mt: 2 }}
        value={filters.industry || ""}
        onChange={(e) => setFilters({ ...filters, industry: e.target.value })}
      >
        <MenuItem value="">All Industries</MenuItem>
        {industries.map((ind) => (
          <MenuItem key={ind} value={ind}>
            {ind}
          </MenuItem>
        ))}
      </TextField>

      {/* Location Filter */}
      <TextField
        type="number"
        label="Distance (km) from central Lahti 15500"
        fullWidth
        sx={{ mt: 2 }}
        value={filters.location_filter || ""}
        onChange={(e) =>
          setFilters({
            ...filters,
            location_filter: Number(e.target.value) || null,
          })
        }
      />
    </Box>
  );
};

export default FilterPanel;
