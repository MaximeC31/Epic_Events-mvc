import sys

from controllers.collaborator_controller import (
    create_collaborator,
    delete_collaborator,
    list_collaborators,
    update_collaborator,
)
from controllers.client_controller import list_all_clients
from controllers.contract_controller import list_all_contracts
from controllers.event_controller import list_all_events
from controllers.login_controller import run_login
from controllers.setup_controller import ensure_setup
from models.collaborator import Role
from models.schema import initialize_schema
from views.main_view import (
    prompt_authenticated_menu,
    prompt_client_menu,
    prompt_collaborator_menu,
    prompt_contract_menu,
    prompt_event_menu,
    prompt_main_menu,
    show_main_message,
)


def run():
    initialize_schema()

    if not ensure_setup():
        sys.exit(1)

    while True:
        choice = prompt_main_menu()

        match choice:
            case "0":
                show_main_message("Fermeture de l'application")
                sys.exit(0)

            case "1":
                collaborator = run_login()
                if collaborator is None:
                    continue

                run_authenticated_menu(collaborator)

            case _:
                show_main_message("Choix invalide")


def run_authenticated_menu(collaborator):
    while True:
        choice = prompt_authenticated_menu(collaborator)

        match collaborator.role, choice:
            case _, "0":
                show_main_message("Déconnexion réussie")
                break

            case _, "1":
                run_client_menu(collaborator)

            case _, "2":
                run_contract_menu(collaborator)

            case _, "3":
                run_event_menu(collaborator)

            case Role.MANAGEMENT, "4":
                run_collaborator_menu(collaborator)

            case _:
                show_main_message("Choix invalide")


def run_client_menu(collaborator):
    while True:
        choice = prompt_client_menu(collaborator)

        match collaborator.role, choice:
            case _, "0":
                break
            case _, "1":
                list_all_clients(collaborator)
            case Role.SALES, "2":
                pass
            case Role.SALES, "3":
                pass
            case Role.SALES, "4":
                pass
            case _:
                show_main_message("Choix invalide")


def run_contract_menu(collaborator):
    while True:
        choice = prompt_contract_menu(collaborator)

        match collaborator.role, choice:
            case _, "0":
                break
            case _, "1":
                list_all_contracts(collaborator)
            case Role.MANAGEMENT, "2":
                pass
            case Role.MANAGEMENT, "3":
                pass
            case Role.MANAGEMENT, "4":
                pass
            case Role.SALES, "3":
                pass
            case Role.SALES, "5":
                pass
            case _:
                show_main_message("Choix invalide")


def run_event_menu(collaborator):
    while True:
        choice = prompt_event_menu(collaborator)

        match collaborator.role, choice:
            case _, "0":
                break
            case _, "1":
                list_all_events(collaborator)
            case Role.SALES, "2":
                pass
            case Role.MANAGEMENT, "3":
                pass
            case Role.MANAGEMENT, "4":
                pass
            case Role.MANAGEMENT, "5":
                pass
            case Role.SUPPORT, "3":
                pass
            case Role.SUPPORT, "5":
                pass
            case _:
                show_main_message("Choix invalide")


def run_collaborator_menu(collaborator):
    while True:
        choice = prompt_collaborator_menu(collaborator)

        match collaborator.role, choice:
            case _, "0":
                break
            case Role.MANAGEMENT, "1":
                list_collaborators(collaborator)
            case Role.MANAGEMENT, "2":
                create_collaborator(collaborator)
            case Role.MANAGEMENT, "3":
                update_collaborator(collaborator)
            case Role.MANAGEMENT, "4":
                delete_collaborator(collaborator)
            case _:
                show_main_message("Choix invalide")
