from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from controllers.authentication_controller import hash_password
from decorators import require_authenticated_collaborator
from models.client import Client
from models.collaborator import Collaborator, Role
from models.database import session_scope
from models.event import Event
from views.collaborator_view import (
    prompt_collaborator_creation,
    prompt_collaborator_deletion_confirmation,
    prompt_collaborator_id_for_deletion,
    prompt_collaborator_id_for_modification,
    prompt_collaborator_modification,
    show_collaborator_creation_success,
    show_collaborator_deletion_cancelled,
    show_collaborator_deletion_success,
    show_collaborator_error,
    show_collaborator_modification_cancelled,
    show_collaborator_modification_success,
    show_collaborator_modification_unchanged,
    show_collaborators,
)


@require_authenticated_collaborator(show_collaborator_error, roles=(Role.MANAGEMENT,))
def list_collaborators(authenticated_collaborator):
    try:
        with session_scope() as session:
            collaborators = session.scalars(select(Collaborator).order_by(Collaborator.id)).all()
            session.expunge_all()
    except SQLAlchemyError:
        show_collaborator_error("Impossible de récupérer les collaborateurs.")
        return

    show_collaborators(collaborators)


@require_authenticated_collaborator(show_collaborator_error, roles=(Role.MANAGEMENT,))
def create_collaborator(authenticated_collaborator):
    first_name, last_name, email, password, password_confirmation, role_choice = (
        prompt_collaborator_creation()
    )

    if not all((first_name, last_name, email, password, password_confirmation, role_choice)):
        show_collaborator_error("Tous les champs sont obligatoires.")
        return

    email_normalized = email.strip().lower()

    password_error = Collaborator.check_password_confirmation(password, password_confirmation)
    if password_error:
        show_collaborator_error(password_error)
        return

    try:
        if 1 <= int(role_choice) <= len(Role):
            role = list(Role)[int(role_choice) - 1]
        else:
            raise ValueError
    except ValueError:
        show_collaborator_error("Le numéro de rôle est incorrect.")
        return

    collaborator = Collaborator(
        first_name=first_name.strip(),
        last_name=last_name.strip(),
        email=email_normalized,
        password_hash=hash_password(password),
        role=role,
        is_active=True,
    )

    validation_error = collaborator.validation_error()
    if validation_error:
        show_collaborator_error(validation_error)
        return

    try:
        with session_scope() as session:
            session.add(collaborator)

    except IntegrityError:
        show_collaborator_error("Impossible de créer le collaborateur : données invalides ou déjà utilisées.")
        return
    except SQLAlchemyError:
        show_collaborator_error("Impossible de créer le collaborateur.")
        return

    show_collaborator_creation_success()


@require_authenticated_collaborator(show_collaborator_error, roles=(Role.MANAGEMENT,))
def delete_collaborator(authenticated_collaborator) -> None:
    try:
        collaborator_id = int(prompt_collaborator_id_for_deletion())

        if collaborator_id == 0:
            show_collaborator_deletion_cancelled()
            return
    except ValueError:
        show_collaborator_error("ID invalide.")
        return

    try:
        with session_scope() as session:
            collaborator = session.get(Collaborator, collaborator_id)

            if collaborator is None:
                show_collaborator_error("Collaborateur introuvable.")
                return

            session.expunge(collaborator)

            if collaborator.id == authenticated_collaborator.id:
                show_collaborator_error("Vous ne pouvez pas supprimer votre propre compte.")
                return

            if not prompt_collaborator_deletion_confirmation(collaborator):
                show_collaborator_deletion_cancelled()
                return
    except SQLAlchemyError:
        show_collaborator_error("Impossible de récupérer le collaborateur.")
        return

    try:
        with session_scope() as session:
            current = session.get(Collaborator, collaborator.id)
            if current is None:
                show_collaborator_error("Collaborateur introuvable.")
                return

            session.delete(current)
    except SQLAlchemyError:
        show_collaborator_error("Impossible de supprimer le collaborateur.")
        return

    show_collaborator_deletion_success()


