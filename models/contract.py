from datetime import datetime
from decimal import Decimal
import re

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
)
from sqlalchemy.orm import relationship

from models.base import Base


class Contract(Base):
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    total_amount = Column(Numeric(12, 2), nullable=False)
    remaining_amount = Column(Numeric(12, 2), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    is_signed = Column(Boolean, nullable=False, server_default="false")

    __table_args__ = (
        CheckConstraint("total_amount > 0", name="check_total_amount_positive"),
        CheckConstraint("remaining_amount >= 0", name="check_remaining_amount_non_negative"),
        CheckConstraint("remaining_amount <= total_amount", name="check_remaining_amount_not_exceed_total"),
    )

    client = relationship("Client", back_populates="contracts")

    @staticmethod
    def parse_amount(value):
        if not isinstance(value, str) or not re.fullmatch(r"[0-9]+(?:,[0-9]{1,2})?", value):
            raise ValueError("Montant invalide : utilisez une virgule et au plus deux décimales.")
        return Decimal(value.replace(",", "."))

    @staticmethod
    def check_total_amount(total_amount):
        if not isinstance(total_amount, Decimal) or not total_amount.is_finite():
            return "Le montant total est incorrect."
        if total_amount <= 0 or total_amount > Decimal("9999999999.99"):
            return "Le montant total doit être supérieur à zéro et tenir sur 12 chiffres."
        exponent = total_amount.as_tuple().exponent
        if not isinstance(exponent, int) or exponent < -2:
            return "Les montants doivent comporter au plus deux décimales."

    @staticmethod
    def check_remaining_amount(remaining_amount, total_amount):
        if not isinstance(remaining_amount, Decimal) or not remaining_amount.is_finite():
            return "Le montant restant est incorrect."
        if remaining_amount < 0 or remaining_amount > total_amount:
            return "Le montant restant doit être compris entre zéro et le montant total."
        exponent = remaining_amount.as_tuple().exponent
        if not isinstance(exponent, int) or exponent < -2:
            return "Les montants doivent comporter au plus deux décimales."

    def validation_error(self):
        return self.check_total_amount(self.total_amount) or self.check_remaining_amount(
            self.remaining_amount, self.total_amount
        )
