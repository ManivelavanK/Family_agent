import logging
import json
from datetime import datetime, date, timedelta, timezone
from sqlalchemy.orm import Session
from app.database.database import SessionLocal
from app.services.medicine_service import check_refill_alerts
from app.services.notification_service import send_notification
from app.rule_engine.alert_service import evaluate_rules_and_generate_alerts
from app.models.appointment import Appointment
from app.models.medicine import Medicine
from app.models.vitals import Vitals
from app.models.activity import Activity
from app.models.nutrition import Nutrition
from app.models.daily_summary import DailySummary
from app.models.emergency import EmergencyIncident

# WhatsApp services
from app.notification.notification_service import (
    notify_medicine,
    notify_low_stock,
    notify_appointment,
    notify_health_summary,
    notify_custom_message
)

logger = logging.getLogger(__name__)


# ── Hourly Jobs ─────────────────────────────────────────────────────────────

def run_daily_refill_check():
    logger.info("Scheduler Job: Checking medicine refill stocks...")
    db = SessionLocal()
    try:
        check_refill_alerts(db)
        
        # WhatsApp Alerts for low stock or missed (0 stock) medicines
        active_meds = db.query(Medicine).filter(Medicine.is_active == True).all()
        for med in active_meds:
            if med.inventory_count == 0:
                logger.warning("Missed medicine warning: %s is out of stock.", med.name)
                notify_custom_message(None, f"MISSED MEDICINE ALERT: {med.name} is completely out of stock!")
            elif med.inventory_count <= 5:
                logger.info("Low stock warning: %s has %d remaining.", med.name, med.inventory_count)
                notify_low_stock(None, med.name, med.inventory_count)
    except Exception as e:
        logger.error("Error checking refill alerts: %s", e)
    finally:
        db.close()


def run_hourly_health_rules_check():
    logger.info("Scheduler Job: Performing hourly health rule engine evaluation...")
    db = SessionLocal()
    try:
        alerts = evaluate_rules_and_generate_alerts(db)
        for alert in alerts:
            if alert.get("severity") == "High":
                send_notification(
                    title=f"CRITICAL HEALTH RULE ALERT: {alert.get('title')}",
                    body=f"{alert.get('description')} Recommended Action: {alert.get('recommended_action')}",
                    notification_type="Emergency"
                )
    except Exception as e:
        logger.error("Error during hourly health rules check: %s", e)
    finally:
        db.close()


def run_hourly_appointment_check():
    logger.info("Scheduler Job: Checking for upcoming doctor appointments...")
    db = SessionLocal()
    try:
        now = datetime.now()
        
        # 1. Check appointments scheduled in the next hour
        one_hour_later = now + timedelta(hours=1)
        upcoming_1h = db.query(Appointment).filter(
            Appointment.appointment_time >= now,
            Appointment.appointment_time <= one_hour_later
        ).all()

        for appt in upcoming_1h:
            send_notification(
                title="Upcoming Appointment Alert",
                body=f"Reminder: You have an appointment with {appt.doctor_name} ({appt.specialty}) at {appt.appointment_time.strftime('%I:%M %p')}.",
                notification_type="Reminder"
            )

        # 2. Check appointments scheduled in the next 24 hours
        time_24h_start = now + timedelta(hours=23)
        time_24h_end = now + timedelta(hours=24)
        upcoming_24h = db.query(Appointment).filter(
            Appointment.appointment_time >= time_24h_start,
            Appointment.appointment_time <= time_24h_end
        ).all()

        for appt in upcoming_24h:
            logger.info("Sending 24h WhatsApp reminder for appointment: %s", appt.doctor_name)
            notify_appointment(
                phone=None,
                doctor=appt.doctor_name,
                specialty=appt.specialty,
                time=appt.appointment_time.strftime("%Y-%m-%d %I:%M %p")
            )

    except Exception as e:
        logger.error("Error during appointment checks: %s", e)
    finally:
        db.close()


