from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from pydantic import BaseModel

router = APIRouter(prefix="/api/mother", tags=["Mother Workspace API"])

# In-memory store for shopping list additions
MOTHER_STATE = {
    "shopping_items": [
        {"id": 1, "name": "Organic Milk", "quantity": "2 Liters", "isPriority": False},
        {"id": 2, "name": "Fresh Spinach", "quantity": "1 bunch", "isPriority": True},
        {"id": 3, "name": "Rohu Fish", "quantity": "1 kg", "isPriority": True},
        {"id": 4, "name": "Basmati Rice", "quantity": "5 kg", "isPriority": False},
        {"id": 5, "name": "Whole Wheat Bread", "quantity": "1 loaf", "isPriority": False},
        {"id": 6, "name": "Farm Eggs", "quantity": "1 dozen", "isPriority": True}
    ],
    "budget": {
        "spent": 1417.0,
        "budget": 3000.0,
        "status": "Within Budget"
    },
    "pantry": {
        "health": 79,
        "lowStockCount": 6
    },
    "waste": {
        "amount": "1.2 kg",
        "status": "Stable"
    },
    "meals": {
        "days": "7 Days",
        "badge": "90% Ingredient match"
    },
    "alerts": {
        "count": 20,
        "badge": "Active"
    },
    "insights": {
        "insight": "Zepto has a 10% discount on vegetables today. We need Spinach and Onions for the planned chicken curry."
    },
    "expiring": [
        {"name": "Rohu Fish", "days": 0, "status": "Expired"},
        {"name": "Spinach", "days": 1, "status": "Expiring"},
        {"name": "Fresh Chicken", "days": 2, "status": "Expiring"}
    ],
    "report": "Pantry Check: Weekly inventory audit completed. | Waste Monitor: Milk carton expired. | Smart Shopping: List generated automatically based on 6 low stock items."
}

class ShoppingItemCreate(BaseModel):
    name: str
    quantity: str = "1 unit"
    isPriority: bool = False

@router.get("/dashboard")
@router.get("/report")
def get_report():
    return {"report": MOTHER_STATE["report"]}

@router.get("/budget")
def get_budget():
    return MOTHER_STATE["budget"]

@router.get("/pantry")
def get_pantry():
    return MOTHER_STATE["pantry"]

@router.get("/shopping")
def get_shopping():
    return {
        "totalCount": len(MOTHER_STATE["shopping_items"]),
        "badge": "Smart Auto-List",
        "items": MOTHER_STATE["shopping_items"]
    }

@router.post("/shopping")
def add_shopping_item(item: ShoppingItemCreate):
    new_item = {
        "id": len(MOTHER_STATE["shopping_items"]) + 1,
        "name": item.name,
        "quantity": item.quantity,
        "isPriority": item.isPriority
    }
    MOTHER_STATE["shopping_items"].append(new_item)
    return {"success": True, "item": new_item}

@router.get("/waste")
def get_waste():
    return MOTHER_STATE["waste"]

@router.get("/meals")
def get_meals():
    return MOTHER_STATE["meals"]

@router.get("/alerts")
def get_alerts():
    return MOTHER_STATE["alerts"]

@router.get("/insights")
def get_insights():
    return MOTHER_STATE["insights"]

@router.get("/pantry/expiring")
def get_expiring():
    return MOTHER_STATE["expiring"]
