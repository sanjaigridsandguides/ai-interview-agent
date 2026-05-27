"""
Generates and saves the LangGraph interview agent flow as a PNG image.

Run from the project root after activating the virtual environment:

    python generate_graph.py

The output file ``agent_flow.png`` will be created in the project root.
If PNG generation fails (e.g. missing browser dependency for Mermaid rendering),
a fallback ``agent_flow.md`` containing the Mermaid diagram source is saved instead.
"""

import os

from agent.graph import create_interview_graph
from logger import get_logger

logger = get_logger(__name__)


def generate_agent_flow_image(output_path: str = "agent_flow.png") -> None:
    """
    Renders the compiled LangGraph agent as a PNG and saves it to disk.

    Args:
        output_path: Destination file path for the PNG image.
    """
    logger.info("Compiling interview agent graph...")
    graph = create_interview_graph()

    try:
        png_bytes: bytes = graph.get_graph().draw_mermaid_png()

        with open(output_path, "wb") as f:
            f.write(png_bytes)

        logger.info("Agent flow diagram saved to: %s", os.path.abspath(output_path))

    except Exception as exc:
        logger.warning("PNG generation failed (%s) — saving Mermaid source instead", exc)

        mermaid_source: str = graph.get_graph().draw_mermaid()
        fallback_path = output_path.replace(".png", ".md")

        with open(fallback_path, "w") as f:
            f.write("# AI Interview Agent — Graph Flow\n\n")
            f.write("```mermaid\n")
            f.write(mermaid_source)
            f.write("\n```\n")

        logger.info("Mermaid diagram source saved to: %s", os.path.abspath(fallback_path))


if __name__ == "__main__":
    generate_agent_flow_image()
