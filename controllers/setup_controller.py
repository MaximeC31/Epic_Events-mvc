from sqlalchemy import select

from controllers.authentication_controller import hash_password
from models.collaborator import Collaborator, Role
from models.database import session_scope
from views.setup_view import show_setup_error, show_setup_form, show_setup_success


def ensure_setup():
    with session_scope() as session:
        stmt = select(Collaborator).limit(1)
        is_configured = session.scalar(stmt) is not None

    if is_configured:
        return True

    return _create_initial_collaborator()


def _create_initial_collaborator():
    try:
        first_name, last_name, email, password, password_confirmation = show_setup_form()

        if not all((first_name, last_name, email, password, password_confirmation)):
            show_setup_error("Tous les champs sont obligatoires")
            return False

        if password != password_confirmation:
            show_setup_error("Les mots de passe ne correspondent pas")
            return False

        collaborator = Collaborator(
            first_name=first_name,
            last_name=last_name,
            email=email,
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
