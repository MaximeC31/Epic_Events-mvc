from enum import Enum

from sqlalchemy import Boolean, Column, Enum as SqlEnum, Integer, String, text

from .base import Base


class Role(str, Enum):
    MANAGEMENT = "gestion"
    SALES = "commercial"
    SUPPORT = "support"


class Collaborator(Base):
    __tablename__ = "collaborators"

    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(SqlEnum(Role), nullable=False)
    is_active = Column(Boolean, nullable=False, server_default=text("true"))
