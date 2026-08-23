"""
Analytics Router
Endpoints for query logs and placement statistics dashboard.
"""

from fastapi import APIRouter, Depends
from typing import List, Dict, Any

router = APIRouter(prefix="/analytics", tags=["Analytics"])


def get_rag_service():
    from ..main import rag_service
    return rag_service


@router.get("/queries")
async def get_recent_queries(limit: int = 25, service = Depends(get_rag_service)):
    """Returns recent queries with execution latency and source count."""
    return service.get_query_logs(limit=limit)


@router.get("/placements")
async def get_placement_summary():
    """Returns structured placement stats for the interactive Placement Dashboard."""
    return {
        "highest_package": "₹44.0 LPA",
        "average_it_ce": "₹8.5 LPA",
        "average_overall": "₹6.5 LPA",
        "placement_rate": "92%",
        "top_recruiters": [
            {"name": "Amazon", "type": "Product / Cloud", "tier": "Super Dream", "avg_ctc": "₹28-44 LPA"},
            {"name": "Morgan Stanley", "type": "Fintech / Investment Banking", "tier": "Super Dream", "avg_ctc": "₹24-30 LPA"},
            {"name": "Crest Data Systems", "type": "Cybersecurity & Data", "tier": "Dream", "avg_ctc": "₹7-12 LPA"},
            {"name": "Sophos", "type": "Network & Security", "tier": "Dream", "avg_ctc": "₹8-14 LPA"},
            {"name": "Reliance Industries (RIL)", "type": "Core & Energy", "tier": "Core Dream", "avg_ctc": "₹7.5-9 LPA"},
            {"name": "Atul Ltd / Aarti Ind", "type": "Chemical Manufacturing", "tier": "Core Core", "avg_ctc": "₹5-7 LPA"},
            {"name": "TCS (Ninja & Digital)", "type": "IT Services / Consulting", "tier": "Standard / Digital", "avg_ctc": "₹3.8-7.5 LPA"},
            {"name": "Infosys / Wipro / Capgemini", "type": "Global IT Solutions", "tier": "Standard", "avg_ctc": "₹4-6 LPA"}
        ],
        "branch_distribution": [
            {"branch": "Information Technology (IT)", "placed_pct": 95, "avg_lpa": 8.8},
            {"branch": "Computer Engineering (CE)", "placed_pct": 96, "avg_lpa": 9.1},
            {"branch": "Chemical Engineering (CH)", "placed_pct": 89, "avg_lpa": 6.2},
            {"branch": "Electronics & Comm (EC)", "placed_pct": 85, "avg_lpa": 6.0},
            {"branch": "Master of Computer Apps (MCA)", "placed_pct": 91, "avg_lpa": 7.2},
            {"branch": "Instrumentation & Control (IC)", "placed_pct": 82, "avg_lpa": 5.4}
        ]
    }
