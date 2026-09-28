from functools import wraps

from models.collaborator import Role


def require_authenticated_collaborator(
    error_handler,
    roles=None,
):
    def decorator(function):
        @wraps(function)
        def wrapper(collaborator):
            if (
                not collaborator
                or not collaborator.is_active
                or not isinstance(collaborator.role, Role)
                or (roles is not None and collaborator.role not in roles)
            ):
                error_handler("Vous n'avez pas la permission de consulter cet élément")
                return

            return function(collaborator)

        return wrapper

    return decorator
