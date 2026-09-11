from views.login_view import show_login_form, show_login_error, show_login_success
from models.database import session_scope
from controllers.authentication_controller import verify_password
from models.collaborator import Role, Collaborator
from sqlalchemy import select, func


def run_login():
    email, password = show_login_form()

    if not email or not password:
        return show_login_error("L'un des champs ne peut pas être vide")

    with session_scope() as session:
        email = email.lower()
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

    show_login_success(collaborator)
    return collaborator
