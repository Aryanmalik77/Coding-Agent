"""Introspection Engine for analyzing failures and finding alternative execution paths."""

from loguru import logger
from typing import Any, Dict, List, Optional
import traceback

class IntrospectionEngine:
    """
    Introspects failures, analyzes root causes, and suggests alternatives.
    """

    def __init__(self, identity_enc, evolution_tracker):
        self.identity = identity_enc
        self.evolution = evolution_tracker

    def introspect_failure(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a failure and return a diagnostic report with alternatives."""
        error_msg = str(error)
        tb = traceback.format_exc()
        
        logger.warning(f"Introspecting failure: {error_msg}")
        
        diagnosis = {
            "error_type": type(error).__name__,
            "message": error_msg,
            "root_cause": self._deduce_root_cause(error_msg, tb),
            "alternatives": self._find_alternatives(error_msg, context),
            "retry_recommended": self._should_retry(error_msg)
        }
        
        return diagnosis

    def _deduce_root_cause(self, msg: str, tb: str) -> str:
        """Heuristically deduce the root cause from error message and traceback."""
        msg_lower = msg.lower()
        if "connection" in msg_lower or "timeout" in msg_lower:
            return "Network or connectivity issue"
        if "permission" in msg_lower or "denied" in msg_lower:
            return "Administrative or permission restriction"
        if "not found" in msg_lower or "404" in msg_lower:
            return "Missing resource or invalid path"
        if "name" in msg_lower and "not defined" in msg_lower:
            return "Logic error (NameError)"
        return "Unknown architectural or runtime failure"

    def _find_alternatives(self, msg: str, context: Dict[str, Any]) -> List[str]:
        """Suggest alternative tools or strategies based on the failure."""
        msg_lower = msg.lower()
        alternatives = []
        
        # Example: if search fails, suggest direct crawling or different provider
        if "search" in msg_lower or "duckduckgo" in msg_lower:
            alternatives.append("Switch to 'scrape_url' if URLs are known")
            alternatives.append("Attempt direct domain crawling if site is known")
        
        # Example: if UI task fails, suggest DOM introspection
        if "ui" in msg_lower or "click" in msg_lower:
            alternatives.append("Use 'get_dom_tree' to locate element coordinates")
            alternatives.append("Wait for page stability then retry")
            
        if not alternatives:
            alternatives.append("Consult Identity Encyclopedia for similar historical successes")
            alternatives.append("Log detailed rationale and request user intervention with specific debug data")
            
        return alternatives

    def _should_retry(self, msg: str) -> bool:
        """Determine if an automatic retry is likely to succeed."""
        volatile_errors = ["timeout", "connection", "rate limit", "busy"]
        return any(v in msg.lower() for v in volatile_errors)
