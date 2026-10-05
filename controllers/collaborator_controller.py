from typing import cast

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

    password_error = Collaborator.check_password(password)
    if password_error:
        show_collaborator_error(password_error)
        return

    password_error = Collaborator.check_password_confirmation(password, password_confirmation)
    if password_error:
        show_collaborator_error(password_error)
        return

    try:
        role = Collaborator.parse_role_choice(role_choice)
    except ValueError as error:
        show_collaborator_error(str(error))
        return

    try:
        password_hash = hash_password(password)
    except ValueError:
        show_collaborator_error("Impossible de sécuriser le mot de passe.")
        return

    collaborator = Collaborator(
        first_name=first_name.strip(),
        last_name=last_name.strip(),
        email=email_normalized,
        password_hash=password_hash,
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
            current_collaborator = session.get(Collaborator, collaborator_id)
            if current_collaborator is None:
                show_collaborator_error("Collaborateur introuvable.")
                return

            session.delete(current_collaborator)
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
    first_name_input, last_name_input, email_input, role_choice, status_choice = prompt_collaborator_modification(
        is_self_update, collaborator
    )

    if is_self_update and (role_choice or status_choice):
        show_collaborator_error("Vous ne pouvez pas modifier votre propre rôle ou statut.")
        return

    parsed_role = None
    parsed_status = None

    if role_choice:
        try:
            parsed_role = Collaborator.parse_role_choice(role_choice)
        except ValueError as error:
            show_collaborator_error(str(error))
            return

    if status_choice:
        try:
            parsed_status = Collaborator.parse_status_choice(status_choice)
        except ValueError as error:
            show_collaborator_error(str(error))
            return

    try:
        with session_scope() as session:
            current_collaborator = session.get(Collaborator, collaborator_id)

            if current_collaborator is None:
                show_collaborator_error("Collaborateur introuvable.")
                return

            first_name = cast(str, current_collaborator.first_name) if first_name_input == "" else first_name_input
            last_name = cast(str, current_collaborator.last_name) if last_name_input == "" else last_name_input
            email = cast(str, current_collaborator.email) if email_input == "" else email_input.lower()
            role = parsed_role if parsed_role is not None else cast(Role, current_collaborator.role)
            is_active = parsed_status if parsed_status is not None else cast(bool, current_collaborator.is_active)
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

            if current_collaborator.id == authenticated_collaborator.id and (
                role is not Role.MANAGEMENT or not is_active
            ):
                show_collaborator_error("Vous ne pouvez pas modifier votre propre rôle ou statut.")
                return

            if current_collaborator.role is Role.SALES and role is not Role.SALES:
                if session.scalar(
                    select(Client.id).where(Client.sales_contact_id == collaborator_id).limit(1)
                ) is not None:
                    show_collaborator_error("Ce commercial est associé à des clients.")
                    return

            if current_collaborator.role is Role.SUPPORT and role is not Role.SUPPORT:
                if session.scalar(
                    select(Event.id).where(Event.support_collaborator_id == collaborator_id).limit(1)
                ) is not None:
                    show_collaborator_error("Ce support est affecté à des événements.")
                    return

            has_changes = (first_name, last_name, email, role, is_active) != (
                current_collaborator.first_name,
                current_collaborator.last_name,
                current_collaborator.email,
                current_collaborator.role,
                current_collaborator.is_active,
            )

            if has_changes:
                setattr(current_collaborator, "first_name", first_name)
                setattr(current_collaborator, "last_name", last_name)
                setattr(current_collaborator, "email", email)
                setattr(current_collaborator, "role", role)
                setattr(current_collaborator, "is_active", is_active)

    except IntegrityError:
        show_collaborator_error(
            "Impossible de modifier le collaborateur : données invalides ou déjà utilisées."
        )
        return

    except SQLAlchemyError:
        show_collaborator_error("Impossible de modifier le collaborateur.")
        return

    if is_self_update:
        setattr(authenticated_collaborator, "first_name", first_name)
        setattr(authenticated_collaborator, "last_name", last_name)
        setattr(authenticated_collaborator, "email", email)

    if not has_changes:
        show_collaborator_modification_unchanged()
        return

    show_collaborator_modification_success()
