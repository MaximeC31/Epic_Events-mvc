import re

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
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
    contracts = relationship("Contract", back_populates="client")

    @staticmethod
    def check_name(name, label):
        if not isinstance(name, str) or not name.strip():
            return f"Le {label} est obligatoire."
        if any(character.isdigit() for character in name):
            return f"Le {label} ne peut pas contenir de chiffre."

    @staticmethod
    def check_email(email):
        if not isinstance(email, str) or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email.strip()):
            return "L'email est incorrect."

    @staticmethod
    def check_phone(phone):
        message = (
            "Le téléphone doit être un numéro français à 10 chiffres ou un numéro "
            "international commençant par + et contenant de 7 à 15 chiffres."
        )
        if not isinstance(phone, str):
            return message
        phone = phone.strip()
        if not re.fullmatch(r"\+?[0-9]+(?:[ .-][0-9]+|[ .-]?\([0-9]+\))*", phone):
            return message
        digits = re.sub(r"[^0-9]", "", phone)
        if phone.startswith("+"):
            if not re.fullmatch(r"[1-9][0-9]{6,14}", digits):
                return message
        elif not re.fullmatch(r"0[1-9][0-9]{8}", digits):
            return message

    @staticmethod
    def check_company_name(company_name):
        if not isinstance(company_name, str) or not company_name.strip():
            return "Le nom de l'entreprise est obligatoire."

    def validation_error(self):
        return (
            self.check_name(self.first_name, "prénom")
            or self.check_name(self.last_name, "nom")
            or self.check_email(self.email)
            or self.check_phone(self.phone)
            or self.check_company_name(self.company_name)
        )
