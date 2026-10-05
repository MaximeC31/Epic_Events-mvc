from decimal import Decimal
from typing import cast

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import selectinload

from decorators import require_authenticated_collaborator
from models.client import Client
from models.collaborator import Role
from models.contract import Contract
from models.database import session_scope
from models.event import Event
from views.contract_view import (
    prompt_contract_amount,
    prompt_contract_client_selection,
    prompt_contract_deletion_confirmation,
    prompt_contract_filter,
    prompt_contract_id_for_deletion,
    prompt_contract_id_for_modification,
    prompt_contract_modification,
    show_contract_creation_cancelled,
    show_contract_creation_success,
    show_contract_deletion_cancelled,
    show_contract_deletion_success,
    show_contract_error,
    show_contract_modification_cancelled,
    show_contract_modification_success,
    show_contract_modification_unchanged,
    show_contracts,
    show_empty_contract_list,
    show_empty_filtered_contract_list,
)


@require_authenticated_collaborator(show_contract_error)
def list_contracts(authenticated_collaborator):
    try:
        with session_scope() as session:
            contracts = session.scalars(
                select(Contract)
                .options(selectinload(Contract.client).selectinload(Client.sales_contact))
                .order_by(Contract.created_at.desc(), Contract.id.desc())
            ).all()

            session.expunge_all()

    except SQLAlchemyError:
        show_contract_error("Impossible de récupérer la liste des contrats.")
        return

    if not contracts:
        show_empty_contract_list()
        return

    show_contracts(contracts)


@require_authenticated_collaborator(show_contract_error, roles=(Role.MANAGEMENT,))
def create_contract(authenticated_collaborator):
    try:
        with session_scope() as session:
            clients = session.scalars(
                select(Client).order_by(
                    func.lower(Client.last_name), func.lower(Client.first_name), Client.id
                )
            ).all()
            session.expunge_all()
    except SQLAlchemyError:
        show_contract_error("Impossible de récupérer les clients.")
        return

    if not clients:
        show_contract_error("Aucun client disponible pour créer un contrat.")
        return

    client_choice = prompt_contract_client_selection(clients)
    if client_choice == "0":
        show_contract_creation_cancelled()
        return

    try:
        client_id = int(client_choice)
    except ValueError:
        show_contract_error("ID invalide.")
        return

    if client_id <= 0:
        show_contract_error("ID invalide.")
        return

    if not any(cast(int, client.id) == client_id for client in clients):
        show_contract_error("Client introuvable.")
        return

    amount_choice = prompt_contract_amount()
    try:
        total_amount = Contract.parse_amount(amount_choice)
    except ValueError as error:
        show_contract_error(str(error))
        return

    contract = Contract(
        client_id=client_id,
        total_amount=total_amount,
        remaining_amount=total_amount,
        is_signed=False,
    )

    validation_error = contract.validation_error()
    if validation_error:
        show_contract_error(validation_error)
        return

    try:
        with session_scope() as session:
            if session.get(Client, client_id) is None:
                show_contract_error("Client introuvable.")
                return

            session.add(contract)
    except IntegrityError:
        show_contract_error("Impossible de créer le contrat : données invalides.")
        return
    except SQLAlchemyError:
        show_contract_error("Impossible de créer le contrat.")
        return

    show_contract_creation_success()


@require_authenticated_collaborator(show_contract_error, roles=(Role.MANAGEMENT,))
def delete_contract(authenticated_collaborator):
    try:
        contract_id = int(prompt_contract_id_for_deletion())
    except ValueError:
        show_contract_error("ID invalide.")
        return

    if contract_id == 0:
        show_contract_deletion_cancelled()
        return
    if contract_id < 0:
        show_contract_error("ID invalide.")
        return

    try:
        with session_scope() as session:
            contract = session.scalar(
                select(Contract).options(selectinload(Contract.client)).where(Contract.id == contract_id)
            )

            if contract is None:
                show_contract_error("Contrat introuvable.")
                return

            session.expunge_all()
    except SQLAlchemyError:
        show_contract_error("Impossible de récupérer le contrat.")
        return

    if not prompt_contract_deletion_confirmation(contract):
        show_contract_deletion_cancelled()
        return

    try:
        with session_scope() as session:
            current_contract = session.get(Contract, contract_id)
            if current_contract is None:
                show_contract_error("Contrat introuvable.")
                return

            has_event = session.scalar(select(Event.id).where(Event.contract_id == contract_id).limit(1))
            if has_event is not None:
                show_contract_error("Impossible de supprimer un contrat associé à un événement.")
                return

            session.delete(current_contract)
    except SQLAlchemyError:
        show_contract_error("Impossible de supprimer le contrat.")
        return

    show_contract_deletion_success()


