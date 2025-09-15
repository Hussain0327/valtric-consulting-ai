"""
Consulting Frameworks Routes for ValtricAI Consulting Agent
"""

import logging
from fastapi import APIRouter, HTTPException, Depends
from api.dependencies import get_current_user, get_project_id

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/frameworks")
async def list_frameworks():
    """List available consulting frameworks"""
    return {
        "frameworks": [
            {
                "id": "swot",
                "name": "SWOT Analysis", 
                "description": "Strengths, Weaknesses, Opportunities, Threats analysis"
            },
            {
                "id": "porters",
                "name": "Porter's 5 Forces",
                "description": "Competitive rivalry, supplier/buyer power, substitution threats, barriers"
            },
            {
                "id": "mckinsey", 
                "name": "McKinsey 7S",
                "description": "Strategy, Structure, Systems, Skills, Staff, Style, Shared Values"
            }
        ]
    }


@router.get("/frameworks/{framework_id}")
async def get_framework_details(framework_id: str):
    """Get detailed information about a specific framework"""
    
    frameworks = {
        "swot": {
            "id": "swot",
            "name": "SWOT Analysis",
            "description": "Strategic planning technique for evaluating internal and external factors",
            "components": ["Strengths", "Weaknesses", "Opportunities", "Threats"],
            "use_cases": ["Strategic planning", "Competitive analysis", "Business assessment"]
        },
        "porters": {
            "id": "porters", 
            "name": "Porter's 5 Forces",
            "description": "Framework for analyzing industry competitiveness and profitability",
            "components": [
                "Competitive Rivalry",
                "Supplier Power", 
                "Buyer Power",
                "Threat of Substitution",
                "Barriers to Entry"
            ],
            "use_cases": ["Industry analysis", "Market entry", "Competitive positioning"]
        },
        "mckinsey": {
            "id": "mckinsey",
            "name": "McKinsey 7S",
            "description": "Organizational effectiveness framework for change management",
            "components": [
                "Strategy", "Structure", "Systems", "Skills", 
                "Staff", "Style", "Shared Values"
            ],
            "use_cases": ["Organizational design", "Change management", "Performance improvement"]
        }
    }
    
    if framework_id not in frameworks:
        raise HTTPException(status_code=404, detail="Framework not found")
    
    return frameworks[framework_id]