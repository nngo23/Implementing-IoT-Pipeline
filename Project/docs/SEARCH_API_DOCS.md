# Candidate Search API Documentation

## Table of Contents
- [Introduction](#introduction)
- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [Usage Examples](#usage-examples)

---

## Introduction

Backend API for a candidate search system using vector search and AI. The API provides intelligent candidate matching based on job descriptions with detailed AI-generated explanations.

**Tech Stack:**
- FastAPI (Python web framework)
- Qdrant (Vector database)
- Sentence Transformers (Text embeddings)
- Google Gemini AI (Explanation generation)

---

## System Requirements

- Python 3.12+
- Docker & Docker Compose
- Google Gemini API Key
- 4GB+ RAM (for embedding model)

---

## Installation

### Install dependencies
```bash
pip install -r requirements.txt
```

**requirements.txt:**
```txt
fastapi==0.121.1
uvicorn[standard]==0.38.0
pydantic==2.12.4
qdrant-client==1.16.2
sentence-transformers==5.2.0
google-genai==1.56.0
python-dotenv==1.2.1
```

---

## Configuration

### 1. Setup Qdrant Database

**Important:** You need to run the Qdrant database from the `TokenSandbox` repository before starting the backend.

#### Step 1: Navigate to TokenSandbox repository
```bash
cd path/to/TokenSandbox
```

#### Step 2: Start Qdrant using Docker Compose
```bash
docker compose -f docker-compose.db.yml up -d
```

#### Step 3: Verify Qdrant is running
```bash
docker ps
```

You should see a container named `qdrant-dev` running on port `6333`.

#### Step 4: Test Qdrant connection
```bash
curl http://localhost:6333/collections
```

### 2. Create `.env` file

Create a `.env` file at the same level as `app`, `scripts`, `tests`, and `data` folders. The content of the `.env` file will be provided separately.

---

## Running the Application

### Prerequisites Checklist

Before running the backend, ensure:
- Qdrant container is running (`docker ps` shows `qdrant-dev`)
- `.env` file is created with valid configuration
- Dependencies are installed (`pip install -r requirements.txt`)

### Development Mode
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Options:**
- `--reload`: Auto-reload on code changes
- `--host 0.0.0.0`: Allow external connections
- `--port 8000`: Specify port (default: 8000)

### Production Mode
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Verify Server is Running

Test the health check endpoint:
```bash
curl http://localhost:8000/api/v1/health
```

---

## API Endpoints

### Base URL
```
http://localhost:8000/api/v1
```

### 1. Health Check

**Endpoint:** `GET /health`

**Description:** Check the health status of the service and Qdrant connection

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "qdrant": {
    "status": "ok",
    "collection": "candidates"
  }
}
```

**Status Codes:**
- `200 OK`: Service is healthy

---

### 2. Search Candidates

**Endpoint:** `POST /search`

**Description:** Search for candidates matching a job description

**Request Body:**
```json
{
  "query": "Looking for the best developers who can work for blockchain company",
  "top_k": 5
}
```

**Parameters:**
| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| query | string | Yes | - | The search query string (job description or requirements) |
| top_k | integer | No | 5 | Number of top results to return (1-50) |
| salary_range | object | No | null | Desired salary range with 'min' and 'max' keys (in EUR/month) |
| industry | string | No | null | For filtering search results by industry, please use the industry names in Finnish (e.g., "Teollisuus", "Terveydenhuolto") |
| location_filter | float | No | null | Search radius in kilometers from candidate location (e.g., 30.0) |

**Response:**
```json
{
  "query": "Looking for experienced welder with ISO 9606-1 certification who can work with MIG/MAG and TIG welding methods. Especially who lives near the company. Let me know they live how far from the company",
  "results": [
        {
            "id": "candidate_079",
            "name": "Markku Pääkkönen",
            "industry": "Teollisuus",
            "category": "Industry",
            "role": "Hitsaaja",
            "role_en": "Welder",
            "skills": [
                "Puikkohitsaus",
                "Teräsrakenteet",
                "Paineastiat",
                "NDT-tarkastus"
            ],
            "experience_years": 16,
            "education": {
                "level": "Ammattitutkinto",
                "institution": "Salpaus",
                "field": "Hitsaus"
            },
            "additional_education": [
                {
                    "type": "Certification",
                    "name": "ISO 9606-1 (paineastiat)",
                    "institution": "Inspecta",
                    "year": 2017
                },
                {
                    "type": "Certification",
                    "name": "EN 287",
                    "institution": "International",
                    "year": 2020
                }
            ],
            "licenses": [
                {
                    "name": "ISO 9606-1 pätevyyskoe",
                    "issuing_authority": "Inspecta"
                },
                {
                    "name": "Työturvallisuuskortti",
                    "issuing_authority": "Työturvallisuuskeskus"
                }
            ],
            "location": {
                "city": "Lahti",
                "postal_code": "15140",
                "coordinates": {
                    "lat": 60.9827,
                    "lon": 25.6612
                }
            },
            "languages": [
                {
                    "language": "Finnish",
                    "proficiency": "native"
                },
                {
                    "language": "English",
                    "proficiency": "intermediate"
                },
                {
                    "language": "German",
                    "proficiency": "basic"
                }
            ],
            "salary": 6000,
            "availability": "2 weeks",
            "applicable_tes": "Teollisuusliitto - Teknologiateollisuus",
            "summary": "Markku Pääkkönen on paineastiahitsauksen huippuosaaja, jolla on laaja kokemus teräsrakenteista ja NDT-tarkastuksista.",
            "qualification_issues": [],
            "match_score": 43.48,
            "explanation": "Markku is a highly experienced welder with 16 years in the industry and holds the crucial ISO 9606-1 certification, specifically for pressure vessels, alongside an EN 287 certification. While his skills list \"Puikkohitsaus,\" it doesn't explicitly mention MIG/MAG or TIG, which is a potential gap for a core requirement. He is located in Lahti, suggesting close proximity to the company, fulfilling the location preference. His salary expectation of €6,000/month is significantly higher than other candidates, which might be a factor."
        },
        {
            "id": "candidate_056",
            "name": "Minna Saarinen",
            "industry": "Teollisuus",
            "category": "Industry",
            "role": "Hitsaaja",
            "role_en": "Welder",
            "skills": [
                "Alumiinihitsaus",
                "TIG",
                "MIG",
                "Laadunvalvonta"
            ],
            "experience_years": 9,
            "education": {
                "level": "Ammattitutkinto",
                "institution": "Salpaus",
                "field": "Hitsaus"
            },
            "additional_education": [],
            "licenses": [
                {
                    "name": "ISO 9606-1 pätevyyskoe",
                    "issuing_authority": "Inspecta"
                },
                {
                    "name": "Työturvallisuuskortti",
                    "issuing_authority": "Työturvallisuuskeskus"
                }
            ],
            "location": {
                "city": "Orimattila",
                "postal_code": "16300",
                "coordinates": {
                    "lat": 60.8049,
                    "lon": 25.7298
                }
            },
            "languages": [
                {
                    "language": "Finnish",
                    "proficiency": "native"
                },
                {
                    "language": "English",
                    "proficiency": "basic"
                }
            ],
            "salary": 3900,
            "availability": "2 weeks",
            "applicable_tes": "Teollisuusliitto - Teknologiateollisuus",
            "summary": "Minna Saarinen on tarkka alumiinihitsaaja, jolla on vahva laadunvalvonnan osaaminen.",
            "qualification_issues": [],
            "match_score": 43.39,
            "explanation": "Minna offers 9 years of experience and is well-qualified with ISO 9606-1 certification. Crucially, she explicitly lists both TIG and MIG welding among her skills, directly matching the required methods. She is located in Orimattila, which is a short distance from Lahti, indicating acceptable proximity to the company. Her salary expectation of €3,900/month appears reasonable for her experience and specific skill set."
        },
        {
            "id": "candidate_039",
            "name": "Erkki Laitinen",
            "industry": "Teollisuus",
            "category": "Industry",
            "role": "Hitsaaja",
            "role_en": "Welder",
            "skills": [
                "TIG-hitsaus",
                "Ruostumaton teräs",
                "Piirustukset"
            ],
            "experience_years": 7,
            "education": {
                "level": "Ammattitutkinto",
                "institution": "Ammattiopisto",
                "field": "Metalliala"
            },
            "additional_education": [],
            "licenses": [
                {
                    "name": "Työturvallisuuskortti",
                    "issuing_authority": "Työturvallisuuskeskus"
                }
            ],
            "location": {
                "city": "Lahti",
                "postal_code": "15200",
                "coordinates": {
                    "lat": 60.9827,
                    "lon": 25.6612
                }
            },
            "languages": [
                {
                    "language": "Finnish",
                    "proficiency": "native"
                }
            ],
            "salary": 3500,
            "availability": "immediate",
            "applicable_tes": "Teollisuusliitto - Teknologiateollisuus",
            "summary": "Erkki Laitinen on TIG-hitsauksen osaaja, mutta ISO 9606-1 -pätevyystodistus puuttuu vaadituista menetelmistä.",
            "qualification_issues": [
                "Puuttuva ISO 9606-1 pätevyyskoe"
            ],
            "match_score": 41.66,
            "explanation": "Erkki has 7 years of welding experience and is skilled in TIG welding, which is one of the required methods. However, he notably lacks the ISO 9606-1 certification, as explicitly stated in his summary, which is a critical mismatch for a core job requirement. While he is conveniently located in Lahti, offering ideal proximity, this deficiency in certification makes him a less suitable candidate. His salary expectation of €3,500/month is competitive."
        },
        {
            "id": "candidate_027",
            "name": "Ari Jokela",
            "industry": "Teollisuus",
            "category": "Industry",
            "role": "Hitsaaja",
            "role_en": "Welder",
            "skills": [
                "MIG/MAG-hitsaus",
                "TIG-hitsaus",
                "Puikkohitsaus",
                "Piirustusten luku"
            ],
            "experience_years": 11,
            "education": {
                "level": "Ammattitutkinto",
                "institution": "Salpaus",
                "field": "Hitsaus"
            },
            "additional_education": [],
            "licenses": [
                {
                    "name": "ISO 9606-1 pätevyyskoe",
                    "issuing_authority": "Inspecta"
                },
                {
                    "name": "Työturvallisuuskortti",
                    "issuing_authority": "Työturvallisuuskeskus"
                }
            ],
            "location": {
                "city": "Lahti",
                "postal_code": "15200",
                "coordinates": {
                    "lat": 60.9827,
                    "lon": 25.6612
                }
            },
            "languages": [
                {
                    "language": "Finnish",
                    "proficiency": "native"
                }
            ],
            "salary": 3800,
            "availability": "2 weeks",
            "applicable_tes": "Teollisuusliitto - Teknologiateollisuus",
            "summary": "Ari Jokela on tarkka ja kokenut hitsaaja, joka hallitsee useita menetelmiä ja piirustusten tulkinnan.",
            "qualification_issues": [],
            "match_score": 39.57,
            "explanation": "Ari is a strong match, boasting 11 years of experience and holding the required ISO 9606-1 certification. He explicitly lists both MIG/MAG-hitsaus and TIG-hitsaus among his skills, directly fulfilling the key welding method requirements. He is conveniently located in Lahti, offering close proximity to the company as requested. His salary expectation of €3,800/month is competitive and reasonable given his qualifications and experience."
        },
        {
            "id": "candidate_095",
            "name": "Jouni Kallinen",
            "industry": "Teollisuus",
            "category": "Industry",
            "role": "Hitsaaja",
            "role_en": "Welder",
            "skills": [
                "Puikkohitsaus",
                "Teräsrakenteet",
                "Piirustukset"
            ],
            "experience_years": 6,
            "education": {
                "level": "Peruskoulu",
                "institution": "-",
                "field": "-"
            },
            "additional_education": [],
            "licenses": [
                {
                    "name": "Työturvallisuuskortti",
                    "issuing_authority": "Työturvallisuuskeskus"
                }
            ],
            "location": {
                "city": "Lahti",
                "postal_code": "15170",
                "coordinates": {
                    "lat": 60.9827,
                    "lon": 25.6612
                }
            },
            "languages": [
                {
                    "language": "Finnish",
                    "proficiency": "native"
                }
            ],
            "salary": 3400,
            "availability": "immediate",
            "applicable_tes": "Teollisuusliitto - Teknologiateollisuus",
            "summary": "Jouni Kallinen on puikkohitsauksen osaaja, mutta ISO-pätevyys puuttuu vaadituista menetelmistä.",
            "qualification_issues": [
                "Puuttuva ISO 9606-1 pätevyyskoe"
            ],
            "match_score": 35.94,
            "explanation": "Jouni has 6 years of experience, primarily in stick welding (Puikkohitsaus) and working with steel structures. A significant drawback is that he lacks the essential ISO 9606-1 certification, as clearly noted in his summary, which is a core requirement for the role. Furthermore, his profile does not indicate experience or skills in either MIG/MAG or TIG welding methods. While he is located in Lahti, offering good proximity, his qualifications do not align with the core demands of the position."
        }
    ]
}
```

**Status Codes:**
- `200 OK`: Success
- `404 Not Found`: No candidates found
- `422 Validation Error`: Invalid request body
- `500 Internal Server Error`: Server error

---

## Usage Examples

### Example 1: Health Check with cURL
```bash
curl http://localhost:8000/api/v1/health
```

### Example 2: Search with cURL
```bash
curl -X POST "http://localhost:8000/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Looking for experienced welder with ISO 9606-1 certification who can work with MIG/MAG and TIG welding methods. Especially who lives near the company. Let me know they live how far from the company",
    "top_k": 3,
    "salary_range": {"min":3000,"max":6000},
    "industry": "Teollisuus",
    "location_filter": 40.5
  }'
