from controllers.authentication_controller import hash_password
from models.collaborator import Collaborator, Role
from models.database import session_scope
from views.setup_view import show_setup_error, show_setup_form, show_setup_success


def run_setup():
    first_name, last_name, email, password, password_confirmation = show_setup_form()

    if password != password_confirmation:
        show_setup_error("Les mots de passe ne correspondent pas")
        return

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
