from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from models.base import Base


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    company_name = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    last_contact_at = Column(DateTime, nullable=False)
    sales_contact_id = Column(Integer, ForeignKey("collaborators.id"), nullable=False)

    sales_contact = relationship("Collaborator")
