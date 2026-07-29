from sqlalchemy import Column, Integer, String, Date, ForeignKey, JSON
from sqlalchemy.ext.hybrid import hybrid_property
from app.database.database import Base

class Exam(Base):
    __tablename__ = "exams"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=True, index=True)
    subject = Column(String, nullable=True)
    exam_date = Column(Date, nullable=False)
    topic = Column(String, nullable=False)
    target_score = Column(Integer, nullable=True)
    actual_score = Column(Integer, nullable=True)
    readiness_score = Column(Integer, nullable=True, default=50)  # AI calculated %
    risk_level = Column(String, nullable=True, default="Medium")  # AI calculated: High, Medium, Low
    study_plan = Column(JSON, nullable=True)  # AI calculated steps

    @hybrid_property
    def child_id(self):
        return self.student_id

    @child_id.setter
    def child_id(self, value):
        self.student_id = value

    @hybrid_property
    def exam_name(self):
        return self.topic

    @exam_name.setter
    def exam_name(self, value):
        self.topic = value

