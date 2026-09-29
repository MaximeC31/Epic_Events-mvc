from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import joinedload

from decorators import require_authenticated_collaborator
from models.client import Client
from models.collaborator import Collaborator, Role
from models.contract import Contract
from models.database import session_scope
from views.client_view import (
    prompt_client_creation,
    prompt_client_deletion_confirmation,
    prompt_client_id_for_deletion,
    prompt_client_id_for_modification,
    prompt_client_modification,
    show_client_creation_success,
    show_client_deletion_cancelled,
    show_client_deletion_success,
    show_client_error,
    show_client_modification_cancelled,
    show_client_modification_success,
    show_client_modification_unchanged,
    show_clients,
    show_empty_client_list,
)


@require_authenticated_collaborator(show_client_error)
def list_clients(authenticated_collaborator):
    try:
        with session_scope() as session:
            query = (
                select(Client)
                .options(joinedload(Client.sales_contact))
                .order_by(func.lower(Client.last_name), func.lower(Client.first_name))
            )
            clients = session.scalars(query).all()
            session.expunge_all()

    except SQLAlchemyError:
        show_client_error("Impossible de récupérer la liste des clients.")
        return

    if not clients:
        show_empty_client_list()
        return

    show_clients(clients)


@require_authenticated_collaborator(show_client_error, roles=(Role.SALES,))
def create_client(authenticated_collaborator):
    first_name, last_name, email, phone, company_name = prompt_client_creation()

    if not all((first_name, last_name, email, phone, company_name)):
        show_client_error("Tous les champs sont obligatoires.")
        return

    now = datetime.now()

    client = Client(
        first_name=first_name.strip(),
        last_name=last_name.strip(),
        email=email.strip().lower(),
        phone=phone.strip(),
        company_name=company_name.strip(),
        created_at=now,
        last_contact_at=now,
        sales_contact_id=authenticated_collaborator.id,
    )

    validation_error = client.validation_error()
    if validation_error:
        show_client_error(validation_error)
        return

    try:
        with session_scope() as session:
            session.add(client)
    except IntegrityError:
        show_client_error("Impossible de créer le client : données invalides.")
        return
    except SQLAlchemyError:
        show_client_error("Impossible de créer le client.")
        return

    show_client_creation_success()


@require_authenticated_collaborator(show_client_error, roles=(Role.SALES,))
def delete_client(authenticated_collaborator):
    try:
        client_id = int(prompt_client_id_for_deletion())
        if client_id == 0:
            show_client_deletion_cancelled()
            return
    except ValueError:
        show_client_error("ID invalide.")
        return

    try:
        with session_scope() as session:
            client = session.get(Client, client_id)
            if client is None or client.sales_contact_id != authenticated_collaborator.id:
                show_client_error("Client introuvable ou non attribué.")
                return
            session.expunge(client)
    except SQLAlchemyError:
        show_client_error("Impossible de récupérer le client.")
        return

    if not prompt_client_deletion_confirmation(client):
        show_client_deletion_cancelled()
        return

    try:
        with session_scope() as session:
            current = session.get(Client, client_id)
            if current is None or current.sales_contact_id != authenticated_collaborator.id:
                show_client_error("Client introuvable ou non attribué.")
                return

            has_contract = session.scalar(select(Contract.id).where(Contract.client_id == client_id).limit(1))
            if has_contract is not None:
                show_client_error("Impossible de supprimer un client associé à un contrat.")
                return

            session.delete(current)
    except SQLAlchemyError:
        show_client_error("Impossible de supprimer le client.")
        return

    show_client_deletion_success()


@require_authenticated_collaborator(show_client_error, roles=(Role.SALES,))
def update_client(authenticated_collaborator):
    try:
        client_id = int(prompt_client_id_for_modification())
        if client_id == 0:
            show_client_modification_cancelled()
            return
    except ValueError:
        show_client_error("ID invalide.")
        return

    try:
        with session_scope() as session:
            client = session.get(Client, client_id)

            if client is None or client.sales_contact_id != authenticated_collaborator.id:
                show_client_error("Client introuvable ou non attribué.")
                return

            session.expunge(client)

    except SQLAlchemyError:
        show_client_error("Impossible de récupérer le client.")
        return

    first_name, last_name, email, phone, company_name = prompt_client_modification(client)
    first_name = client.first_name if first_name == "" else first_name
    last_name = client.last_name if last_name == "" else last_name
    email = client.email if email == "" else email.lower()
    phone = client.phone if phone == "" else phone
    company_name = client.company_name if company_name == "" else company_name

    updated = Client(
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone,
        company_name=company_name,
    )

    validation_error = updated.validation_error()
    if validation_error:
        show_client_error(validation_error)
        return

    try:
        with session_scope() as session:
            current = session.get(Client, client_id)
            if current is None or current.sales_contact_id != authenticated_collaborator.id:
                show_client_error("Client introuvable ou non attribué.")
                return

            if (first_name, last_name, email, phone, company_name) == (
                current.first_name,
                current.last_name,
                current.email,
                current.phone,
                current.company_name,
            ):
                show_client_modification_unchanged()
                return

            setattr(current, "first_name", first_name)
            setattr(current, "last_name", last_name)
            setattr(current, "email", email)
            setattr(current, "phone", phone)
            setattr(current, "company_name", company_name)
            setattr(current, "last_contact_at", datetime.now())

    except IntegrityError:
        show_client_error("Impossible de modifier le client : données invalides.")
        return
    except SQLAlchemyError:
        show_client_error("Impossible de modifier le client.")
        return

    show_client_modification_success()