@require_authenticated_collaborator(show_collaborator_error, roles=(Role.MANAGEMENT,))
def update_collaborator(authenticated_collaborator):
    try:
        collaborator_id = int(prompt_collaborator_id_for_modification())

        if collaborator_id == 0:
            show_collaborator_modification_cancelled()
            return
    except ValueError:
        show_collaborator_error("ID invalide.")
        return

    try:
        with session_scope() as session:
            collaborator = session.get(Collaborator, collaborator_id)

            if collaborator is None:
                show_collaborator_error("Collaborateur introuvable.")
                return

            session.expunge(collaborator)
    except SQLAlchemyError:
        show_collaborator_error("Impossible de récupérer le collaborateur.")
        return

    is_self_update = collaborator.id == authenticated_collaborator.id
    first_name, last_name, email, role_choice, status_choice = prompt_collaborator_modification(
        is_self_update, collaborator
    )

    if is_self_update and (role_choice or status_choice):
        show_collaborator_error("Vous ne pouvez pas modifier votre propre rôle ou statut.")
        return

    first_name = collaborator.first_name if first_name == "" else first_name
    last_name = collaborator.last_name if last_name == "" else last_name
    email = collaborator.email if email == "" else email.lower()
    role = collaborator.role
    is_active = collaborator.is_active

    if role_choice:
        try:
            role = Collaborator.parse_role_choice(role_choice)
        except ValueError as error:
            show_collaborator_error(str(error))
            return

    if status_choice:
        try:
            is_active = Collaborator.parse_status_choice(status_choice)
        except ValueError as error:
            show_collaborator_error(str(error))
            return

    updated = Collaborator(
        first_name=first_name,
        last_name=last_name,
        email=email,
        role=role,
        is_active=is_active,
    )

    validation_error = updated.validation_error()
    if validation_error:
        show_collaborator_error(validation_error)
        return

    try:
        with session_scope() as session:
            collaborator = session.get(Collaborator, collaborator.id)

            if collaborator is None:
                show_collaborator_error("Collaborateur introuvable.")
                return

            if collaborator.id == authenticated_collaborator.id and (
                role is not Role.MANAGEMENT or not is_active
            ):
                show_collaborator_error("Vous ne pouvez pas modifier votre propre rôle ou statut.")
                return

            if collaborator.role is Role.SALES and role is not Role.SALES:
                if session.scalar(
                    select(Client.id).where(Client.sales_contact_id == collaborator.id).limit(1)
                ):
                    show_collaborator_error("Ce commercial est associé à des clients.")
                    return

            if collaborator.role is Role.SUPPORT and role is not Role.SUPPORT:
                if session.scalar(
                    select(Event.id).where(Event.support_collaborator_id == collaborator.id).limit(1)
                ):
                    show_collaborator_error("Ce support est affecté à des événements.")
                    return

            if (first_name, last_name, email, role, is_active) == (
                collaborator.first_name,
                collaborator.last_name,
                collaborator.email,
                collaborator.role,
                collaborator.is_active,
            ):
                show_collaborator_modification_unchanged()
                return

            setattr(collaborator, "first_name", first_name)
            setattr(collaborator, "last_name", last_name)
            setattr(collaborator, "email", email)
            setattr(collaborator, "role", role)
            setattr(collaborator, "is_active", is_active)

    except IntegrityError:
        show_collaborator_error(
            "Impossible de modifier le collaborateur : données invalides ou déjà utilisées."
        )
        return

    except SQLAlchemyError:
        show_collaborator_error("Impossible de modifier le collaborateur.")
        return

    if is_self_update:
        authenticated_collaborator.first_name = first_name
        authenticated_collaborator.last_name = last_name
        authenticated_collaborator.email = email

    show_collaborator_modification_success()
