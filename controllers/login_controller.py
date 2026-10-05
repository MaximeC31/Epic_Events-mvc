from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError

from controllers.authentication_controller import verify_password
from models.collaborator import Collaborator, Role
from models.database import session_scope
from views.login_view import prompt_login_form, show_login_error


def run_login():
    email, password = prompt_login_form()

    if not email or not password:
        show_login_error("L'un des champs ne peut pas être vide")
        return

    email_error = Collaborator.check_email(email)
    if email_error:
        show_login_error(email_error)
        return

    password_error = Collaborator.check_password(password)
    if password_error:
        show_login_error(password_error)
        return

    try:
        with session_scope() as session:
            email = email.strip().lower()
            query = select(Collaborator).where(func.lower(Collaborator.email) == email)
            authenticated_collaborator = session.scalar(query)

            if authenticated_collaborator is None:
                show_login_error("Cet utilisateur n'existe pas")
                return

            if authenticated_collaborator.is_active is False:
                show_login_error("Compte désactivé")
                return

            if not verify_password(password, authenticated_collaborator.password_hash):
                show_login_error("Mot de passe invalide")
                return

            if not isinstance(authenticated_collaborator.role, Role):
                show_login_error("Rôle invalide")
                return

            session.expunge(authenticated_collaborator)
    except SQLAlchemyError:
        show_login_error("Une erreur est survenue lors de la connexion")
        return None

    return authenticated_collaborator
