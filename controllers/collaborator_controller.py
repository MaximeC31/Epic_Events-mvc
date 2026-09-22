from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from controllers.authentication_controller import hash_password

from decorators import require_authenticated_collaborator

from models.collaborator import Collaborator, Role
from models.database import session_scope

from views.collaborator_view import (
    show_collaborator_creation_error,
    show_collaborator_creation_success,
    show_create_collaborator_form,
)


@require_authenticated_collaborator(show_collaborator_creation_error)
def create_collaborator(authenticated_collaborator):
    if authenticated_collaborator.role is not Role.MANAGEMENT:
        show_collaborator_creation_error("Vous n'avez pas la permission de créer un collaborateur.")
        return

    first_name, last_name, email, password, password_confirmation, role_choice = (
        show_create_collaborator_form()
    )

    if not all((first_name, last_name, email, password, password_confirmation, role_choice)):
        show_collaborator_creation_error("Tous les champs sont obligatoires.")
        return

    if password != password_confirmation:
        show_collaborator_creation_error("Les mots de passe ne correspondent pas.")
        return

    roles_by_choice = {
        "1": Role.MANAGEMENT,
        "2": Role.SALES,
        "3": Role.SUPPORT,
    }
    role = roles_by_choice.get(role_choice)
    if role is None:
        show_collaborator_creation_error("Rôle invalide sélectionné.")
        return

    email_normalized = email.strip().lower()

    try:
        with session_scope() as session:
            query = select(Collaborator).where(func.lower(Collaborator.email) == email_normalized)
            already_exists = session.scalar(query)

            if already_exists:
                show_collaborator_creation_error("Un collaborateur avec cet email existe déjà.")
                return

            session.add(
                Collaborator(
                    first_name=first_name.strip(),
                    last_name=last_name.strip(),
                    email=email_normalized,
                    password_hash=hash_password(password),
                    role=role,
                    is_active=True,
                )
            )

    except IntegrityError:
        show_collaborator_creation_error("Un collaborateur avec cet email existe déjà.")
        return
    except SQLAlchemyError:
        show_collaborator_creation_error("Impossible de créer le collaborateur.")
        return

    show_collaborator_creation_success()
