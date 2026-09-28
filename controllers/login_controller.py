from sqlalchemy import func, select

from controllers.authentication_controller import verify_password
from models.collaborator import Collaborator, Role
from models.database import session_scope
from views.login_view import prompt_login_form, show_login_error


def run_login():
    email, password = prompt_login_form()

    if not email or not password:
        return show_login_error("L'un des champs ne peut pas être vide")

    email_error = Collaborator.check_email(email)
    if email_error:
        show_login_error(email_error)
        return

    with session_scope() as session:
        email = email.strip().lower()
        stmt = select(Collaborator).where(func.lower(Collaborator.email) == email)
        collaborator = session.scalar(stmt)

        if collaborator is None:
            show_login_error("Cet utilisateur n'existe pas")
            return

        if collaborator.is_active is False:
            show_login_error("Compte désactivé")
            return

        if not verify_password(password, collaborator.password_hash):
            show_login_error("Mot de passe invalide")
            return

        if not isinstance(collaborator.role, Role):
            show_login_error("Rôle invalide")
            return

        session.expunge(collaborator)

    return collaborator
