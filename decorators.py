from functools import wraps

from models.collaborator import Role


def require_authenticated_collaborator(error_handler):
    def decorator(function):
        @wraps(function)
        def wrapper(collaborator):
            if not collaborator or not collaborator.is_active or not isinstance(collaborator.role, Role):
                error_handler("Vous n'avez pas la permission de consulter cet élément")
                return

            return function(collaborator)

        return wrapper

    return decorator
