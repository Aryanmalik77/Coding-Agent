"""Due Diligence Agent: Analyzes intent against real-world constraints."""

from pathlib import Path
from typing import Dict, List, Any, Optional
from coding_agent.subagents.base_agent import BaseSubagent

from coding_agent.swarm.graph_store import GraphStore
from coding_agent.subagents.keyword_extraction_agent import KeywordExtractionAgent

class DueDiligenceAgent(BaseSubagent):
    def __init__(self, project_path: Path, workspace: Optional[Path] = None):
        super().__init__(project_path)
        self.diligence_log = "DILIGENCE_AUDIT.md"
        self.workspace = workspace
        self.knowledge_engine = GraphStore(workspace) if workspace else None
        self.extractor = KeywordExtractionAgent()

    async def audit_intent(self, intent: str, constraints: Dict[str, Any], fortress_engine: Any) -> Dict[str, Any]:
        """
        Analyze user intent against mathematical, physical, and systemic limits.
        Consult historical case studies for comparative evidence via Hybrid Search.
        """
        report = {
            "intent": intent,
            "feasibility_score": 100.0,
            "violations": [],
            "alternatives": [],
            "precedents": [],
            "status": "Optimal"
        }

        # 0. Consult Knowledge Engine for Precedents
        if self.knowledge_engine:
            # 0. Extract high-essence keywords for search
            search_terms = self.extractor.get_search_keywords(intent)
            
            precedent_set = set()
            for term in search_terms:
                # Use hybrid search (Lexical + Semantic)
                studies = await self.knowledge_engine.hybrid_search("CaseStudy", term)
                for s in studies:
                    precedent_set.add(f"Case Study: {s.get('title')} - Results: {s.get('benchmark_results')}")
            
            report["precedents"] = list(precedent_set)

        # 1. Mathematical/Algorithmic Analysis
        math_limit = constraints.get("mathematical_limit", "O(2^n)")
        if "O(2^n)" in math_limit and ("large" in intent.lower() or "llm" in intent.lower()):
            report["feasibility_score"] -= 40
            report["violations"].append("Algorithmic complexity O(2^n) is non-viable for large-scale operations (Mathematical Limit).")
            report["alternatives"].append("Switch to O(n log n) approximation or heuristic search.")

        # 2. Physical/Hardware Analysis
        hw_limits = constraints.get("hardware", {})
        if hw_limits.get("max_ram_gb", 16) < 8 and ("train" in intent.lower() or "llm" in intent.lower()):
            report["feasibility_score"] -= 50
            report["violations"].append("Insufficient RAM for training/running large models (Physical Limit).")
            report["alternatives"].append("Utilize quantized models (4-bit) or cloud compute clusters.")

        # 3. Network/Latency Analysis
        network = constraints.get("network", {})
        if network.get("max_latency_ms", 500) > 100 and ("trading" in intent.lower() or "real-time" in intent.lower()):
            report["feasibility_score"] -= 30
            report["violations"].append("Network latency too high for real-time high-frequence intent (Network Limit).")
            report["alternatives"].append("Deploy edge-computing nodes closer to exchange gateways.")

        if report["feasibility_score"] < 70:
            report["status"] = "At Risk / Sub-optimal"

        # 4. Fortress Alignment Interaction
        alignment_note = f"Due Diligence Audit: {report['status']} (Score: {report['feasibility_score']})"
        fortress_engine.record_diligence_audit(intent, report) # Register the audit event
        
        # Log the report locally
        self._log_report(report)
        
        return report

    def _log_report(self, report: Dict[str, Any]):
        """Persist the diligence report to the local context."""
        content = f"# Due Diligence Audit Report\n\n"
        content += f"## Intent: {report['intent']}\n"
        content += f"**Status**: {report['status']} | **Feasibility Score**: {report['feasibility_score']}/100\n\n"
        
        if report["precedents"]:
            content += "### Comparative Evidence (Knowledge Vault)\n"
            for p in report["precedents"]:
                content += f"- 🔍 {p}\n"
            content += "\n"

        if report["violations"]:
            content += "### Detected Constraints & Violations\n"
            for v in report["violations"]:
                content += f"- ⚠️ {v}\n"
        
        if report["alternatives"]:
            content += "\n### Suggested Alternative Designs\n"
            for a in report["alternatives"]:
                content += f"- ✅ {a}\n"
                
        self.write_context_file(self.diligence_log, content)