@require_authenticated_collaborator(show_contract_error, roles=(Role.MANAGEMENT,))
def update_contract(authenticated_collaborator):
    try:
        contract_id = int(prompt_contract_id_for_modification())
    except ValueError:
        show_contract_error("ID invalide.")
        return

    if contract_id == 0:
        show_contract_modification_cancelled()
        return
    if contract_id < 0:
        show_contract_error("ID invalide.")
        return

    try:
        with session_scope() as session:
            contract = session.scalar(
                select(Contract).options(selectinload(Contract.client)).where(Contract.id == contract_id)
            )
            if contract is None:
                show_contract_error("Contrat introuvable.")
                return

            clients = session.scalars(
                select(Client).order_by(
                    func.lower(Client.last_name), func.lower(Client.first_name), Client.id
                )
            ).all()
            session.expunge_all()
    except SQLAlchemyError:
        show_contract_error("Impossible de récupérer le contrat.")
        return

    client_input, total_input, remaining_input, status_input = prompt_contract_modification(
        contract, clients
    )

    parsed_client_id = None

    if client_input:
        try:
            parsed_client_id = int(client_input)
        except ValueError:
            show_contract_error("ID client invalide.")
            return

        if parsed_client_id <= 0:
            show_contract_error("ID client invalide.")
            return

        if not any(cast(int, client.id) == parsed_client_id for client in clients):
            show_contract_error("Client introuvable.")
            return

    try:
        parsed_total = Contract.parse_amount(total_input) if total_input else None
        parsed_remaining = Contract.parse_amount(remaining_input) if remaining_input else None
    except ValueError as error:
        show_contract_error(str(error))
        return

    if status_input not in ("", "0", "1"):
        show_contract_error("Le statut est incorrect.")
        return

    parsed_signed = None if status_input == "" else status_input == "1"

    try:
        with session_scope() as session:
            current_contract = session.get(Contract, contract_id)
            if current_contract is None:
                show_contract_error("Contrat introuvable.")
                return

            client_id = (
                parsed_client_id if parsed_client_id is not None else cast(int, current_contract.client_id)
            )
            total_amount = (
                parsed_total if parsed_total is not None else cast(Decimal, current_contract.total_amount)
            )
            remaining_amount = (
                parsed_remaining
                if parsed_remaining is not None
                else cast(Decimal, current_contract.remaining_amount)
            )
            is_signed = (
                parsed_signed if parsed_signed is not None else cast(bool, current_contract.is_signed)
            )
            updated = Contract(
                client_id=client_id,
                total_amount=total_amount,
                remaining_amount=remaining_amount,
                is_signed=is_signed,
            )
            validation_error = updated.validation_error()
            if validation_error:
                show_contract_error(validation_error)
                return

            if client_id != cast(int, current_contract.client_id):
                if session.get(Client, client_id) is None:
                    show_contract_error("Client introuvable.")
                    return
                has_event = session.scalar(select(Event.id).where(Event.contract_id == contract_id).limit(1))

                if has_event is not None:
                    show_contract_error(
                        "Impossible de changer le client d'un contrat associé à un événement."
                    )
                    return

            if (client_id, total_amount, remaining_amount, is_signed) == (
                current_contract.client_id,
                current_contract.total_amount,
                current_contract.remaining_amount,
                current_contract.is_signed,
            ):
                show_contract_modification_unchanged()
                return

            setattr(current_contract, "client_id", client_id)
            setattr(current_contract, "total_amount", total_amount)
            setattr(current_contract, "remaining_amount", remaining_amount)
            setattr(current_contract, "is_signed", is_signed)
    except IntegrityError:
        show_contract_error("Impossible de modifier le contrat : données invalides.")
        return
    except SQLAlchemyError:
        show_contract_error("Impossible de modifier le contrat.")
        return

    show_contract_modification_success()


