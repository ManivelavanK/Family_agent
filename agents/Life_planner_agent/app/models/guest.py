import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from app.database.session import Base

class Guest(Base):
    __tablename__ = "guests"

    id = Column(Integer, primary_key=True, index=True)
    family_id = Column(String(100), nullable=False, default="default_family", index=True)
    name = Column(String(255), nullable=False)
    relationship = Column(String(100), nullable=True)
    group_name = Column(String(100), nullable=True, index=True)
    adults = Column(Integer, nullable=False, default=1)
    children = Column(Integer, nullable=False, default=0)
    arrival_datetime = Column(DateTime(timezone=True), nullable=True, index=True)
    departure_datetime = Column(DateTime(timezone=True), nullable=True, index=True)
    accommodation_info = Column(Text, nullable=True)
    food_preferences = Column(Text, nullable=True)
    dietary_restrictions = Column(Text, nullable=True)
    special_requirements = Column(Text, nullable=True)
    transport_info = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "family_id": self.family_id,
            "name": self.name,
            "relationship": self.relationship,
            "group_name": self.group_name,
            "adults": self.adults,
            "children": self.children,
            "arrival_datetime": str(self.arrival_datetime) if self.arrival_datetime else None,
            "departure_datetime": str(self.departure_datetime) if self.departure_datetime else None,
            "accommodation_info": self.accommodation_info,
            "food_preferences": self.food_preferences,
            "dietary_restrictions": self.dietary_restrictions,
            "special_requirements": self.special_requirements,
            "transport_info": self.transport_info,
            "notes": self.notes,
            "created_at": str(self.created_at),
            "updated_at": str(self.updated_at)
        }
