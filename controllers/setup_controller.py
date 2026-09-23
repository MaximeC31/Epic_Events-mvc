from sqlalchemy import select

from controllers.authentication_controller import hash_password

from models.collaborator import Collaborator, Role
from models.database import session_scope

from views.setup_view import show_setup_error, show_setup_form, show_setup_success


def ensure_setup():
    with session_scope() as session:
        stmt = select(Collaborator).limit(1)
        existing_collaborator = session.scalar(stmt)

    if existing_collaborator:
        return True

    return _create_initial_collaborator()


def _create_initial_collaborator():
    try:
        first_name, last_name, email, password, password_confirmation = show_setup_form()

        if not all((first_name, last_name, email, password, password_confirmation)):
            show_setup_error("Tous les champs sont obligatoires")
            return False

        if any(c.isdigit() for c in first_name):
            show_setup_error("Le prénom ne peut pas contenir de chiffre")
            return False

        if any(c.isdigit() for c in last_name):
            show_setup_error("Le nom ne peut pas contenir de chiffre")
            return False

        if "@" not in email or "." not in email:
            show_setup_error("L'email est incorrect")
            return False

        email_normalized = email.strip().lower()

        if password != password_confirmation:
            show_setup_error("Les mots de passe ne correspondent pas")
            return False

        collaborator = Collaborator(
            first_name=first_name,
            last_name=last_name,
            email=email_normalized,
            password_hash=hash_password(password),
            role=Role.MANAGEMENT,
            is_active=True,
        )

        with session_scope() as session:
            session.add(collaborator)

        show_setup_success()
        return True

    except Exception:
        show_setup_error("Une erreur est survenue lors de la configuration")
        return False
