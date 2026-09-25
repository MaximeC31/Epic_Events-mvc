import sys

from controllers.collaborator_controller import create_collaborator, delete_collaborator, update_collaborateur
from controllers.client_controller import list_all_clients
from controllers.contract_controller import list_all_contracts
from controllers.event_controller import list_all_events
from controllers.login_controller import run_login
from controllers.setup_controller import ensure_setup

from models.collaborator import Role
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

        match collaborator.role:
            case Role.MANAGEMENT:
                match choice:
                    case "1":
                        list_all_clients(collaborator)
                    case "2":
                        list_all_contracts(collaborator)
                    case "3":
                        list_all_events(collaborator)
                    case "4":
                        create_collaborator(collaborator)
                    case "5":
                        delete_collaborator(collaborator)
                    case "6":
                        update_collaborateur(collaborator)
                    case "7":
                        show_main_message("Déconnexion réussie")
                        break
                    case _:
                        show_main_message("Choix invalide")
            case Role.SALES:
                match choice:
                    case "1":
                        list_all_clients(collaborator)
                    case "2":
                        list_all_contracts(collaborator)
                    case "3":
                        list_all_events(collaborator)
                    case "4":
                        show_main_message("Déconnexion réussie")
                        break
                    case _:
                        show_main_message("Choix invalide")
            case Role.SUPPORT:
                match choice:
                    case "1":
                        list_all_clients(collaborator)
                    case "2":
                        list_all_contracts(collaborator)
                    case "3":
                        list_all_events(collaborator)
                    case "4":
                        show_main_message("Déconnexion réussie")
                        break
                    case _:
                        show_main_message("Choix invalide")
            case _:
                show_main_message("Rôle inconnu")
