from typing import Dict, List

# ---------------------------------------------------------------------------
# Bloom's Taxonomy — 6 levels used to structure interview questions.
# Questions are generated in order from level 1 (Remember) to 6 (Create),
# progressively raising the cognitive demand placed on the candidate.
# ---------------------------------------------------------------------------
TAXONOMY_LEVELS: List[Dict] = [
    {
        "level": 1,
        "name": "Remember",
        "description": "Recall basic facts, definitions, and foundational knowledge",
        "verb_hints": "Define, list, recall, identify, name, state",
    },
    {
        "level": 2,
        "name": "Understand",
        "description": "Explain concepts in own words, summarise, and interpret",
        "verb_hints": "Explain, describe, summarise, interpret, classify, compare",
    },
    {
        "level": 3,
        "name": "Apply",
        "description": "Use knowledge in real-world or new situations",
        "verb_hints": "Implement, use, execute, solve, demonstrate, apply",
    },
    {
        "level": 4,
        "name": "Analyze",
        "description": "Break down information, identify patterns and relationships",
        "verb_hints": "Analyze, differentiate, compare, break down, examine, contrast",
    },
    {
        "level": 5,
        "name": "Evaluate",
        "description": "Make judgments, justify decisions, critique approaches",
        "verb_hints": "Evaluate, justify, assess, critique, recommend, defend",
    },
    {
        "level": 6,
        "name": "Create",
        "description": "Design, construct, or produce new solutions and ideas",
        "verb_hints": "Design, construct, develop, formulate, plan, produce",
    },
]

# ---------------------------------------------------------------------------
# Candidate profile options — rendered as dropdowns in the registration form
# ---------------------------------------------------------------------------
JOB_ROLES: List[str] = [
    "Software Engineer",
    "Frontend Developer",
    "Backend Developer",
    "Full Stack Developer",
    "Data Scientist",
    "Machine Learning Engineer",
    "DevOps Engineer",
    "Cloud Engineer",
    "Product Manager",
    "UI/UX Designer",
    "QA Engineer",
    "Mobile Developer",
]

EDUCATION_QUALIFICATIONS: List[str] = [
    "High School",
    "Diploma",
    "Bachelor's Degree",
    "Master's Degree",
    "PhD",
    "Professional Certification",
    "Self-Taught",
]

# ---------------------------------------------------------------------------
# LLM configuration
# ---------------------------------------------------------------------------
GROQ_MODEL: str = "llama-3.3-70b-versatile"
GROQ_TEMPERATURE_QUESTION: float = 0.7   # Higher creativity for question generation
GROQ_TEMPERATURE_EVALUATION: float = 0.3  # Lower variance for consistent scoring

# ---------------------------------------------------------------------------
# Interview rules
# ---------------------------------------------------------------------------
TOTAL_QUESTIONS: int = 6          # One question per Bloom's taxonomy level
MAX_SCORE_PER_QUESTION: float = 10.0

# ---------------------------------------------------------------------------
# Sarvam AI endpoints and defaults
# ---------------------------------------------------------------------------
SARVAM_TTS_URL: str = "https://api.sarvam.ai/text-to-speech"
SARVAM_STT_URL: str = "https://api.sarvam.ai/speech-to-text"
SARVAM_TTS_SPEAKER: str = "anushka"
SARVAM_LANGUAGE_CODE: str = "en-IN"
SARVAM_TTS_MODEL: str = "bulbul:v2"

# ---------------------------------------------------------------------------
# Hire recommendation thresholds (based on overall average score out of 10)
# ---------------------------------------------------------------------------
HIRE_THRESHOLDS: Dict[str, float] = {
    "Strongly Recommend": 8.0,
    "Recommend": 6.5,
    "Neutral": 5.0,
    "Not Recommended": 0.0,
}
