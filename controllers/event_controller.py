from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload

from decorators import require_authenticated_collaborator

from models.contract import Contract
from models.database import session_scope
from models.event import Event

from views.event_view import show_empty_event_list, show_event_error, show_event_list


@require_authenticated_collaborator(show_event_error)
def list_all_events(collaborator):
    try:
        with session_scope() as session:
            all_events = (
                session.query(Event)
                .options(
                    joinedload(Event.contract).joinedload(Contract.client),
                    joinedload(Event.support),
                )
                .order_by(Event.start_datetime.asc(), Event.id.asc())
                .all()
            )
            session.expunge_all()

    except SQLAlchemyError:
        show_event_error("Une erreur est survenue lors de la consultation des événements.")
        return

    if not all_events:
        show_empty_event_list()
        return

    show_event_list(all_events)
