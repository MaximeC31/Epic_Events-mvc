from datetime import datetime
from typing import cast

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import joinedload

from decorators import require_authenticated_collaborator
from models.client import Client
from models.collaborator import Collaborator, Role
from models.contract import Contract
from models.database import session_scope
from models.event import Event
from views.event_view import (
    prompt_event_contract_selection,
    prompt_event_creation,
    prompt_event_deletion_confirmation,
    prompt_event_id_for_deletion,
    prompt_event_id_for_modification,
    prompt_event_support_assignment,
    prompt_support_event_modification,
    show_empty_event_list,
    show_event_creation_cancelled,
    show_event_creation_success,
    show_event_deletion_cancelled,
    show_event_deletion_success,
    show_event_error,
    show_events,
    show_event_modification_cancelled,
    show_event_modification_success,
    show_event_modification_unchanged,
)


@require_authenticated_collaborator(show_event_error)
def list_events(authenticated_collaborator):
    try:
        with session_scope() as session:
            query = (
                select(Event)
                .options(
                    joinedload(Event.contract).joinedload(Contract.client),
                    joinedload(Event.support),
                )
                .order_by(Event.start_datetime.asc(), Event.id.asc())
            )
            events = session.scalars(query).all()
            session.expunge_all()

    except SQLAlchemyError:
        show_event_error("Une erreur est survenue lors de la consultation des événements.")
        return

    if not events:
        show_empty_event_list()
        return

    show_events(events)


@require_authenticated_collaborator(show_event_error, roles=(Role.SUPPORT,))
def update_support_event(authenticated_collaborator):
    try:
        event_id = int(prompt_event_id_for_modification())
    except ValueError:
        show_event_error("ID invalide.")
        return

    if event_id == 0:
        show_event_modification_cancelled()
        return
    if event_id < 0:
        show_event_error("ID invalide.")
        return

    try:
        with session_scope() as session:
            event = session.scalar(
                select(Event)
                .where(Event.id == event_id)
                .options(
                    joinedload(Event.contract).joinedload(Contract.client),
                    joinedload(Event.support),
                )
            )
            if event is None:
                show_event_error("Événement introuvable.")
                return
            if cast(int | None, event.support_collaborator_id) != authenticated_collaborator.id:
                show_event_error("Vous ne pouvez modifier que vos événements attribués.")
                return
            session.expunge_all()
    except SQLAlchemyError:
        show_event_error("Impossible de récupérer l'événement.")
        return

    start_choice, end_choice, location_choice, participants_choice, notes_choice = (
        prompt_support_event_modification(event)
    )
    try:
        parsed_start = Event.parse_datetime(start_choice) if start_choice else None
        parsed_end = Event.parse_datetime(end_choice) if end_choice else None
    except ValueError as error:
        show_event_error(str(error))
        return

    try:
        parsed_participants = int(participants_choice) if participants_choice else None
    except ValueError:
        show_event_error("Le nombre de participants doit être un entier.")
        return

    try:
        with session_scope() as session:
            current_event = session.get(Event, event_id)
            if current_event is None:
                show_event_error("Événement introuvable.")
                return
            if cast(int | None, current_event.support_collaborator_id) != authenticated_collaborator.id:
                show_event_error("Vous ne pouvez modifier que vos événements attribués.")
                return

            start_datetime = (
                parsed_start if parsed_start is not None else cast(datetime, current_event.start_datetime)
            )
            end_datetime = (
                parsed_end if parsed_end is not None else cast(datetime, current_event.end_datetime)
            )
            location = location_choice if location_choice else cast(str, current_event.location)
            number_of_participants = (
                parsed_participants
                if parsed_participants is not None
                else cast(int, current_event.number_of_participants)
            )
            if notes_choice == "":
                notes = cast(str | None, current_event.notes)
            elif notes_choice == "0":
                notes = None
            else:
                notes = notes_choice

            updated = Event(
                contract_id=cast(int, current_event.contract_id),
                support_collaborator_id=cast(int | None, current_event.support_collaborator_id),
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                location=location,
                number_of_participants=number_of_participants,
                notes=notes,
            )
            validation_error = updated.validation_error()
            if validation_error:
                show_event_error(validation_error)
                return

            if (start_datetime, end_datetime, location, number_of_participants, notes) == (
                current_event.start_datetime,
                current_event.end_datetime,
                current_event.location,
                current_event.number_of_participants,
                current_event.notes,
            ):
                show_event_modification_unchanged()
                return

            setattr(current_event, "start_datetime", start_datetime)
            setattr(current_event, "end_datetime", end_datetime)
            setattr(current_event, "location", location)
            setattr(current_event, "number_of_participants", number_of_participants)
            setattr(current_event, "notes", notes)
    except IntegrityError:
        show_event_error("Impossible de modifier l'événement : données invalides.")
        return
    except SQLAlchemyError:
        show_event_error("Impossible de modifier l'événement.")
        return

    show_event_modification_success()


