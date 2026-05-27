from typing import List
from pydantic import BaseModel, Field


class GeneratedQuestion(BaseModel):
    """Structured output schema used when the LLM generates an interview question."""

    question: str = Field(description="The interview question to present to the candidate")
    taxonomy_level: str = Field(description="Bloom's taxonomy level name for this question")
    difficulty_rationale: str = Field(
        description="Brief explanation of why this question fits the taxonomy level"
    )


class AnswerEvaluation(BaseModel):
    """Structured output schema used when the LLM evaluates a candidate's answer."""

    score: float = Field(ge=0, le=10, description="Numeric score out of 10")
    evaluation_feedback: str = Field(
        description="Detailed narrative feedback on the candidate's response"
    )
    key_points_covered: List[str] = Field(
        description="Key points the candidate addressed correctly"
    )
    missing_points: List[str] = Field(
        description="Important points the candidate failed to mention"
    )


class InterviewReport(BaseModel):
    """Structured output schema used when the LLM generates the final interview report."""

    overall_score: float = Field(ge=0, le=10, description="Overall score out of 10")
    final_feedback: str = Field(
        description="Comprehensive narrative feedback covering the entire interview"
    )
    hire_recommendation: str = Field(
        description=(
            "Hiring decision — must be exactly one of: "
            "Strongly Recommend | Recommend | Neutral | Not Recommended"
        )
    )
    key_strengths: List[str] = Field(description="Top strengths demonstrated by the candidate")
    areas_for_improvement: List[str] = Field(
        description="Specific areas where the candidate should develop further"
    )
