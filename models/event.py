from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from models.base import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False)
    start_datetime = Column(DateTime, nullable=False)
    end_datetime = Column(DateTime, nullable=False)
    location = Column(String, nullable=False)
    number_of_participants = Column(Integer, nullable=False)
    notes = Column(String, nullable=True)
    support_collaborator_id = Column(Integer, ForeignKey("collaborators.id"), nullable=True)

    __table_args__ = (
        CheckConstraint("end_datetime >= start_datetime", name="check_event_dates_order"),
        CheckConstraint(
            "number_of_participants >= 0",
            name="check_event_participants_non_negative",
        ),
    )

    contract = relationship("Contract")
    support = relationship("Collaborator")
