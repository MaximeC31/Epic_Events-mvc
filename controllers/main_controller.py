import sys

from controllers.login_controller import run_login
from controllers.setup_controller import ensure_setup
from controllers.client_controller import list_all_clients
from models.schema import initialize_schema
from views.main_view import show_authenticated_menu, show_main_menu, show_main_message


def run():
    initialize_schema()

    if not ensure_setup():
        sys.exit(1)

    while True:
        choice = show_main_menu()

        match choice:
            case "1":
                collaborator = run_login()
                if collaborator is None:
                    continue

                run_authenticated_menu(collaborator)

            case "2":
                show_main_message("Fermeture de l'application")
                sys.exit(0)

            case _:
                show_main_message("Choix invalide")


def run_authenticated_menu(collaborator):
    while True:
        choice = show_authenticated_menu(collaborator)

        match choice:
            case "1":
                list_all_clients(collaborator)
            case "2":
                show_main_message("Déconnexion réussie")
                return
            case _:
                show_main_message("Choix invalide")
