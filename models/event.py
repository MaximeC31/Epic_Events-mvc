from datetime import datetime

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

    @staticmethod
    def parse_datetime(value):
        message = "Date invalide : utilisez le format JJ/MM/AAAA HH:MM."
        if not isinstance(value, str):
            raise ValueError(message)
        try:
            parsed_datetime = datetime.strptime(value, "%d/%m/%Y %H:%M")
        except ValueError:
            raise ValueError(message) from None
        if parsed_datetime.strftime("%d/%m/%Y %H:%M") != value:
            raise ValueError(message)
        return parsed_datetime

    @staticmethod
    def check_dates(start_datetime, end_datetime):
        if not isinstance(start_datetime, datetime) or not isinstance(end_datetime, datetime):
            return "Les dates de début et de fin sont obligatoires et doivent être valides."
        if end_datetime < start_datetime:
            return "La date de fin ne peut pas précéder la date de début."

    @staticmethod
    def check_location(location):
        if not isinstance(location, str) or not location.strip():
            return "Le lieu est obligatoire."

    @staticmethod
    def check_number_of_participants(number_of_participants):
        if not isinstance(number_of_participants, int) or isinstance(number_of_participants, bool):
            return "Le nombre de participants doit être un entier."
        if not 0 <= number_of_participants <= 2147483647:
            return "Le nombre de participants doit être compris entre 0 et 2147483647."

    def validation_error(self):
        return (
            self.check_dates(self.start_datetime, self.end_datetime)
            or self.check_location(self.location)
            or self.check_number_of_participants(self.number_of_participants)
        )