# ── Morning Job (8 AM) ──────────────────────────────────────────────────────

def run_morning_schedule_generation():
    logger.info("Scheduler Job: Running morning schedule compiler (8 AM)...")
    db = SessionLocal()
    today = date.today()
    try:
        # 1. Today's medicines
        active_meds = db.query(Medicine).filter(Medicine.is_active == True).all()
        med_list = [f"{m.name} ({m.dosage} at {m.time_of_day})" for m in active_meds]

        # 2. Today's appointments
        start_of_day = datetime.combine(today, datetime.min.time())
        end_of_day = datetime.combine(today, datetime.max.time())
        todays_appts = db.query(Appointment).filter(
            Appointment.appointment_time >= start_of_day,
            Appointment.appointment_time <= end_of_day
        ).all()
        appt_list = [f"{a.doctor_name} ({a.specialty}) at {a.appointment_time.strftime('%I:%M %p')}" for a in todays_appts]

        # Compile Schedule Dict
        morning_data = {
            "todays_medicines": med_list,
            "todays_appointments": appt_list,
            "water_reminder": "Remember to drink water regularly today. Target: 1500ml.",
            "walking_reminder": "Keep active! Don't forget your scheduled morning walk."
        }

        # Store in DB
        summary = db.query(DailySummary).filter(DailySummary.date == today).first()
        if not summary:
            summary = DailySummary(date=today)
            db.add(summary)

        summary.morning_schedule = json.dumps(morning_data)
        db.commit()
        logger.info("Stored Morning Schedule in SQLite for date: %s", today)

        # Local Alert Notification
        send_notification("Morning Schedule Compiled", f"You have {len(med_list)} medicines and {len(appt_list)} appointments today.", "Info")

        # WhatsApp reminders for each scheduled medication
        for med in active_meds:
            logger.info("Sending morning WhatsApp reminder for medication: %s", med.name)
            notify_medicine(
                phone=None,
                name="Grandparent",
                medicine=med.name,
                time=med.time_of_day
            )

    except Exception as e:
        logger.error("Failed to generate morning schedule: %s", e)
    finally:
        db.close()


# ── Evening Job (8 PM) ──────────────────────────────────────────────────────

