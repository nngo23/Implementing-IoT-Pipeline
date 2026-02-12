from google import genai
from app.config import Config
from typing import List, Dict

# Initialize the client once
client = genai.Client()

class GeminiClient:
    def __init__(self):
        self.model = Config.GEMINI_MODEL  # e.g., "gemini-2.5-flash"

    def format_candidates(self, candidates: List[Dict]) -> str:
        """
        Format candidates to readable text for Gemini API.
        """
        formatted = ""
        for c in candidates:
            formatted += f"Name: {c.get('name')}\n"
            formatted += f"Role: {c.get('role')} ({c.get('role_en')})\n"
            formatted += f"Industry: {c.get('industry')} / {c.get('category')}\n"

            skills = c.get("skills", [])
            if skills:
                formatted += f"Skills: {', '.join(skills)}\n"

            formatted += f"Experience: {c.get('experience_years')} years\n"

            edu = c.get("education", {})
            if isinstance(edu, dict):
                parts = [
                    edu.get("level"),
                    edu.get("field"),
                    f"from {edu.get('institution')}"
                ]
                formatted += f"Education: {' '.join(filter(None, parts))}\n"

            add_edu = c.get("additional_education", [])
            if add_edu:
                edu_list = []
                for e in add_edu[:3]:
                    if isinstance(e, dict):
                        edu_list.append(f"{e.get('type', 'Degree')} in {e.get('name', '')}")
                formatted += "Advanced Qualifications: " + ", ".join(edu_list)
                if len(add_edu) > 3:
                    formatted += f" (+{len(add_edu)-3} more)"
                formatted += "\n"

            licenses = c.get("licenses", [])
            if licenses:
                formatted += f"Licenses: {', '.join([l.get('name', '') for l in licenses if isinstance(l, dict)])}\n"

            languages = c.get("languages", [])
            if languages:
                lang_list = []
                for lang in languages:
                    if isinstance(lang, dict):
                        language = lang.get("language")
                        prof = lang.get("proficiency")
                        if language:
                            lang_list.append(f"{language} ({prof})" if prof else language)
                formatted += f"Languages: {', '.join(lang_list)}\n"

            loc = c.get("location", {})
            if isinstance(loc, dict) and loc.get("city"):
                formatted += f"Location: {loc.get('city')}\n"

            salary = c.get("salary")
            if salary:
                formatted += f"Salary: €{salary:,}/month\n"

            if c.get("availability"):
                formatted += f"Availability: {c.get('availability')}\n"

            if c.get("summary"):
                formatted += f"Summary: {c.get('summary')}\n"

            score = c.get("score")
            if score is not None:
                formatted += f"Match Score: {score}%\n"

            formatted += "\n" + "-" * 80 + "\n\n"

        return formatted

    def generate_text(self, prompt: str, coming_candidates: List[Dict]) -> str:
        """
        Generate match explanations for candidates using Gemini
        """
        formatted_candidates = self.format_candidates(coming_candidates)

        full_prompt = f"""You are a professional recruitment assistant analyzing candidate matches.

Job requirement / search query: "{prompt}"

Here are the top matching candidates:

{formatted_candidates}

Your task:
- For EACH candidate, explain in 4-5 sentences why they match (or don't match) the job requirement
- Focus on: relevant experience, key skills, education level, licenses/certifications, language abilities, salary...
- Use the exact candidate name as provided
- Be specific and reference actual qualifications

Output format (strictly follow):
**Candidate Name 1**
4-5 sentence explanation...

**Candidate Name 2**
4-5 sentence explanation...

(No introduction or conclusion, just the list.)
"""

        try:
            # === Correct API call ===
            response = client.models.generate_content(
                model=self.model,
                contents=full_prompt
            )
            return response.text or ""
        except Exception as e:
            print("⚠️ Gemini generation failed:")
            import traceback
            traceback.print_exc()
            return ""


# Singleton instance
gemini_client = GeminiClient()
