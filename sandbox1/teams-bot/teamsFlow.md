# Teams Bot Conversation Flow – BOB

## 1. Greeting

Card: 01-greeting.json  
Purpose: Introduce BOB and explain what it does.

User action:

- Click "Start search"

---

## 2. Prompt / Minimum Criteria

Card: 02-criteria.json  
Inputs:

- query (job description, skills, requirements)

UX:

- Warning text: "More detail = better results"

---

## 3. Filters

Card: 03-filters.json  
Inputs:

- salaryMin
- salaryMax
- industry
- distanceKm

UX:

- Optional fields
- Helper text explaining each filter

---

## 4. Search Execution

Backend action:

- Bot builds payload (see payload-mapping.md)
- Calls FastAPI /search

---

## 5. Results

Card: 04-results.json  
Content:

- Max 5 candidates
- Match score
- Explanation
- 👍 / 👎 feedback buttons

---

## 6. Feedback Loop

User action:

- Submit feedback
  Backend:
- POST /feedback
- Used for AI learning

Conversation can restart from step 2.
