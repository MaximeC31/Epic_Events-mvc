import sys

from sqlalchemy import select

from controllers.login_controller import run_login
from controllers.setup_controller import run_setup
from models.collaborator import Collaborator
from models.database import session_scope
from models.schema import initialize_schema
from views.main_view import show_main_menu


def run():
    initialize_schema()

    with session_scope() as session:
        stmt = select(Collaborator).limit(1)
        is_configured = session.scalar(stmt) is not None

    if not is_configured and not run_setup():
        return

    choice = show_main_menu()

    match choice:
        case "1":
            collaborator = run_login()
            if collaborator is None:
                return
            return collaborator

        case "2":
            print("Fermeture de l'application")
            sys.exit(0)

        case _:
            print("Choix invalide")
            sys.exit(1)
