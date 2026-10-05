import re
from enum import Enum

from sqlalchemy import Boolean, Column, Enum as SqlEnum, Integer, String, text

from models.base import Base


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

    @staticmethod
    def check_name(name, label) -> str | None:
        if not isinstance(name, str) or not name.strip():
            return f"Le {label} est obligatoire."
        if any(character.isdigit() for character in name):
            return f"Le {label} ne peut pas contenir de chiffre."

    @staticmethod
    def check_email(email) -> str | None:
        if not isinstance(email, str) or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email.strip()):
            return "L'email est incorrect."

    @staticmethod
    def check_role(role) -> str | None:
        if not isinstance(role, Role):
            return "Le rôle est incorrect."

    @staticmethod
    def parse_role_choice(choice) -> Role:
        try:
            role_number = int(choice)
        except (TypeError, ValueError):
            raise ValueError("Le numéro de rôle est incorrect.") from None

        if not 1 <= role_number <= len(Role):
            raise ValueError("Le numéro de rôle est incorrect.")

        return list(Role)[role_number - 1]

    @staticmethod
    def check_password(password: str) -> str | None:
        if not password:
            return "Le mot de passe est obligatoire."
        if len(password.encode("utf-8")) > 72:
            return "Le mot de passe ne peut pas dépasser 72 octets en UTF-8."

    @staticmethod
    def check_password_confirmation(password, confirmation) -> str | None:
        if password != confirmation:
            return "Les mots de passe ne correspondent pas."

    @staticmethod
    def parse_status_choice(choice) -> bool:
        if choice == "0":
            return False
        if choice == "1":
            return True
        raise ValueError("Le statut est incorrect.")

    def validation_error(self) -> str | None:
        return (
            self.check_name(self.first_name, "prénom")
            or self.check_name(self.last_name, "nom")
            or self.check_email(self.email)
            or self.check_role(self.role)
        )
