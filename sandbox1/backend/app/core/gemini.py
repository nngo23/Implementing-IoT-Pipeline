from google import genai
from google.genai.errors import ClientError
from app.config import Config
from typing import List, Dict
import logging
import time

logger = logging.getLogger(__name__)


class GeminiClient:
    FALLBACK_MODEL = "models/gemini-2.5-flash"  # Known working model for generateContent

    def __init__(self):
        self.client = genai.Client(api_key=Config.GEMINI_API_KEY)
        self.model = Config.GEMINI_MODEL or self.FALLBACK_MODEL

    def format_candidates(self, candidates: List[Dict]) -> str:
        """Format candidates to readable text for Gemini API"""
        formatted = ""
        for candidate in candidates:
            formatted += f"Name: {candidate.get('name')}\n"
            formatted += f"Role: {candidate.get('role')} ({candidate.get('role_en')})\n"
            formatted += f"Industry: {candidate.get('industry')} / {candidate.get('category')}\n"

            # Skills
            skills = candidate.get("skills", [])
            if skills:
                formatted += f"Skills: {', '.join(skills)}\n"

            # Experience
            formatted += f"Experience: {candidate.get('experience_years')} years\n"

            # Education
            education = candidate.get("education", {})
            if isinstance(education, dict):
                edu_parts = [
                    education.get("level"),
                    education.get("field"),
                    f"from {education.get('institution')}"
                ]
                formatted += f"Education: {' '.join(filter(None, edu_parts))}\n"

            # Additional education
            additional_edu = candidate.get("additional_education", [])
            if additional_edu:
                formatted += "Advanced Qualifications: "
                edu_list = []
                for edu in additional_edu[:3]:
                    if isinstance(edu, dict):
                        edu_type = edu.get("type", "Degree")
                        edu_name = edu.get("name", "")
                        if edu_name:
                            edu_list.append(f"{edu_type} in {edu_name}")
                formatted += ", ".join(edu_list)
                if len(additional_edu) > 3:
                    formatted += f" (+{len(additional_edu)-3} more)"
                formatted += "\n"

            # Licenses
            licenses = candidate.get("licenses", [])
            if licenses:
                license_names = [
                    lic.get("name", "") for lic in licenses if isinstance(lic, dict)
                ]
                formatted += f"Licenses: {', '.join(filter(None, license_names))}\n"

            # Languages
            languages = candidate.get("languages", [])
            if languages:
                lang_list = []
                for lang in languages:
                    if isinstance(lang, dict):
                        language = lang.get("language")
                        proficiency = lang.get("proficiency")
                        if language:
                            lang_list.append(f"{language} ({proficiency})" if proficiency else language)
                formatted += f"Languages: {', '.join(lang_list)}\n"

            # Location
            location = candidate.get("location", {})
            if isinstance(location, dict):
                city = location.get("city")
                if city:
                    formatted += f"Location: {city}\n"

            # Salary
            salary = candidate.get("salary")
            if salary:
                formatted += f"Salary: €{salary:,}/month\n"

            # Availability
            availability = candidate.get("availability")
            if availability:
                formatted += f"Availability: {availability}\n"

            # Summary
            summary = candidate.get("summary")
            if summary:
                formatted += f"Summary: {summary}\n"

            # Score
            score = candidate.get("score")
            if score is not None:
                formatted += f"Match Score: {score}%\n"

            formatted += "\n" + "-" * 80 + "\n\n"

        return formatted

    def generate_text(self, prompt: str, coming_candidates: List[Dict]) -> str:
        """Generate match explanations for candidates using Gemini"""

        formatted_candidates = self.format_candidates(coming_candidates)

        full_prompt = f"""You are a professional recruitment assistant analyzing candidate matches.

Job requirement / search query: "{prompt}"

Here are the top matching candidates:

{formatted_candidates}

Your task:
- For EACH candidate, explain in 4-5 sentences why they match (or don't match)
- Focus on: experience, skills, education, certifications, languages, salary
- Use exact candidate name
- Be specific and reference actual data

Output format (STRICT):
**Candidate Name**
4-5 sentence explanation...

(No intro, no conclusion)
"""

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=full_prompt
            )
            return response.text or ""

        except ClientError as e:
            error_msg = str(e).lower()
            # Auto-fallback to known working model if current one fails
            if "404" in error_msg:
                if self.model != self.FALLBACK_MODEL:
                    logger.warning(
                        "Gemini model %s not found. Falling back to %s.",
                        self.model, self.FALLBACK_MODEL
                    )
                    self.model = self.FALLBACK_MODEL
                    # Retry once
                    try:
                        response = self.client.models.generate_content(
                            model=self.model,
                            contents=full_prompt
                        )
                        return response.text or ""
                    except Exception as e2:
                        logger.error("Fallback Gemini model also failed: %s", e2)
                        return "AI explanation temporarily unavailable (model error)."
                else:
                    return "AI explanation temporarily unavailable (model error)."

            if "429" in error_msg:
                logger.warning("Gemini quota exceeded → skipping call")
                return "AI explanation temporarily unavailable (quota reached)."

            logger.error("Gemini ClientError: %s", e)
            return "AI explanation temporarily unavailable (client error)."

        except Exception as e:
            logger.error("Unexpected Gemini error: %s", e)
            return "AI explanation unavailable due to unexpected error."


# Singleton client
gemini_client = GeminiClient()