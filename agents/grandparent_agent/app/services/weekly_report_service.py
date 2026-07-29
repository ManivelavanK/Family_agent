import os
import json
import logging
from datetime import date, datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func

# ReportLab modules
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Models
from app.models.vitals import Vitals
from app.models.activity import Activity
from app.models.nutrition import Nutrition
from app.models.medicine import Medicine
from app.models.appointment import Appointment
from app.models.weekly_report import WeeklyReport

logger = logging.getLogger(__name__)
REPORTS_DIR = "reports"


def generate_weekly_report(db: Session, ending_date: date = None) -> WeeklyReport:
    """
    Compiles average BP, sugar, heart rate, sleep, calories, water intake,
    medicines, and appointments over the last 7 days.
    Generates a clean PDF using ReportLab and stores the record in database.
    """
    if ending_date is None:
        ending_date = date.today()

    start_date = ending_date - timedelta(days=7)
    logger.info("Weekly Report Service: Compiling report from %s to %s", start_date, ending_date)

    # Convert date bounds to datetime bounds for timestamp fields
    start_dt = datetime.combine(start_date, datetime.min.time())
    end_dt = datetime.combine(ending_date, datetime.max.time())

    # 1. Average Vitals
    vitals_avg = db.query(
        func.avg(Vitals.blood_pressure_systolic).label("sys"),
        func.avg(Vitals.blood_pressure_diastolic).label("dia"),
        func.avg(Vitals.heart_rate).label("hr"),
        func.avg(Vitals.blood_sugar).label("bs")
    ).filter(Vitals.timestamp >= start_dt, Vitals.timestamp <= end_dt).first()

    sys_avg = round(vitals_avg.sys, 2) if vitals_avg and vitals_avg.sys else 120.0
    dia_avg = round(vitals_avg.dia, 2) if vitals_avg and vitals_avg.dia else 80.0
    hr_avg = round(vitals_avg.hr, 2) if vitals_avg and vitals_avg.hr else 72.0
    bs_avg = round(vitals_avg.bs, 2) if vitals_avg and vitals_avg.bs else 95.0

    # 2. Activity Averages
    activity_avg = db.query(
        func.avg(Activity.steps).label("steps"),
        func.avg(Activity.sleep_hours).label("sleep")
    ).filter(Activity.date >= start_date, Activity.date <= ending_date).first()

    steps_avg = round(activity_avg.steps, 2) if activity_avg and activity_avg.steps else 0.0
    sleep_avg = round(activity_avg.sleep, 2) if activity_avg and activity_avg.sleep else 7.0

    # 3. Nutrition Averages
    nutrition_avg = db.query(
        func.avg(Nutrition.calories).label("cal"),
        func.avg(Nutrition.water_ml).label("water")
    ).filter(Nutrition.timestamp >= start_dt, Nutrition.timestamp <= end_dt).first()

    cal_avg = round(nutrition_avg.cal, 2) if nutrition_avg and nutrition_avg.cal else 2000.0
    water_avg = round(nutrition_avg.water, 2) if nutrition_avg and nutrition_avg.water else 1500.0

    # 4. Medicines list
    meds = db.query(Medicine).filter(Medicine.is_active == True).all()
    med_list = [f"{m.name} ({m.dosage}, {m.time_of_day})" for m in meds]

    # 5. Appointments list
    appts = db.query(Appointment).filter(
        Appointment.appointment_time >= start_dt,
        Appointment.appointment_time <= end_dt
    ).all()
    appt_list = [f"{a.doctor_name} ({a.specialty}) at {a.appointment_time.strftime('%Y-%m-%d %H:%M')}" for a in appts]

    # Combine into JSON payload
    report_data = {
        "start_date": str(start_date),
        "end_date": str(ending_date),
        "vitals_averages": {
            "systolic_bp": sys_avg,
            "diastolic_bp": dia_avg,
            "heart_rate": hr_avg,
            "blood_sugar": bs_avg
        },
        "activity_averages": {
            "steps": steps_avg,
            "sleep_hours": sleep_avg
        },
        "nutrition_averages": {
            "calories": cal_avg,
            "water_ml": water_avg
        },
        "active_medicines": med_list,
        "weekly_appointments": appt_list
    }

    # Ensure reports directory exists
    os.makedirs(REPORTS_DIR, exist_ok=True)
    pdf_filename = f"weekly_report_{ending_date.isoformat()}.pdf"
    pdf_path = os.path.join(REPORTS_DIR, pdf_filename)

    # 6. Generate ReportLab PDF
    logger.info("Weekly Report Service: Generating PDF at path: %s", pdf_path)
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Custom styles
    title_style = ParagraphStyle(
        'ReportTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor("#2C3E50"),
        spaceAfter=15
    )
    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor("#16A085"),
        spaceBefore=15,
        spaceAfter=10
    )
    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['BodyText'],
        fontSize=10,
        spaceAfter=6
    )

    story.append(Paragraph("KinNest — Weekly Health Summary Report", title_style))
    story.append(Paragraph(f"Reporting Period: {start_date} to {ending_date}", body_style))
    story.append(Paragraph(f"Generated On: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}", body_style))
    story.append(Spacer(1, 15))

    # Averages Table
    story.append(Paragraph("1. Weekly Health Metrics Averages", section_style))
    table_data = [
        ["Health Parameter", "Weekly Average Value / Status"],
        ["Blood Pressure (Systolic / Diastolic)", f"{sys_avg} / {dia_avg} mmHg"],
        ["Blood Sugar", f"{bs_avg} mg/dL"],
        ["Heart Rate", f"{hr_avg} bpm"],
        ["Sleep Hours", f"{sleep_avg} hours"],
        ["Steps Walked", f"{steps_avg} steps"],
        ["Calories Consumed", f"{cal_avg} kcal"],
        ["Water Intake", f"{water_avg} ml"]
    ]
    t = Table(table_data, colWidths=[200, 250])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (1,0), colors.HexColor("#34495E")),
        ('TEXTCOLOR', (0,0), (1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#ECF0F1")),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor("#BDC3C7")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F9F9F9")])
    ]))
    story.append(t)
    story.append(Spacer(1, 15))

    # Medicines List
    story.append(Paragraph("2. Active Medications Checked", section_style))
    if med_list:
        for med in med_list:
            story.append(Paragraph(f"• {med}", body_style))
    else:
        story.append(Paragraph("No active medicines listed in daily schedule.", body_style))
    story.append(Spacer(1, 15))

    # Appointments List
    story.append(Paragraph("3. Doctor Visits & Appointments This Week", section_style))
    if appt_list:
        for appt in appt_list:
            story.append(Paragraph(f"• {appt}", body_style))
    else:
        story.append(Paragraph("No doctor appointments recorded during this reporting window.", body_style))

    # Build PDF doc
    doc.build(story)

    # Save details to DB (upsert if exists)
    summary = db.query(WeeklyReport).filter(WeeklyReport.date == ending_date).first()
    if not summary:
        summary = WeeklyReport(date=ending_date)
        db.add(summary)

    summary.report_json = json.dumps(report_data)
    summary.pdf_path = pdf_path.replace("\\", "/") # Normalize slash format
    db.commit()
    db.refresh(summary)

    logger.info("Weekly Report Service: Log archived in database with ID %d.", summary.id)
    return summary
