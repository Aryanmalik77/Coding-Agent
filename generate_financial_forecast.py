"""Generates the Strategic Financial Forecast for Fortress Ecosystem."""

import asyncio
import json
from pathlib import Path
from coding_agent.fortress.engine import FortressEngine
from coding_agent.swarm.lmdb_store import LMDBStore

async def generate_forecast():
    print("--- Generating Strategic Financial Forecast ---")
    
    workspace = Path("c:/Users/HP/coding agent")
    store = LMDBStore(workspace)
    fortress = FortressEngine(store, workspace)
    
    keys = store.list_keys()
    obj_keys = [k for k in keys if k.startswith("fortress:objective:")]
    
    forecast_md = "# 📈 Fortress Strategic Financial Forecast\n\n"
    forecast_md += "Consolidated ROI and Resource Sustainability analysis for autonomous entities.\n\n"
    forecast_md += "| Objective | Daily Cost | Daily Revenue | ROI % | Sustainability |\n"
    forecast_md += "| :--- | :--- | :--- | :--- | :--- |\n"
    
    total_cost = 0.0
    total_revenue = 0.0
    
    for k in obj_keys:
        obj_id = k.split(":")[-1]
        obj = store.get(k)
        report = await fortress.calibrate_monetization(obj_id)
        
        if "error" in report: continue
        
        title = obj.get('title', obj_id).split(":")[0]
        forecast_md += f"| {title} | ${report['daily_run_cost']} | ${report['estimated_daily_revenue']} | {report['projected_roi_percent']}% | {report['sustainability_status']} |\n"
        
        total_cost += report['daily_run_cost']
        total_revenue += report['estimated_daily_revenue']

    forecast_md += f"\n---\n\n"
    forecast_md += f"### 📊 Ecosystem Totals (Projected)\n"
    forecast_md += f"- **Total Daily Burn**: ${total_cost:.2f}\n"
    forecast_md += f"- **Total Daily Revenue**: ${total_revenue:.2f}\n"
    forecast_md += f"- **Net Daily Profit**: ${total_revenue - total_cost:.2f}\n"
    forecast_md += f"- **Projected 30-Day Margin**: ${ (total_revenue - total_cost) * 30:.2f}\n\n"
    
    forecast_md += "> [!IMPORTANT]\n"
    forecast_md += "> This forecast assumes 100% operational uptime and linear revenue scaling. Resource costs are based on current heuristic models ($0.05/k cycles, $0.002/k tokens).\n"

    target_path = Path("C:/Users/HP/.gemini/antigravity/brain/dea61889-22c2-418b-9aa0-179cdbc5b71f/strategic_financial_forecast.md")
    target_path.write_text(forecast_md, encoding="utf-8")
    print(f"[SUCCESS] Forecast generated at {target_path}")

if __name__ == "__main__":
    asyncio.run(generate_forecast())
