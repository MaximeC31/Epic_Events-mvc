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
)


@require_authenticated_collaborator(show_contract_error)
def list_contracts(collaborator):
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
def create_contract(collaborator):
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
        prompt_client_id = int(client_choice)
    except ValueError:
        show_contract_error("ID invalide.")
        return

    if prompt_client_id <= 0:
        show_contract_error("ID invalide.")
        return

    client_exists = False
    for client in clients:
        if cast(int, client.id) == prompt_client_id:
            client_exists = True
            break

    if not client_exists:
        show_contract_error("Client introuvable.")
        return

    amount_choice = prompt_contract_amount()
    try:
        total_amount = Contract.parse_amount(amount_choice)
    except ValueError as error:
        show_contract_error(str(error))
        return

    contract = Contract(
        client_id=prompt_client_id,
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
            if session.get(Client, prompt_client_id) is None:
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
def delete_contract(collaborator):
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
            current = session.get(Contract, contract_id)
            if current is None:
                show_contract_error("Contrat introuvable.")
                return

            has_event = session.scalar(select(Event.id).where(Event.contract_id == contract_id).limit(1))
            if has_event is not None:
                show_contract_error("Impossible de supprimer un contrat associé à un événement.")
                return

            session.delete(current)
    except SQLAlchemyError:
        show_contract_error("Impossible de supprimer le contrat.")
        return

    show_contract_deletion_success()


@require_authenticated_collaborator(show_contract_error, roles=(Role.MANAGEMENT,))
def update_contract(collaborator):
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

    client_choice, total_choice, remaining_choice, status_choice = prompt_contract_modification(
        contract, clients
    )

    client_id = cast(int, contract.client_id)

    if client_choice:
        try:
            client_id = int(client_choice)
        except ValueError:
            show_contract_error("ID client invalide.")
            return

        if client_id <= 0:
            show_contract_error("ID client invalide.")
            return

        client_exists = False
        for client in clients:
            if cast(int, client.id) == client_id:
                client_exists = True
                break

        if not client_exists:
            show_contract_error("Client introuvable.")
            return

    try:
        total_amount = (
            Contract.parse_amount(total_choice) if total_choice else cast(Decimal, contract.total_amount)
        )
        remaining_amount = (
            Contract.parse_amount(remaining_choice)
            if remaining_choice
            else cast(Decimal, contract.remaining_amount)
        )
    except ValueError as error:
        show_contract_error(str(error))
        return

    if status_choice not in ("", "0", "1"):
        show_contract_error("Le statut est incorrect.")
        return

    is_signed = cast(bool, contract.is_signed) if status_choice == "" else status_choice == "1"

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

    try:
        with session_scope() as session:
            current = session.get(Contract, contract_id)
            if current is None:
                show_contract_error("Contrat introuvable.")
                return

            if client_id != cast(int, current.client_id):
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
                current.client_id,
                current.total_amount,
                current.remaining_amount,
                current.is_signed,
            ):
                show_contract_modification_unchanged()
                return

            setattr(current, "client_id", client_id)
            setattr(current, "total_amount", total_amount)
            setattr(current, "remaining_amount", remaining_amount)
            setattr(current, "is_signed", is_signed)
    except IntegrityError:
        show_contract_error("Impossible de modifier le contrat : données invalides.")
        return
    except SQLAlchemyError:
        show_contract_error("Impossible de modifier le contrat.")
        return

    show_contract_modification_success()
