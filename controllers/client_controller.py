from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload

from decorators import require_authenticated_collaborator

from models.client import Client
from models.database import session_scope

from views.client_view import (
    show_client_error,
    show_clients,
    show_empty_client_list,
)


@require_authenticated_collaborator(show_client_error)
def list_all_clients(collaborator):
    try:
        with session_scope() as session:
            query = (
                select(Client)
                .options(joinedload(Client.sales_contact))
                .order_by(func.lower(Client.last_name), func.lower(Client.first_name))
            )
            all_clients = session.scalars(query).all()

            session.expunge_all()

    except SQLAlchemyError:
        show_client_error("Impossible de récupérer la liste des clients.")
        return

    if not all_clients:
        show_empty_client_list()
        return

    show_clients(all_clients)
