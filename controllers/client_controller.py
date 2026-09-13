from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload

from models.client import Client
from models.collaborator import Role
from models.database import session_scope
from views.client_view import (
    show_client_error,
    show_clients,
    show_empty_client_list,
)


def list_all_clients(collaborator):
    if not collaborator or not collaborator.is_active or not isinstance(collaborator.role, Role):
        show_client_error("Vous n'avez pas la permission de consulter les clients")
        return

    try:
        with session_scope() as session:
            query = (
                select(Client)
                .options(joinedload(Client.sales_contact))
                .order_by(func.lower(Client.last_name), func.lower(Client.first_name))
            )
            all_clients = session.scalars(query).all()

            display_data = [
                {
                    "first_name": client.first_name,
                    "last_name": client.last_name,
                    "email": client.email,
                    "phone": client.phone,
                    "company": client.company_name,
                    "created_at": client.created_at,
                    "last_contact_at": client.last_contact_at,
                    "salesperson_name": (
                        f"{client.sales_contact.first_name} {client.sales_contact.last_name}"
                    ),
                }
                for client in all_clients
            ]

    except SQLAlchemyError:
        show_client_error("Impossible de récupérer la liste des clients.")
        return

    if not display_data:
        show_empty_client_list()
        return

    show_clients(display_data)
