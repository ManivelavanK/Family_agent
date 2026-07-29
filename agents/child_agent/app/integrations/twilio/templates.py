from typing import Dict, Any

NOTIFICATION_TEMPLATES: Dict[str, str] = {
    "HOMEWORK_REMINDER": """KinNest Parent Update

Your child has a pending assignment: {subject} - {title}.

Status: Pending
Priority: {priority}
Due Date: {due_date}

Suggested action:
Encourage a 45-minute study session today.

— KinNest AI""",

    "HOMEWORK_OVERDUE": """KinNest Parent Alert

ATTENTION: Your child has overdue homework: {subject} - {title}.

Status: OVERDUE
Priority: HIGH
Due Date: {due_date}

Suggested action:
Please assist your child in completing this overdue task today.

— KinNest AI""",

    "EXAM_APPROACHING": """KinNest Parent Update

Upcoming exam approaching: {exam_name} ({subject}).

Exam Date: {exam_date}
Preparation level: {preparation_percentage}%

Suggested action:
Schedule 30-minute daily revision sessions.

— KinNest AI""",

    "STUDY_CONSISTENCY_WARNING": """KinNest Parent Update

Study consistency alert: Study focus score or session count has declined recently.

Current focus score: {avg_focus_score}/100

Suggested action:
Review daily quiet study hours with your child.

— KinNest AI""",

    "EXCESSIVE_SCREEN_TIME_ALERT": """KinNest Parent Alert

Screen-time limit warning: Recreational screen time reached {avg_daily_minutes} minutes today.

Suggested action:
Encourage an outdoor activity or screen-free break.

— KinNest AI""",

    "SAFETY_ALERT": """KinNest CRITICAL SAFETY ALERT

Check-in status for {child_name} requires immediate attention: {status}.

Last note/location: {location_note}

Suggested action:
Check location status immediately and contact guardian.

— KinNest AI""",

    "ATTENDANCE_CONCERN": """KinNest Parent Alert

Attendance alert: Recent attendance rate has dropped to {attendance_percentage}%.

Suggested action:
Contact school administrator or review class schedule.

— KinNest AI""",

    "WELLNESS_CONCERN": """KinNest Parent Update

Wellness check: Recent activity indicates your child may be feeling fatigued or stressed.

Suggested action:
Have a gentle conversation and encourage relaxation.

— KinNest AI""",

    "WEEKLY_CHILD_SUMMARY": """KinNest Weekly Parent Briefing

Child: {child_name}
Homework completed: {completed_count} | Overdue: {overdue_count}
Attendance: {attendance_percentage}%
Avg screen time: {avg_daily_minutes} mins/day

— KinNest AI""",

    "POSITIVE_ACHIEVEMENT": """KinNest Celebration Update!

Great news! {child_name} achieved a milestone: {title}.

Keep up the fantastic support!

— KinNest AI""",
}


def render_whatsapp_template(notification_type: str, data: Dict[str, Any]) -> str:
    template = NOTIFICATION_TEMPLATES.get(notification_type)
    if not template:
        return f"KinNest Parent Update\n\n{data.get('message', 'Update received.')}\n\n— KinNest AI"

    try:
        return template.format(**data)
    except KeyError:
        return f"KinNest Parent Update\n\n{data.get('message', 'Update received.')}\n\n— KinNest AI"
