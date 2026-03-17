from typing import List, Dict

class PromptManager:
    """
    Handles prompt construction for sub-agents.
    Ensures that deep identity awareness is kept in the Encyclopedia
    and not injected into the active system prompts.
    """

    @staticmethod
    def build_system_prompt(base_prompt: str, task_context: str) -> str:
        """
        Builds a lean system prompt.
        Encourages tools usage for retrieving architectural context.
        """
        prompt = (
            f"{base_prompt}\n\n"
            "## OPERATIONAL GUIDES\n"
            "- You have access to an 'Identity Encyclopedia' via `query_encyclopedia`.\n"
            "- For any architectural decisions or system design questions, USE THE TOOL to retrieve context.\n"
            "- DO NOT assume knowledge of the full swarm architecture without querying.\n"
            f"\n### CURRENT TASK CONTEXT\n{task_context}"
        )
        return prompt

    @staticmethod
    def build_self_modification_prompt(rationale: str) -> str:
        """Prompt used when the agent is asked to refactor its own code."""
        return (
            "You are performing a self-modification task.\n"
            f"REQUIRED RATIONALE: {rationale}\n"
            "You must ensure that any change is documented in the Evolution Tracker and "
            "aligns with the design patterns found in the Encyclopedia."
        )
