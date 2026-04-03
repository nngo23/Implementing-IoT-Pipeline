# Teams Bot → FastAPI Payload Mapping

This document defines how Microsoft Teams Adaptive Card inputs are transformed
into FastAPI search requests. The payload MUST match the Web UI axios request.

---

## Search Endpoint

POST /api/v1/search

### Canonical Payload

```json
{
  "query": "string",
  "top_k": 5,
  "industry": "string | null",
  "salary_range": {
    "min": number | null,
    "max": number | null
  },
  "location_filter": number | null
}
```

## Feedback Endpoint

POST /api/v1/feedback

## Payload

```json
{
  "candidate_id": "string",
  "feedback_type": "up | down",
  "reason": "string | null"
}
```

This matches Web UI feedback logic exactly.

# Test Adaptive Cards in Teams App Studio (exact steps)

This is **mandatory** before backend wiring.

### Step-by-step (no guessing):

1. Open **Microsoft Teams**
2. Install **Developer Portal**
3. Go to **Tools → Adaptive Cards**
4. Paste each card JSON **one by one**
5. Click **Preview**
6. Fill inputs → **Submit**
7. Inspect **Submit payload**

### What you verify

✔ Input IDs are correct  
✔ Numbers submit as numbers  
✔ Empty fields submit as `null` / empty  
✔ No missing `step` field

### 🔴 Common mistake to avoid

```json
"salaryMin": ""
```