@require_authenticated_collaborator(show_event_error, roles=(Role.SUPPORT,))
def list_assigned_support_events(authenticated_collaborator):
    try:
        with session_scope() as session:
            query = (
                select(Event)
                .where(Event.support_collaborator_id == authenticated_collaborator.id)
                .options(
                    joinedload(Event.contract).joinedload(Contract.client),
                    joinedload(Event.support),
                )
                .order_by(Event.start_datetime.asc(), Event.id.asc())
            )
            events = session.scalars(query).all()
            session.expunge_all()
    except SQLAlchemyError:
        show_event_error("Impossible de récupérer vos événements attribués.")
        return

    if not events:
        show_empty_event_list()
        return
    show_events(events)


@require_authenticated_collaborator(show_event_error, roles=(Role.SALES,))
def create_event(authenticated_collaborator):
    try:
        with session_scope() as session:
            query = (
                select(Contract)
                .join(Contract.client)
                .where(
                    Contract.is_signed.is_(True),
                    Client.sales_contact_id == authenticated_collaborator.id,
                )
                .options(joinedload(Contract.client))
                .order_by(Contract.created_at.desc(), Contract.id.desc())
            )
            contracts = session.scalars(query).all()
            session.expunge_all()
    except SQLAlchemyError:
        show_event_error("Impossible de récupérer les contrats disponibles.")
        return

    if not contracts:
        show_event_error("Aucun contrat signé de vos clients disponible pour créer un événement.")
        return

    contract_choice = prompt_event_contract_selection(contracts)
    if contract_choice == "0":
        show_event_creation_cancelled()
        return

    try:
        contract_id = int(contract_choice)
    except ValueError:
        show_event_error("ID invalide.")
        return

    if contract_id <= 0:
        show_event_error("ID invalide.")
        return
    if not any(cast(int, contract.id) == contract_id for contract in contracts):
        show_event_error("Contrat indisponible pour créer un événement.")
        return

    start_choice, end_choice, location, participants_choice, notes = prompt_event_creation()
    try:
        start_datetime = Event.parse_datetime(start_choice)
        end_datetime = Event.parse_datetime(end_choice)
    except ValueError as error:
        show_event_error(str(error))
        return

    try:
        number_of_participants = int(participants_choice)
    except ValueError:
        show_event_error("Le nombre de participants doit être un entier.")
        return

    event = Event(
        contract_id=contract_id,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        location=location.strip(),
        number_of_participants=number_of_participants,
        notes=notes.strip() or None,
        support_collaborator_id=None,
    )

    validation_error = event.validation_error()
    if validation_error:
        show_event_error(validation_error)
        return

    try:
        with session_scope() as session:
            query = select(Contract).where(Contract.id == contract_id).options(joinedload(Contract.client))
            contract = session.scalars(query).first()
            if (
                contract is None
                or not cast(bool, contract.is_signed)
                or contract.client.sales_contact_id != authenticated_collaborator.id
            ):
                show_event_error("Contrat indisponible pour créer un événement.")
                return

            session.add(event)
    except IntegrityError:
        show_event_error("Impossible de créer l'événement : données invalides.")
        return
    except SQLAlchemyError:
        show_event_error("Impossible de créer l'événement.")
        return

    show_event_creation_success()


