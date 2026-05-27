from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from constants import GROQ_MODEL, GROQ_TEMPERATURE_EVALUATION, GROQ_TEMPERATURE_QUESTION
from schemas.agent import AnswerEvaluation, GeneratedQuestion


async def generate_interview_question(
    session_data: dict,
    question_no: int,
    taxonomy: dict,
    history_context: str,
    groq_api_key: str,
) -> GeneratedQuestion:
    """Calls Groq LLM to generate one interview question at the given Bloom's taxonomy level."""
    llm = ChatGroq(api_key=groq_api_key, model=GROQ_MODEL, temperature=GROQ_TEMPERATURE_QUESTION)
    structured_llm = llm.with_structured_output(GeneratedQuestion)

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """You are an expert technical interviewer conducting a structured professional interview.
Generate exactly one interview question targeting the specified Bloom's Taxonomy level.
The question must be directly relevant to the candidate's role and stated skill set.
Keep the language conversational but technically rigorous.
Do not repeat topics already covered in the conversation history.""",
        ),
        (
            "human",
            """Candidate Profile:
- Name: {name}
- Target Role: {job_role}
- Experience: {experience}
- Skills: {skills_set}
- Education: {highest_qualification}

Bloom's Taxonomy Level: {taxonomy_level} — {taxonomy_name}
Description: {taxonomy_description}
Action verbs to guide question style: {taxonomy_verbs}

This is Question {question_no} of 6.

Recent Conversation History:
{history_context}

Generate one question appropriate for this taxonomy level.""",
        ),
    ])

    return await (prompt | structured_llm).ainvoke({
        "name": session_data["name"],
        "job_role": session_data["job_role"],
        "experience": session_data["experience"],
        "skills_set": session_data["skills_set"],
        "highest_qualification": session_data["highest_qualification"],
        "taxonomy_level": taxonomy["level"],
        "taxonomy_name": taxonomy["name"],
        "taxonomy_description": taxonomy["description"],
        "taxonomy_verbs": taxonomy["verb_hints"],
        "question_no": question_no,
        "history_context": history_context,
    })


async def evaluate_candidate_answer(
    session_data: dict,
    question_text: str,
    answer_text: str,
    taxonomy_level: str,
    groq_api_key: str,
) -> AnswerEvaluation:
    """Calls Groq LLM to score and provide feedback on a candidate's answer."""
    llm = ChatGroq(api_key=groq_api_key, model=GROQ_MODEL, temperature=GROQ_TEMPERATURE_EVALUATION)
    structured_llm = llm.with_structured_output(AnswerEvaluation)

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """You are a senior technical interviewer objectively evaluating a candidate's response.
Score from 0 to 10 based on accuracy, depth, and relevance.
Be specific and constructive in your feedback.
Adjust expectations relative to the candidate's stated experience level.""",
        ),
        (
            "human",
            """Candidate Profile:
- Target Role: {job_role}
- Experience: {experience}
- Skills: {skills_set}

Bloom's Level: {taxonomy_level}
Question: {question}

Candidate's Answer: {answer}

Evaluate the answer and provide a score out of 10 with detailed feedback.""",
        ),
    ])

    return await (prompt | structured_llm).ainvoke({
        "job_role": session_data["job_role"],
        "experience": session_data["experience"],
        "skills_set": session_data["skills_set"],
        "taxonomy_level": taxonomy_level,
        "question": question_text,
        "answer": answer_text,
    })
