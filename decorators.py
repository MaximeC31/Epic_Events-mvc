from functools import wraps

from sqlalchemy.exc import SQLAlchemyError

from models.collaborator import Collaborator, Role
from models.database import session_scope


def require_authenticated_collaborator(
    error_handler,
    roles=None,
):
    def decorator(function):
        @wraps(function)
        def wrapper(authenticated_collaborator):
            if authenticated_collaborator is None:
                error_handler("Veuillez vous connecter.")
                return

            try:
                with session_scope() as session:
                    collaborator = session.get(Collaborator, authenticated_collaborator.id)
                    if (
                        collaborator is None
                        or not collaborator.is_active
                        or not isinstance(collaborator.role, Role)
                        or (roles is not None and collaborator.role not in roles)
                    ):
                        error_handler("Accès refusé. Veuillez vous reconnecter.")
                        return

                    session.expunge(collaborator)
            except SQLAlchemyError:
                error_handler("Impossible de vérifier vos permissions.")
                return

            return function(collaborator)

        return wrapper

    return decorator
