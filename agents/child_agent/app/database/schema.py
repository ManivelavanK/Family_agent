from sqlalchemy.orm import Session
from app.database.database import Base, engine, SessionLocal
from app.models.student import Student
from app.models.subject import Subject
from app.models.assignment import Assignment
from app.models.study_session import StudySession
from app.models.goal import Goal
from app.models.exam import Exam
from app.models.progress import Progress
from app.models.notification import Notification
from app.models.memory import StudentMemory

def create_tables():
    Base.metadata.create_all(bind=engine)
    
    # Database seeding
    db = SessionLocal()
    try:
        # Check if student exists
        student = db.query(Student).first()
        if not student:
            print("Seeding database with default student profile and dynamic details...")
            from app.models.profile import ChildProfile
            from app.models.digital_twin import DigitalTwin
            from app.models.screen_time import ScreenTimeLog
            from app.models.attendance import Attendance
            from app.models.pocket_money import PocketMoneyAllowance, ChildExpense
            from app.models.safety import CheckInLog
            from datetime import date, timedelta, time

            # 1. Create Child Profile
            child = ChildProfile(
                family_id="fam_123",
                name="Alex Mercer",
                age=16,
                date_of_birth=date(2010, 5, 15),
                gender="Male",
                parent_contact="+917358625565",
                education_stage="High School"
            )
            db.add(child)
            db.commit()
            db.refresh(child)

            # 2. Create Student
            student = Student(
                name="Alex Mercer",
                grade="Freshman",
                learning_style="Visual & Practical",
                interests=["Coding", "Astronomy", "Digital Art", "Robotics"],
                career_interest="Machine Learning Engineer",
                weekly_target_hours=15,
                education_level="COLLEGE",
                age=16,
                institution="State Tech College",
                year_of_study="Freshman",
                profile_metadata={
                    "coding_platforms": {"leetcode": "alex_codes", "github": "alexmercer-dev"},
                    "projects": ["AutoFocus AI Study Companion", "Neural Net Gesture Tracker"],
                    "hackathons": ["Global AI Hackathon 2026", "ViteConf Hackathon"],
                    "certifications": ["AWS Cloud Practitioner", "Google Advanced Data Analytics"],
                    "resume_score": 0.88,
                    "internship_tracking": "Applying for ML Internships",
                    "interview_prep": "Practicing LeetCode Mediums"
                }
            )
            db.add(student)
            db.commit()
            db.refresh(student)

            # 3. Create subjects
            subjects = [
                Subject(student_id=student.id, name="Mathematics", target_hours_per_week=3, current_grade="A", color="#3B82F6"),
                Subject(student_id=student.id, name="Physics", target_hours_per_week=3, current_grade="B+", color="#6366F1"),
                Subject(student_id=student.id, name="Chemistry", target_hours_per_week=2, current_grade="A-", color="#10B981"),
                Subject(student_id=student.id, name="Computer Science", target_hours_per_week=3, current_grade="A+", color="#7C3AED"),
                Subject(student_id=student.id, name="English", target_hours_per_week=2, current_grade="B", color="#F59E0B")
            ]
            db.add_all(subjects)
            db.commit()

            # 4. Create study sessions for past 7 days (dynamic chart data)
            from datetime import datetime
            today_dt = datetime.now()
            today = date.today()
            
            def make_session(days_ago, duration, score, topic, notes, subject_idx):
                start = today_dt - timedelta(days=days_ago)
                end = start + timedelta(minutes=duration)
                return StudySession(
                    student_id=student.id,
                    subject_id=subjects[subject_idx].id,
                    topic=topic,
                    start_time=start,
                    end_time=end,
                    duration_minutes=duration,
                    focus_score=score,
                    notes=notes
                )

            sessions = [
                make_session(6, 90, 85, "Limits", "Calculus limits practice", 0),
                make_session(5, 120, 78, "Mechanics", "Mechanics physics lab prep", 1),
                make_session(4, 150, 92, "AI Router", "Coding project: AI router in FastAPI", 3),
                make_session(3, 100, 80, "Matrix Algebra", "Matrix algebra test prep", 0),
                make_session(2, 75, 88, "Organic Chemistry", "Organic chemistry compounds", 2),
                make_session(1, 180, 95, "React Dashboard", "Coding frontend dashboard in React", 3),
                make_session(0, 90, 82, "Linear Regression", "Linear regression math practice", 0)
            ]
            db.add_all(sessions)

            # 5. Create Assignments
            assignments = [
                Assignment(student_id=student.id, subject_id=subjects[3].id, title="ML Model Proposal", description="Submit draft proposal for the student dashboard predictor", due_date=today + timedelta(days=3), status="Pending"),
                Assignment(student_id=student.id, subject_id=subjects[0].id, title="Calculus Homework 5", description="Chapter 4 exercises 1 to 20", due_date=today + timedelta(days=1), status="Pending"),
                Assignment(student_id=student.id, subject_id=subjects[1].id, title="Physics lab report", description="Thermodynamics group project submission", due_date=today - timedelta(days=1), status="Completed"),
                Assignment(student_id=student.id, subject_id=subjects[2].id, title="Periodic Table Quiz prep", description="Review transitions elements", due_date=today + timedelta(days=4), status="Pending")
            ]
            db.add_all(assignments)

            # 6. Create Goals
            goals = [
                Goal(student_id=student.id, title="Complete LeetCode Top Interview 150", target_date=today + timedelta(days=30), status="In Progress", progress_percentage=45),
                Goal(student_id=student.id, title="AWS Certification Prep", target_date=today + timedelta(days=15), status="In Progress", progress_percentage=75),
                Goal(student_id=student.id, title="Launch Portfolio Site", target_date=today - timedelta(days=2), status="Completed", progress_percentage=100)
            ]
            db.add_all(goals)

            # 7. Create Exams
            exams = [
                Exam(student_id=student.id, subject_id=subjects[0].id, exam_date=today + timedelta(days=7), topic="Linear Algebra Exam", target_score=95, actual_score=None, readiness_score=85, risk_level="Low", study_plan={"steps": ["Review notes", "Solve past papers"]}),
                Exam(student_id=student.id, subject_id=subjects[1].id, exam_date=today - timedelta(days=4), topic="Classical Mechanics", target_score=90, actual_score=88, readiness_score=90, risk_level="Low")
            ]
            db.add_all(exams)

            # 8. Create Academic Digital Twin
            twin = DigitalTwin(
                student_id=student.id,
                learning_score=0.86,
                confidence=0.92,
                subject_mastery={"Mathematics": 0.85, "Physics": 0.80, "Computer Science": 0.90},
                exam_readiness=0.85,
                focus_score=0.88,
                knowledge_gaps={"Chemistry": ["Organic reactions"]},
                productivity_trend={"weeks": ["Week 1"], "hours": [12.0]},
                learning_style="Visual & Practical",
                weekly_capacity=15.0
            )
            db.add(twin)

            # 9. Create Screen Time logs
            for i in range(7):
                db.add(ScreenTimeLog(
                    child_id=child.id,
                    date=today - timedelta(days=i),
                    mobile=30 + (i * 10),
                    gaming=20 + (i * 5),
                    tv=15,
                    social_media=25,
                    study_screen_time=60 + (i * 15),
                    other=10
                ))

            # 10. Create Attendance
            for i in range(7):
                db.add(Attendance(
                    child_id=child.id,
                    date=today - timedelta(days=i),
                    subject="Mathematics",
                    status="PRESENT"
                ))

            # 11. Create Pocket Money & Expenses
            db.add(PocketMoneyAllowance(
                family_id="fam_123",
                child_id=child.id,
                amount=2000.0,
                frequency="Monthly",
                date=today
            ))
            db.add(ChildExpense(
                family_id="fam_123",
                child_id=child.id,
                amount=250.0,
                category="Books",
                date=today - timedelta(days=2)
            ))
            db.add(ChildExpense(
                family_id="fam_123",
                child_id=child.id,
                amount=150.0,
                category="Food",
                date=today
            ))

            # 12. Create Check-in Log
            db.add(CheckInLog(
                child_id=child.id,
                date=today,
                expected_return_time=time(19, 30),
                status="RETURNED"
            ))

            db.commit()
            print("Database dynamic seeding completed successfully.")
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()