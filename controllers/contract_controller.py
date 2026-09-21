from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload

from decorators import require_authenticated_collaborator

from models.client import Client
from models.contract import Contract
from models.database import session_scope

from views.contract_view import (
    show_contract_error,
    show_contracts,
    show_empty_contract_list,
)


@require_authenticated_collaborator(show_contract_error)
def list_all_contracts(collaborator):
    try:
        with session_scope() as session:
            all_contracts = (
                session.query(Contract)
                .options(selectinload(Contract.client).selectinload(Client.sales_contact))
                .order_by(Contract.created_at.desc(), Contract.id.desc())
                .all()
            )
            session.expunge_all()

    except SQLAlchemyError:
        show_contract_error("Impossible de récupérer la liste des contrats.")
        return

    if not all_contracts:
        show_empty_contract_list()
        return

    show_contracts(all_contracts)
