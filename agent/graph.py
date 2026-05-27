from langgraph.graph import END, START, StateGraph

from agent.nodes.evaluate_answer import evaluate_answer_node
from agent.nodes.fetch_session import fetch_session_node
from agent.nodes.generate_question import generate_question_node
from agent.state import InterviewState
from logger import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Routing functions
# ---------------------------------------------------------------------------


def route_after_fetch(state: InterviewState) -> str:
    """
    Decides the next node after session data is loaded.

    - Error  → stop immediately.
    - start  → generate the first question.
    - answer → evaluate the submitted answer.
    """
    if state.get("error"):
        return "end"

    return "generate_question" if state.get("mode") == "start" else "evaluate_answer"


def route_after_evaluation(state: InterviewState) -> str:
    """
    Decides what happens after an answer is evaluated.

    - Error or interview complete (all 6 done) → stop.
    - More questions remaining                 → generate next question.
    """
    if state.get("error") or state.get("is_interview_complete"):
        return "end"

    return "generate_question"


# ---------------------------------------------------------------------------
# Graph factory
# ---------------------------------------------------------------------------


def create_interview_graph() -> StateGraph:
    """
    Builds and compiles the LangGraph interview agent.

    Topology::

        START
          │
          ▼
        fetch_session ──(error)──────────────────────────► END
          │
          ├──(mode=start)──► generate_question ──────────► END
          │
          └──(mode=answer)─► evaluate_answer
                               │
                               ├──(more questions)──► generate_question ──► END
                               │
                               └──(all 6 done)──────────────────────────► END

    evaluate_answer handles session completion internally when all 6 questions
    are answered — no extra node needed.
    """
    graph = StateGraph(InterviewState)

    # Register nodes
    graph.add_node("fetch_session", fetch_session_node)
    graph.add_node("generate_question", generate_question_node)
    graph.add_node("evaluate_answer", evaluate_answer_node)

    # Entry point
    graph.add_edge(START, "fetch_session")

    # Routing after fetch
    graph.add_conditional_edges(
        "fetch_session",
        route_after_fetch,
        {
            "generate_question": "generate_question",
            "evaluate_answer": "evaluate_answer",
            "end": END,
        },
    )

    # Routing after evaluation
    graph.add_conditional_edges(
        "evaluate_answer",
        route_after_evaluation,
        {
            "generate_question": "generate_question",
            "end": END,
        },
    )

    # Terminal edge
    graph.add_edge("generate_question", END)

    return graph.compile()
