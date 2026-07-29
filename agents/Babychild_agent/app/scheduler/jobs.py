from datetime import datetime, date, time, timedelta
import logging

from app.database.database import SessionLocal
from app.models.sleep import SleepRecord
from app.services import baby_service, rule_service, health_service, feeding_service, vaccination_service, notification_service

logger = logging.getLogger(__name__)

def check_baby_alerts_job():
    logger.info("[Scheduler Job] Starting check_baby_alerts_job...")
    db = SessionLocal()
    try:
        babies = baby_service.get_all_babies(db=db)
        logger.info(f"[Scheduler Job] Found {len(babies)} babies to evaluate for alerts.")
        for baby in babies:
            if not baby.parent_contact:
                logger.warning(f"[Scheduler Job] Baby {baby.name} (ID: {baby.id}) has no parent contact configured.")
                continue
                
            # Evaluate alerts using the simple rule engine
            alerts_data = rule_service.generate_alerts(db=db, baby_id=baby.id)
            alerts = alerts_data.get("alerts", [])
            
            for alert in alerts:
                try:
                    if "feeding" in alert.lower():
                        logger.info(f"[Scheduler Job] Dispatching feeding alert for baby {baby.name}")
                        notification_service.send_feeding_alert(
                            to_phone=baby.parent_contact,
                            baby_name=baby.name,
                            hours=4.0
                        )
                    elif "temperature" in alert.lower() or "fever" in alert.lower() or "high" in alert.lower():
                        logger.info(f"[Scheduler Job] Dispatching high temperature alert for baby {baby.name}")
                        # Retrieve latest temperature
                        health_sum = health_service.get_health_summary(db=db, baby_id=baby.id)
                        temp = health_sum.get("latest_temperature_c") or 38.5
                        notification_service.send_fever_alert(
                            to_phone=baby.parent_contact,
                            baby_name=baby.name,
                            temp=temp
                        )
                except Exception as alert_err:
                    logger.error(f"[Scheduler Job] Failed to send alert '{alert}' to {baby.parent_contact}: {alert_err}")
    except Exception as e:
        logger.error(f"[Scheduler Job] Critical failure in check_baby_alerts_job: {e}")
    finally:
        db.close()
        logger.info("[Scheduler Job] Finished check_baby_alerts_job.")

def vaccination_reminders_job():
    logger.info("[Scheduler Job] Starting vaccination_reminders_job...")
    db = SessionLocal()
    try:
        babies = baby_service.get_all_babies(db=db)
        for baby in babies:
            if not baby.parent_contact:
                continue
                
            upcoming = vaccination_service.get_upcoming_vaccinations(db=db, baby_id=baby.id)
            today = date.today()
            three_days_later = today + timedelta(days=3)
            
            for v in upcoming:
                if v.status == "pending" and today <= v.due_date <= three_days_later:
                    try:
                        logger.info(f"[Scheduler Job] Dispatching vaccine reminder for {v.vaccine_name} to {baby.name}")
                        notification_service.send_vaccination_reminder(
                            to_phone=baby.parent_contact,
                            baby_name=baby.name,
                            vaccine_name=v.vaccine_name,
                            due_date=str(v.due_date)
                        )
                    except Exception as alert_err:
                        logger.error(f"[Scheduler Job] Failed to send vaccine reminder to {baby.parent_contact}: {alert_err}")
    except Exception as e:
        logger.error(f"[Scheduler Job] Critical failure in vaccination_reminders_job: {e}")
    finally:
        db.close()
        logger.info("[Scheduler Job] Finished vaccination_reminders_job.")

def daily_summaries_job():
    logger.info("[Scheduler Job] Starting daily_summaries_job...")
    db = SessionLocal()
    try:
        babies = baby_service.get_all_babies(db=db)
        for baby in babies:
            if not baby.parent_contact:
                continue
                
            # Aggregate feeding today
            feed_summary = feeding_service.get_today_summary(db=db, baby_id=baby.id)
            total_feedings = feed_summary.get("total_feedings", 0)
            total_quantity_ml = feed_summary.get("total_quantity_ml", 0)

            # Aggregate sleep today
            today_start = datetime.combine(date.today(), time.min)
            today_end = datetime.combine(date.today(), time.max)
            today_sleep_records = db.query(SleepRecord).filter(
                SleepRecord.baby_id == baby.id,
                SleepRecord.start_time >= today_start,
                SleepRecord.end_time <= today_end
            ).all()
            today_sleep_duration = sum(s.duration_minutes for s in today_sleep_records)
            
            summary_text = (
                f"• Total Feedings: {total_feedings} times ({total_quantity_ml} ml)\n"
                f"• Total Sleep: {round(today_sleep_duration / 60, 1)} hours ({today_sleep_duration} mins)"
            )
            
            try:
                logger.info(f"[Scheduler Job] Dispatching daily summary WhatsApp to {baby.name}")
                notification_service.send_daily_summary(
                    to_phone=baby.parent_contact,
                    baby_name=baby.name,
                    summary_text=summary_text
                )
            except Exception as alert_err:
                logger.error(f"[Scheduler Job] Failed to send daily summary to {baby.parent_contact}: {alert_err}")
    except Exception as e:
        logger.error(f"[Scheduler Job] Critical failure in daily_summaries_job: {e}")
    finally:
        db.close()
        logger.info("[Scheduler Job] Finished daily_summaries_job.")
