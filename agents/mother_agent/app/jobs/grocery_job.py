import logging
from app.database.database import SessionLocal
from app.services.shopping_service import generate_shopping_list

logger = logging.getLogger(__name__)


def run_daily_grocery_check():
    logger.info("Running daily grocery check...")
    db = SessionLocal()
    try:
        shopping_list = generate_shopping_list(db)
        if shopping_list:
            logger.info("Daily shopping report — %d items need attention:", len(shopping_list))
            for item in shopping_list:
                logger.info(
                    "  [%s] stock=%.2f %s | buy=%.2f %s",
                    item["item"],
                    item["current_stock"],
                    item["unit"],
                    item["recommended_purchase"],
                    item["unit"],
                )
        else:
            logger.info("Daily grocery check: everything is sufficiently stocked.")
    except Exception as e:
        logger.error("Daily grocery check failed: %s", e)
        raise
    finally:
        db.close()