@require_authenticated_collaborator(show_contract_error, roles=(Role.SALES,))
def update_sales_contract(authenticated_collaborator):
    try:
        contract_id = int(prompt_contract_id_for_modification())
    except ValueError:
        show_contract_error("ID invalide.")
        return

    if contract_id == 0:
        show_contract_modification_cancelled()
        return
    if contract_id < 0:
        show_contract_error("ID invalide.")
        return

    try:
        with session_scope() as session:
            contract = session.scalar(
                select(Contract).options(selectinload(Contract.client)).where(Contract.id == contract_id)
            )
            if contract is None:
                show_contract_error("Contrat introuvable.")
                return
            if contract.client.sales_contact_id != authenticated_collaborator.id:
                show_contract_error("Vous ne pouvez modifier que les contrats de vos clients.")
                return
            session.expunge_all()
    except SQLAlchemyError:
        show_contract_error("Impossible de récupérer le contrat.")
        return

    _, total_choice, remaining_choice, status_choice = prompt_contract_modification(contract)
    try:
        parsed_total = Contract.parse_amount(total_choice) if total_choice else None
        parsed_remaining = Contract.parse_amount(remaining_choice) if remaining_choice else None
    except ValueError as error:
        show_contract_error(str(error))
        return

    if status_choice not in ("", "0", "1"):
        show_contract_error("Le statut est incorrect.")
        return

    try:
        with session_scope() as session:
            current_contract = session.scalar(
                select(Contract).options(selectinload(Contract.client)).where(Contract.id == contract_id)
            )
            if current_contract is None:
                show_contract_error("Contrat introuvable.")
                return
            if current_contract.client.sales_contact_id != authenticated_collaborator.id:
                show_contract_error("Vous ne pouvez modifier que les contrats de vos clients.")
                return

            total_amount = (
                parsed_total if parsed_total is not None else cast(Decimal, current_contract.total_amount)
            )
            remaining_amount = (
                parsed_remaining if parsed_remaining is not None else cast(Decimal, current_contract.remaining_amount)
            )
            is_signed = cast(bool, current_contract.is_signed) if status_choice == "" else status_choice == "1"
            updated = Contract(
                client_id=cast(int, current_contract.client_id),
                total_amount=total_amount,
                remaining_amount=remaining_amount,
                is_signed=is_signed,
            )
            validation_error = updated.validation_error()
            if validation_error:
                show_contract_error(validation_error)
                return

            if (total_amount, remaining_amount, is_signed) == (
                current_contract.total_amount,
                current_contract.remaining_amount,
                current_contract.is_signed,
            ):
                show_contract_modification_unchanged()
                return

            setattr(current_contract, "total_amount", total_amount)
            setattr(current_contract, "remaining_amount", remaining_amount)
            setattr(current_contract, "is_signed", is_signed)
    except IntegrityError:
        show_contract_error("Impossible de modifier le contrat : données invalides.")
        return
    except SQLAlchemyError:
        show_contract_error("Impossible de modifier le contrat.")
        return

    show_contract_modification_success()


@require_authenticated_collaborator(show_contract_error, roles=(Role.SALES,))
def list_filtered_sales_contracts(authenticated_collaborator):
    choice = prompt_contract_filter()
    if choice == "0":
        return
    if choice not in ("1", "2"):
        show_contract_error("Choix invalide.")
        return

    try:
        with session_scope() as session:
            query = (
                select(Contract)
                .join(Contract.client)
                .where(Client.sales_contact_id == authenticated_collaborator.id)
                .options(selectinload(Contract.client).selectinload(Client.sales_contact))
                .order_by(Contract.created_at.desc(), Contract.id.desc())
            )
            if choice == "1":
                query = query.where(Contract.is_signed.is_(False))
            else:
                query = query.where(Contract.remaining_amount > 0)
            contracts = session.scalars(query).all()
            session.expunge_all()
    except SQLAlchemyError:
        show_contract_error("Impossible de récupérer les contrats filtrés.")
        return

    if not contracts:
        show_empty_filtered_contract_list()
        return
    show_contracts(contracts)