```

### Example 3: JavaScript (Fetch API)
```javascript
const searchCandidates = async () => {
  const response = await fetch('http://localhost:8000/api/v1/search', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      "query": "Looking for experienced welder with ISO 9606-1 certification who can work with MIG/MAG and TIG welding methods. Especially who lives near the company. Let me know they live how far from the company",
      "top_k": 3,
      "salary_range": {"min":3000,"max":6000},
      "industry": "Teollisuus",
      "location_filter": 40.5
    })
  });

  const data = await response.json();
  console.log(data);
};

searchCandidates();
```

### Example 4: Python (Requests)
```python
import requests

url = "http://localhost:8000/api/v1/search"
payload = {
    "query": "Looking for experienced welder with ISO 9606-1 certification who can work with MIG/MAG and TIG welding methods. Especially who lives near the company. Let me know they live how far from the company",
    "top_k": 3,
    "salary_range": {"min":3000,"max":6000},
    "industry": "Teollisuus",
    "location_filter": 40.5
}

response = requests.post(url, json=payload)
data = response.json()
print(data)
```

### Example 5: Axios (React/Vue)
```javascript
import axios from 'axios';

const searchCandidates = async (query, topK = 5, industry, salary_range, location_filter) => {
  try {
    const response = await axios.post('http://localhost:8000/api/v1/search', {
      query: query,
      top_k: topK,
      industry: industry,
      salary_range: salary_range,
      location_filter: location_filter
    });
    return response.data;
  } catch (error) {
    console.error('Error:', error.response?.data || error.message);
    throw error;
  }
};

// Usage
searchCandidates('Blockchain developer', 5)
  .then(data => console.log(data))
  .catch(error => console.error(error));
```

---
