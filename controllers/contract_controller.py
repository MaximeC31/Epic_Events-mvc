from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload

from models.client import Client
from models.collaborator import Role
from models.contract import Contract
from models.database import session_scope

from views.contract_view import (
    show_contract_error,
    show_contracts,
    show_empty_contract_list,
)


def list_all_contracts(collaborator):
    if (
        not collaborator
        or not collaborator.is_active
        or not isinstance(collaborator.role, Role)
    ):
        show_contract_error("Vous n'avez pas la permission de consulter les contrats.")
        return

    try:
        with session_scope() as session:
            contracts = (
                session.query(Contract)
                .options(selectinload(Contract.client).selectinload(Client.sales_contact))
                .order_by(Contract.created_at.desc(), Contract.id.desc())
                .all()
            )

            display_data = [
                {
                    "id": contract.id,
                    "client_name": f"{contract.client.first_name} {contract.client.last_name}",
                    "company": contract.client.company_name,
                    "salesperson_name": f"{contract.client.sales_contact.first_name} {contract.client.sales_contact.last_name}",
                    "total_amount": contract.total_amount,
                    "remaining_amount": contract.remaining_amount,
                    "created_at": contract.created_at,
                    "is_signed": contract.is_signed,
                }
                for contract in contracts
            ]

    except SQLAlchemyError:
        show_contract_error("Impossible de récupérer la liste des contrats.")
        return

    if not display_data:
        show_empty_contract_list()
        return

    show_contracts(display_data)
