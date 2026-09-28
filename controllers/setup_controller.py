from sqlalchemy import select

from controllers.authentication_controller import hash_password
from models.collaborator import Collaborator, Role
from models.database import session_scope
from views.setup_view import prompt_setup_form, show_setup_error, show_setup_success


def ensure_setup():
    with session_scope() as session:
        stmt = select(Collaborator).limit(1)
        existing_collaborator = session.scalar(stmt)

    if existing_collaborator:
        return True

    return _create_initial_collaborator()


def _create_initial_collaborator():
    try:
        first_name, last_name, email, password, password_confirmation = prompt_setup_form()

        if not all((first_name, last_name, email, password, password_confirmation)):
            show_setup_error("Tous les champs sont obligatoires")
            return False

        email_normalized = email.strip().lower()

        password_error = Collaborator.check_password_confirmation(password, password_confirmation)
        if password_error:
            show_setup_error(password_error)
            return False

        collaborator = Collaborator(
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            email=email_normalized,
            password_hash=hash_password(password),
            role=Role.MANAGEMENT,
            is_active=True,
        )

        validation_error = collaborator.validation_error()
        if validation_error:
            show_setup_error(validation_error)
            return False

        with session_scope() as session:
            session.add(collaborator)

        show_setup_success()
        return True

    except Exception:
        show_setup_error("Une erreur est survenue lors de la configuration")
        return False