@require_authenticated_collaborator(show_event_error, roles=(Role.MANAGEMENT,))
def delete_event(authenticated_collaborator):
    try:
        event_id = int(prompt_event_id_for_deletion())
    except ValueError:
        show_event_error("ID invalide.")
        return

    if event_id == 0:
        show_event_deletion_cancelled()
        return
    if event_id < 0:
        show_event_error("ID invalide.")
        return

    try:
        with session_scope() as session:
            event = session.scalar(
                select(Event)
                .where(Event.id == event_id)
                .options(
                    joinedload(Event.contract).joinedload(Contract.client),
                    joinedload(Event.support),
                )
            )
            if event is None:
                show_event_error("Événement introuvable.")
                return
            session.expunge_all()
    except SQLAlchemyError:
        show_event_error("Impossible de récupérer l'événement.")
        return

    if not prompt_event_deletion_confirmation(event):
        show_event_deletion_cancelled()
        return

    try:
        with session_scope() as session:
            current_event = session.get(Event, event_id)
            if current_event is None:
                show_event_error("Événement introuvable.")
                return
            session.delete(current_event)
    except SQLAlchemyError:
        show_event_error("Impossible de supprimer l'événement.")
        return

    show_event_deletion_success()


@require_authenticated_collaborator(show_event_error, roles=(Role.MANAGEMENT,))
def assign_event_support(authenticated_collaborator):
    try:
        event_id = int(prompt_event_id_for_modification())
    except ValueError:
        show_event_error("ID invalide.")
        return

    if event_id == 0:
        show_event_modification_cancelled()
        return
    if event_id < 0:
        show_event_error("ID invalide.")
        return

    try:
        with session_scope() as session:
            event = session.scalar(
                select(Event)
                .where(Event.id == event_id)
                .options(
                    joinedload(Event.contract).joinedload(Contract.client),
                    joinedload(Event.support),
                )
            )
            if event is None:
                show_event_error("Événement introuvable.")
                return

            supports = session.scalars(
                select(Collaborator)
                .where(Collaborator.role == Role.SUPPORT, Collaborator.is_active.is_(True))
                .order_by(Collaborator.last_name, Collaborator.first_name, Collaborator.id)
            ).all()
            session.expunge_all()
    except SQLAlchemyError:
        show_event_error("Impossible de récupérer l'événement et les supports.")
        return

    support_choice = prompt_event_support_assignment(event, supports)
    if support_choice == "":
        show_event_modification_unchanged()
        return

    try:
        support_number = int(support_choice)
    except ValueError:
        show_event_error("ID support invalide.")
        return

    if support_number < 0:
        show_event_error("ID support invalide.")
        return

    support_id = support_number if support_number != 0 else None
    if support_id is not None and not any(cast(int, support.id) == support_id for support in supports):
        show_event_error("Support actif introuvable.")
        return

    try:
        with session_scope() as session:
            current_event = session.get(Event, event_id)
            if current_event is None:
                show_event_error("Événement introuvable.")
                return

            if support_id is not None:
                support = session.get(Collaborator, support_id)
                if (
                    support is None
                    or cast(Role, support.role) != Role.SUPPORT
                    or not cast(bool, support.is_active)
                ):
                    show_event_error("Support actif introuvable.")
                    return

            if support_id == cast(int | None, current_event.support_collaborator_id):
                show_event_modification_unchanged()
                return

            setattr(current_event, "support_collaborator_id", support_id)
    except SQLAlchemyError:
        show_event_error("Impossible de modifier l'affectation du support.")
        return

    show_event_modification_success()


@require_authenticated_collaborator(show_event_error, roles=(Role.MANAGEMENT,))
def list_events_without_support(authenticated_collaborator):
    try:
        with session_scope() as session:
            query = (
                select(Event)
                .where(Event.support_collaborator_id.is_(None))
                .options(
                    joinedload(Event.contract).joinedload(Contract.client),
                    joinedload(Event.support),
                )
                .order_by(Event.start_datetime.asc(), Event.id.asc())
            )
            events = session.scalars(query).all()
            session.expunge_all()
    except SQLAlchemyError:
        show_event_error("Impossible de récupérer les événements sans support.")
        return

    if not events:
        show_empty_event_list()
        return
    show_events(events)
