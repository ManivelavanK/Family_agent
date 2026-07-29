from sqlalchemy import Column, Integer, Float, String, Date, ForeignKey
from app.database.database import Base

class PocketMoneyAllowance(Base):
    __tablename__ = "pocket_money_allowances"

    id = Column(Integer, primary_key=True, index=True)
    family_id = Column(String, nullable=False, index=True)
    child_id = Column(Integer, ForeignKey("child_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    frequency = Column(String, nullable=False)  # Daily, Weekly, Monthly
    date = Column(Date, nullable=False)


class ChildExpense(Base):
    __tablename__ = "child_expenses"

    id = Column(Integer, primary_key=True, index=True)
    family_id = Column(String, nullable=False, index=True)
    child_id = Column(Integer, ForeignKey("child_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    category = Column(String, nullable=False)  # Food, Transport, Education, Entertainment, Shopping, Gaming, Subscriptions, Friends, Emergency, Other
    description = Column(String, nullable=True)
    date = Column(Date, nullable=False)


class SavingGoal(Base):
    __tablename__ = "saving_goals"

    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("child_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String, nullable=False)
    target_amount = Column(Float, nullable=False)
    current_saved = Column(Float, nullable=False, default=0.0)
    target_date = Column(Date, nullable=False)
