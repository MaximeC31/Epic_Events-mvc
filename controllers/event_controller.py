from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload

from models.collaborator import Role
from models.contract import Contract
from models.database import session_scope
from models.event import Event

from views.event_view import show_empty_event_list, show_event_error, show_event_list


def list_all_events(collaborator):
    if not collaborator or not collaborator.is_active or not isinstance(collaborator.role, Role):
        show_event_error("Vous n'avez pas la permission de consulter les événements.")
        return

    try:
        with session_scope() as session:
            events = (
                session.query(Event)
                .options(
                    joinedload(Event.contract).joinedload(Contract.client),
                    joinedload(Event.support),
                )
                .order_by(Event.start_datetime.asc(), Event.id.asc())
                .all()
            )

            display_data = [
                {
                    "id": event.id,
                    "contract_id": event.contract_id,
                    "client_name": f"{event.contract.client.first_name} {event.contract.client.last_name}",
                    "client_contact": (
                        f"{event.contract.client.email} / {event.contract.client.phone}"
                    ),
                    "start_time": event.start_datetime,
                    "end_time": event.end_datetime,
                    "support_responsible": (
                        f"{event.support.first_name} {event.support.last_name}" if event.support else None
                    ),
                    "location": event.location,
                    "participant_count": event.number_of_participants,
                    "notes": event.notes,
                }
                for event in events
            ]

    except SQLAlchemyError:
        show_event_error("Une erreur est survenue lors de la consultation des événements.")
        return

    if not display_data:
        show_empty_event_list()
        return

    show_event_list(display_data)
