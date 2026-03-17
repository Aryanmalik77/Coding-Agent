"""Registry for all coding agent tools."""

from typing import Any, Dict
from coding_agent.tools.filesystem import ReadFileTool, WriteFileTool, EditFileTool, ListDirTool
from coding_agent.tools.evolution_tools import RecordEvolutionOutcomeTool, RevertToHistoricalVersionTool, AddEvolutionInsightTool
from coding_agent.tools.identity_tools import DocumentSystemComponentTool, RecordDesignPatternTool, QueryEncyclopediaTool
from coding_agent.tools.research_tools import BenchmarkDesignTool, AppreciateFeatureTool
from coding_agent.tools.coordination_tools import DelegateUITaskTool, RequestSwarmPlanningTool
from coding_agent.tools.research_web_tools import DeepResearchTool, ScrapeUrlTool
from coding_agent.tools.audit_tools import AuditHistoryTool
from coding_agent.tools.system_tools import ResourceAuditorTool
from coding_agent.tools.introspection_tools import IntrospectionTool
from coding_agent.tools.fortress_tools import FortressDiagnosticTool

class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, Any] = {}

    def register(self, tool: Any):
        self.tools[tool.name] = tool

    def get_tool(self, name: str) -> Any:
        return self.tools.get(name)

    def list_tools(self) -> list[dict]:
        return [
            {
                "name": t.name,
                "description": getattr(t, "description", t.name),
                "parameters": getattr(t, "parameters", {})
            }
            for t in self.tools.values()
        ]

def initialize_tools(agent: Any) -> ToolRegistry:
    registry = ToolRegistry()
    
    # Filesystem
    registry.register(ReadFileTool(agent.workspace))
    registry.register(WriteFileTool(agent.workspace, agent.evolution))
    registry.register(EditFileTool(agent.workspace, agent.evolution))
    registry.register(ListDirTool(agent.workspace))
    
    # Evolution
    registry.register(RecordEvolutionOutcomeTool(agent.evolution))
    registry.register(RevertToHistoricalVersionTool(agent.versioning))
    registry.register(AddEvolutionInsightTool(agent.evolution))
    
    # Identity
    registry.register(DocumentSystemComponentTool(agent.identity))
    registry.register(RecordDesignPatternTool(agent.identity))
    registry.register(QueryEncyclopediaTool(agent.identity))
    
    # Audit & Logging
    registry.register(AuditHistoryTool(agent.activity))

    # Advanced Web Research
    from coding_agent.research.scraper import Scraper
    from coding_agent.research.crawler import Crawler
    from coding_agent.research.search_agent import SearchAgent
    from coding_agent.tools.search_provider import DuckDuckGoSearchTool
    
    scraper = Scraper()
    # Pass the scraper instance to the crawler
    crawler = Crawler(scraper=scraper)
    search_tool = DuckDuckGoSearchTool()
    search_agent = SearchAgent(search_tool=search_tool, scraper=scraper, crawler=crawler, logging_hooks=agent.hooks)
    
    deep_research = DeepResearchTool(search_agent)
    registry.register(deep_research)
    registry.register(ScrapeUrlTool(scraper))
    
    # System & Environment
    registry.register(ResourceAuditorTool())
    registry.register(IntrospectionTool(agent))
    registry.register(FortressDiagnosticTool(agent.fortress, agent.activity))
    
    return registry
