from datetime import datetime

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
        CheckConstraint("total_amount >= 0", name="check_total_amount_non_negative"),
        CheckConstraint("remaining_amount >= 0", name="check_remaining_amount_non_negative"),
        CheckConstraint("remaining_amount <= total_amount", name="check_remaining_amount_not_exceed_total"),
    )

    client = relationship("Client", back_populates="contracts")
