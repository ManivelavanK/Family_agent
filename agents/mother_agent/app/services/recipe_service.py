import logging
import html
from sqlalchemy.orm import Session
from app.models.grocery_item import GroceryItem
from app.models.expiry import ExpiryItem
from app.services.ai_service import generate_recipe_recommendation

logger = logging.getLogger(__name__)


def suggest_recipe(db: Session) -> dict:
    inventory = db.query(GroceryItem).filter(GroceryItem.quantity > 0).all()
    expiry_items = db.query(ExpiryItem).all()

    if not inventory:
        return {"message": "No ingredients available in inventory."}

    ingredients = sorted({html.escape(item.name) for item in inventory})
    expiring = sorted({html.escape(item.item_name) for item in expiry_items})

    prompt = f"""You are an intelligent family cooking assistant.

Available ingredients:
{ingredients}

Ingredients expiring soon (prioritize these):
{expiring}

Generate 3 practical home recipes.

Rules:
- Use maximum available ingredients.
- Prioritize expiring ingredients.
- Do not suggest recipes using unavailable ingredients.
- Prefer breakfast, lunch, and dinner recipes.
- Include: recipe name, ingredients used, cooking steps, preparation time.

Return only plain text."""

    try:
        recipe = generate_recipe_recommendation(prompt)
    except Exception as e:
        logger.error("Recipe AI call failed: %s", e)
        recipe = "Unable to generate recipes at this time."

    return {
        "available_ingredients": ingredients,
        "expiring_items": expiring,
        "recipes": recipe,
    }
