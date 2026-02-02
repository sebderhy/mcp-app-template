"""Scenario modeler widget."""

from __future__ import annotations

import math
from copy import deepcopy
from typing import Any, Dict, List

import mcp.types as types
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from ._base import Widget, format_validation_error, get_invocation_meta

WIDGET = Widget(
    identifier="get_scenario_data",
    title="SaaS Scenario Modeler",
    description="""Interactive SaaS financial projection tool with scenario templates.

Use this tool when:
- The user wants to model SaaS business scenarios
- Projecting revenue, profit, and growth over 12 months
- Comparing different business strategies (bootstrapped, VC-funded, etc.)

Args:
    starting_mrr: Starting monthly recurring revenue in dollars (default: 50000)
    monthly_growth_rate: Monthly growth rate percentage (default: 5)
    monthly_churn_rate: Monthly churn rate percentage (default: 3)
    gross_margin: Gross margin percentage (default: 80)
    fixed_costs: Fixed monthly costs in dollars (default: 30000)

Returns:
    Interactive widget with sliders, 12-month projection chart, and comparison
    against 5 pre-built scenario templates (Bootstrapped, VC Rocketship, Cash Cow,
    Turnaround, Efficient Growth).

Example:
    get_scenario_data(starting_mrr=100000, monthly_growth_rate=15)""",
    template_uri="ui://widget/scenario-modeler.html",
    invoking="Loading scenario modeler...",
    invoked="Scenario modeler ready",
    component_name="scenario-modeler",
)


class ScenarioModelerInput(BaseModel):
    """Input for scenario modeler widget."""
    starting_mrr: float = Field(default=50000, alias="startingMRR", description="Starting MRR in dollars")
    monthly_growth_rate: float = Field(default=5, alias="monthlyGrowthRate", description="Monthly growth rate %")
    monthly_churn_rate: float = Field(default=3, alias="monthlyChurnRate", description="Monthly churn rate %")
    gross_margin: float = Field(default=80, alias="grossMargin", description="Gross margin %")
    fixed_costs: float = Field(default=30000, alias="fixedCosts", description="Fixed monthly costs")
    model_config = ConfigDict(populate_by_name=True, extra="forbid")


INPUT_MODEL = ScenarioModelerInput


def _calculate_projections(starting_mrr: float, monthly_growth_rate: float,
                           monthly_churn_rate: float, gross_margin: float,
                           fixed_costs: float) -> List[Dict[str, Any]]:
    """Calculate 12-month SaaS projections."""
    net_growth_rate = (monthly_growth_rate - monthly_churn_rate) / 100
    projections = []
    cumulative_revenue = 0.0
    for month in range(1, 13):
        mrr = starting_mrr * math.pow(1 + net_growth_rate, month)
        gross_profit = mrr * (gross_margin / 100)
        net_profit = gross_profit - fixed_costs
        cumulative_revenue += mrr
        projections.append({
            "month": month, "mrr": mrr, "grossProfit": gross_profit,
            "netProfit": net_profit, "cumulativeRevenue": cumulative_revenue,
        })
    return projections


def _calculate_summary(projections: List[Dict[str, Any]], starting_mrr: float) -> Dict[str, Any]:
    """Calculate summary metrics from projections."""
    ending_mrr = projections[11]["mrr"]
    total_revenue = sum(p["mrr"] for p in projections)
    total_profit = sum(p["netProfit"] for p in projections)
    mrr_growth_pct = ((ending_mrr - starting_mrr) / starting_mrr) * 100
    avg_margin = (total_profit / total_revenue) * 100 if total_revenue else 0
    break_even = next((p["month"] for p in projections if p["netProfit"] >= 0), 0)
    return {
        "endingMRR": ending_mrr, "arr": ending_mrr * 12,
        "totalRevenue": total_revenue, "totalProfit": total_profit,
        "mrrGrowthPct": mrr_growth_pct, "avgMargin": avg_margin,
        "breakEvenMonth": break_even,
    }


def _build_scenario_template(id: str, name: str, description: str, icon: str,
                              params: Dict[str, Any], key_insight: str) -> Dict[str, Any]:
    """Build a complete scenario template with projections and summary."""
    projections = _calculate_projections(**params)
    summary = _calculate_summary(projections, params["starting_mrr"])
    return {
        "id": id, "name": name, "description": description, "icon": icon,
        "parameters": {
            "startingMRR": params["starting_mrr"],
            "monthlyGrowthRate": params["monthly_growth_rate"],
            "monthlyChurnRate": params["monthly_churn_rate"],
            "grossMargin": params["gross_margin"],
            "fixedCosts": params["fixed_costs"],
        },
        "projections": projections, "summary": summary, "keyInsight": key_insight,
    }


SCENARIO_TEMPLATES = [
    _build_scenario_template("bootstrapped", "Bootstrapped Growth",
        "Low burn, steady growth, path to profitability", "🌱",
        {"starting_mrr": 30000, "monthly_growth_rate": 4, "monthly_churn_rate": 2,
         "gross_margin": 85, "fixed_costs": 20000},
        "Profitable by month 1, but slower scale"),
    _build_scenario_template("vc-rocketship", "VC Rocketship",
        "High burn, explosive growth, raise more later", "🚀",
        {"starting_mrr": 100000, "monthly_growth_rate": 15, "monthly_churn_rate": 5,
         "gross_margin": 70, "fixed_costs": 150000},
        "Loses money early but ends at 3x MRR"),
    _build_scenario_template("cash-cow", "Cash Cow",
        "Mature product, high margin, stable revenue", "🐄",
        {"starting_mrr": 80000, "monthly_growth_rate": 2, "monthly_churn_rate": 1,
         "gross_margin": 90, "fixed_costs": 40000},
        "Consistent profitability, low risk"),
    _build_scenario_template("turnaround", "Turnaround",
        "Fighting churn, rebuilding product-market fit", "🔄",
        {"starting_mrr": 60000, "monthly_growth_rate": 6, "monthly_churn_rate": 8,
         "gross_margin": 75, "fixed_costs": 50000},
        "Negative net growth requires urgent action"),
    _build_scenario_template("efficient-growth", "Efficient Growth",
        "Balanced approach with sustainable economics", "⚖️",
        {"starting_mrr": 50000, "monthly_growth_rate": 8, "monthly_churn_rate": 3,
         "gross_margin": 80, "fixed_costs": 35000},
        "Good growth with path to profitability"),
]

SCENARIO_DEFAULT_INPUTS = {
    "startingMRR": 50000, "monthlyGrowthRate": 5, "monthlyChurnRate": 3,
    "grossMargin": 80, "fixedCosts": 30000,
}


async def handle(widget: Widget, arguments: Dict[str, Any]) -> types.ServerResult:
    try:
        payload = ScenarioModelerInput.model_validate(arguments)
    except ValidationError as e:
        error_msg = format_validation_error(e, ScenarioModelerInput)
        return types.ServerResult(types.CallToolResult(
            content=[types.TextContent(type="text", text=error_msg)],
            isError=True,
        ))

    structured_content = {
        "templates": deepcopy(SCENARIO_TEMPLATES),
        "defaultInputs": SCENARIO_DEFAULT_INPUTS,
    }

    return types.ServerResult(types.CallToolResult(
        content=[types.TextContent(type="text", text=f"SaaS Scenario Modeler ({len(SCENARIO_TEMPLATES)} templates)")],
        structuredContent=structured_content,
        _meta=get_invocation_meta(widget),
    ))