def run_evening_summary_generation():
    logger.info("Scheduler Job: Running evening summary compiler (8 PM)...")
    db = SessionLocal()
    today = date.today()
    try:
        start_of_day = datetime.combine(today, datetime.min.time())
        end_of_day = datetime.combine(today, datetime.max.time())

        # 1. Daily Health Summary (Vitals Averages today)
        vitals = db.query(Vitals).filter(
            Vitals.timestamp >= start_of_day,
            Vitals.timestamp <= end_of_day
        ).all()

        vitals_summary = {}
        bp_str = "120/80"
        if vitals:
            sys_avg = sum(v.blood_pressure_systolic for v in vitals) / len(vitals)
            dia_avg = sum(v.blood_pressure_diastolic for v in vitals) / len(vitals)
            sugar_avg = sum(v.blood_sugar for v in vitals) / len(vitals)
            hr_avg = sum(v.heart_rate for v in vitals) / len(vitals)
            vitals_summary = {
                "avg_systolic": round(sys_avg, 2),
                "avg_diastolic": round(dia_avg, 2),
                "avg_blood_sugar": round(sugar_avg, 2),
                "avg_heart_rate": round(hr_avg, 2)
            }
            bp_str = f"{round(sys_avg)}/{round(dia_avg)}"
        else:
            vitals_summary = "No vitals logs recorded today."

        # 2. Missed medicines (active meds with 0 remaining inventory)
        active_meds = db.query(Medicine).filter(Medicine.is_active == True).all()
        missed = [m.name for m in active_meds if m.inventory_count == 0]

        # 3. Activity summary today
        activity = db.query(Activity).filter(Activity.date == today).first()
        activity_data = {
            "steps": activity.steps if activity else 0,
            "sleep_hours": activity.sleep_hours if activity else 0.0,
            "active_minutes": activity.duration_minutes if activity else 0
        }

        # 4. Nutrition summary today
        nutrition = db.query(Nutrition).filter(
            Nutrition.timestamp >= start_of_day,
            Nutrition.timestamp <= end_of_day
        ).all()
        calories_total = sum(n.calories for n in nutrition)
        water_total = sum(n.water_ml for n in nutrition)
        nutrition_data = {
            "calories": calories_total,
            "water_ml": water_total
        }

        # Compile Evening Summary Dict
        evening_data = {
            "vitals_averages": vitals_summary,
            "missed_medications": missed,
            "activity": activity_data,
            "nutrition": nutrition_data
        }

        # Store in DB
        summary = db.query(DailySummary).filter(DailySummary.date == today).first()
        if not summary:
            summary = DailySummary(date=today)
            db.add(summary)

        summary.evening_summary = json.dumps(evening_data)
        db.commit()
        logger.info("Stored Evening Summary in SQLite for date: %s", today)

        # Local Alert Notification
        send_notification("Evening Health Summary Compiled", "Evening compilation complete. Logs successfully persisted.", "Info")

        # WhatsApp Daily Wellness Summary Report
        status_msg = "Wellness looks stable today." if not missed else f"Missed meds: {', '.join(missed)}"
        notify_health_summary(
            phone=None,
            bp=bp_str,
            sleep=activity_data["sleep_hours"],
            water=nutrition_data["water_ml"],
            status=status_msg
        )

    except Exception as e:
        logger.error("Failed to generate evening health summary: %s", e)
    finally:
        db.close()


# ── Weekly Sunday Job (11 PM) ───────────────────────────────────────────────

def run_weekly_report_generation():
    logger.info("Scheduler Job: Running weekly health summary report generation...")
    from app.services.weekly_report_service import generate_weekly_report
    db = SessionLocal()
    try:
        report = generate_weekly_report(db)
        logger.info("Scheduler Job: Weekly report and PDF generated successfully.")

        # WhatsApp Weekly PDF notification alert
        report_data = json.loads(report.report_json)
        bp_avgs = report_data.get("vitals_averages", {})
        bp_str = f"{bp_avgs.get('systolic_bp', 120)}/{bp_avgs.get('diastolic_bp', 80)}"
        sugar_val = bp_avgs.get("blood_sugar", 95.0)

        notify_custom_message(
            phone=None,
            message=(
                f"Weekly Health Summary: Average BP: {bp_str}, Sugar Avg: {sugar_val}. "
                f"Download report PDF link: http://localhost:8000/api/v1/report/{report.id}/pdf"
            )
        )
    except Exception as e:
        logger.error("Failed to generate weekly report: %s", e)
    finally:
        db.close()


# ── Emergency Escalation Checker (Every 5 minutes) ──────────────────────────

def run_emergency_escalation_check():
    logger.info("Scheduler Job: Checking for unacknowledged Emergency Incident escalations...")
    db = SessionLocal()
    try:
        # Check active emergencies older than 5 minutes
        cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=5)
        unresolved = db.query(EmergencyIncident).filter(
            EmergencyIncident.status == "Active",
            EmergencyIncident.time <= cutoff_time
        ).all()

        for incident in unresolved:
            logger.warning("Escalating Emergency Incident ID %d. Unacknowledged for 5+ minutes.", incident.id)
            escalation_msg = (
                f"CRITICAL ESCALATION: Emergency incident ID {incident.id} "
                f"({incident.reason}) remains UNACKNOWLEDGED for over 5 minutes! "
                f"Please take immediate action!"
            )
            notify_custom_message(None, escalation_msg)
    except Exception as e:
        logger.error("Error during emergency escalation check: %s", e)
    finally:
        db.close()
