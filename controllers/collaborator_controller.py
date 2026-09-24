from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from controllers.authentication_controller import hash_password

from decorators import require_authenticated_collaborator

from models.collaborator import Collaborator, Role
from models.database import session_scope

from views.collaborator_view import (
    prompt_collaborator_creation,
    prompt_collaborator_deletion_confirmation,
    prompt_collaborator_id_for_deletion,
    show_collaborator_creation_success,
    show_collaborator_deletion_cancelled,
    show_collaborator_deletion_success,
    show_collaborator_error,
)


@require_authenticated_collaborator(show_collaborator_error)
def create_collaborator(authenticated_collaborator):
    if authenticated_collaborator.role is not Role.MANAGEMENT:
        show_collaborator_error("Vous n'avez pas la permission de créer un collaborateur.")
        return

    first_name, last_name, email, password, password_confirmation, role_choice = (
        prompt_collaborator_creation()
    )

    if not all((first_name, last_name, email, password, password_confirmation, role_choice)):
        show_collaborator_error("Tous les champs sont obligatoires.")
        return

    if any(c.isdigit() for c in first_name):
        show_collaborator_error("Le prénom ne peut pas contenir de chiffre.")
        return

    if any(c.isdigit() for c in last_name):
        show_collaborator_error("Le nom ne peut pas contenir de chiffre.")
        return

    email_normalized = email.strip().lower()
    if "@" not in email_normalized or "." not in email_normalized:
        show_collaborator_error("L'email est incorrect.")
        return

    if password != password_confirmation:
        show_collaborator_error("Les mots de passe ne correspondent pas.")
        return

    roles = list(Role)
    try:
        role_number = int(role_choice)
    except ValueError:
        show_collaborator_error("Le numéro de rôle est incorrect.")
        return

    if role_number < 1 or role_number > len(roles):
        show_collaborator_error("Le numéro de rôle est incorrect.")
        return
    role = roles[role_number - 1]

    try:
        with session_scope() as session:
            query = select(Collaborator).where(func.lower(Collaborator.email) == email_normalized)
            already_exists = session.scalar(query)

            if already_exists:
                show_collaborator_error("Un collaborateur avec cet email existe déjà.")
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
        show_collaborator_error("Un collaborateur avec cet email existe déjà.")
        return
    except SQLAlchemyError:
        show_collaborator_error("Impossible de créer le collaborateur.")
        return

    show_collaborator_creation_success()


@require_authenticated_collaborator(show_collaborator_error)
def delete_collaborator(authenticated_collaborator) -> None:
    if authenticated_collaborator.role is not Role.MANAGEMENT:
        show_collaborator_error("Accès réservé à la gestion.")
        return

    try:
        with session_scope() as session:
            collaborators = session.scalars(select(Collaborator)).all()
            session.expunge_all()
    except SQLAlchemyError:
        show_collaborator_error("Impossible de récupérer les collaborateurs.")
        return

    if not collaborators:
        show_collaborator_error("Aucun collaborateur à supprimer.")
        return

    try:
        collaborator_id = int(prompt_collaborator_id_for_deletion(collaborators))
    except ValueError:
        show_collaborator_error("ID invalide.")
        return

    if collaborator_id == 0:
        show_collaborator_deletion_cancelled()
        return

    collaborator = None
    for c in collaborators:
        if c.id == collaborator_id:
            collaborator = c
            break

    if collaborator is None:
        show_collaborator_error("Collaborateur introuvable.")
        return

    if collaborator.id == authenticated_collaborator.id:
        show_collaborator_error("Vous ne pouvez pas supprimer votre propre compte.")
        return

    if not prompt_collaborator_deletion_confirmation(collaborator):
        show_collaborator_deletion_cancelled()
        return

    try:
        with session_scope() as session:
            actor = session.get(Collaborator, authenticated_collaborator.id)
            if actor is None or actor.is_active is False or actor.role is not Role.MANAGEMENT:
                show_collaborator_error("Accès réservé à la gestion.")
                return

            current = session.get(Collaborator, collaborator.id)
            if current is None:
                show_collaborator_error("Collaborateur introuvable.")
                return

            session.delete(current)
    except SQLAlchemyError:
        show_collaborator_error("Impossible de supprimer le collaborateur.")
        return

    show_collaborator_deletion_success()
