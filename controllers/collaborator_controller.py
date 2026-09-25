from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from controllers.authentication_controller import hash_password

from decorators import require_authenticated_collaborator

from models.collaborator import Collaborator, Role
from models.client import Client
from models.database import session_scope
from models.event import Event

from views.collaborator_view import (
    prompt_collaborator_creation,
    prompt_collaborator_deletion_confirmation,
    prompt_collaborator_id_for_deletion,
    show_collaborator_creation_success,
    show_collaborator_deletion_cancelled,
    show_collaborator_deletion_success,
    show_collaborator_error,
    prompt_collaborator_id_for_modification,
    prompt_collaborator_modification,
    show_collaborator_modification_cancelled,
    show_collaborator_modification_success,
    show_collaborator_modification_unchanged,
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
        if collaborator_id == 0:
            show_collaborator_deletion_cancelled()
            return
    except ValueError:
        show_collaborator_error("ID invalide.")
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


@require_authenticated_collaborator(show_collaborator_error)
def update_collaborateur(authenticated_collaborator):
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
        show_collaborator_error("Aucun collaborateur à modifier.")
        return

    try:
        collaborator_id = int(prompt_collaborator_id_for_modification(collaborators))
        if collaborator_id == 0:
            show_collaborator_modification_cancelled()
            return
    except ValueError:
        show_collaborator_error("ID invalide.")
        return

    collaborator = None
    for c in collaborators:
        if c.id == collaborator_id:
            collaborator = c
            break
    if collaborator is None:
        show_collaborator_error("Collaborateur introuvable.")
        return

    is_self_update = collaborator.id == authenticated_collaborator.id
    first_name, last_name, email, role_choice, status_choice = prompt_collaborator_modification(
        is_self_update, collaborator
    )

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

            first_name = current.first_name if first_name == "" else first_name
            last_name = current.last_name if last_name == "" else last_name
            email = current.email if email == "" else email.lower()
            role = current.role
            is_active = current.is_active

            if any(c.isdigit() for c in first_name):
                show_collaborator_error("Le prénom ne peut pas contenir de chiffre.")
                return
            if any(c.isdigit() for c in last_name):
                show_collaborator_error("Le nom ne peut pas contenir de chiffre.")
                return
            if "@" not in email or "." not in email:
                show_collaborator_error("L'email est incorrect.")
                return

            if role_choice != "":
                try:
                    role_number = int(role_choice)
                except ValueError:
                    show_collaborator_error("Le numéro de rôle est incorrect.")
                    return
                roles = list(Role)
                if role_number < 1 or role_number > len(roles):
                    show_collaborator_error("Le numéro de rôle est incorrect.")
                    return
                role = roles[role_number - 1]

            if status_choice != "":
                if status_choice not in ("0", "1"):
                    show_collaborator_error("Le statut est incorrect.")
                    return
                is_active = status_choice == "1"

            if current.role is Role.SALES and role is not Role.SALES:
                if session.scalar(select(Client.id).where(Client.sales_contact_id == current.id).limit(1)):
                    show_collaborator_error("Ce commercial est associé à des clients.")
                    return

            if current.role is Role.SUPPORT and role is not Role.SUPPORT:
                if session.scalar(
                    select(Event.id).where(Event.support_collaborator_id == current.id).limit(1)
                ):
                    show_collaborator_error("Ce support est affecté à des événements.")
                    return

            if session.scalar(
                select(Collaborator.id).where(
                    func.lower(Collaborator.email) == email.lower(),
                    Collaborator.id != current.id,
                )
            ):
                show_collaborator_error("Un collaborateur avec cet email existe déjà.")
                return

            if (first_name, last_name, email, role, is_active) == (
                current.first_name,
                current.last_name,
                current.email,
                current.role,
                current.is_active,
            ):
                show_collaborator_modification_unchanged()
                return

            setattr(current, "first_name", first_name)
            setattr(current, "last_name", last_name)
            setattr(current, "email", email)
            setattr(current, "role", role)
            setattr(current, "is_active", is_active)
    except IntegrityError:
        show_collaborator_error("Un collaborateur avec cet email existe déjà.")
        return
    except SQLAlchemyError:
        show_collaborator_error("Impossible de modifier le collaborateur.")
        return

    if is_self_update:
        authenticated_collaborator.first_name = first_name
        authenticated_collaborator.last_name = last_name
        authenticated_collaborator.email = email
    show_collaborator_modification_success()
