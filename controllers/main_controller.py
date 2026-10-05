import sys

import sentry_sdk
from sqlalchemy.exc import SQLAlchemyError

from controllers.collaborator_controller import (
    create_collaborator,
    delete_collaborator,
    list_collaborators,
    update_collaborator,
)
from controllers.client_controller import create_client, delete_client, list_clients, update_client
from controllers.contract_controller import (
    create_contract,
    delete_contract,
    list_contracts,
    list_filtered_sales_contracts,
    update_contract,
    update_sales_contract,
)
from controllers.event_controller import (
    assign_event_support,
    create_event,
    delete_event,
    list_assigned_support_events,
    list_events,
    list_events_without_support,
    update_support_event,
)
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
from views.setup_view import show_setup_error


def run():
    try:
        initialize_schema()
    except SQLAlchemyError as error:
        sentry_sdk.capture_exception(error)
        show_setup_error("Impossible d'initialiser la base de données.")
        sys.exit(1)

    if not ensure_setup():
        sys.exit(1)

    while True:
        choice = prompt_main_menu()

        match choice:
            case "0":
                show_main_message("Fermeture de l'application")
                sys.exit(0)

            case "1":
                authenticated_collaborator = run_login()
                if authenticated_collaborator is None:
                    continue

                run_authenticated_menu(authenticated_collaborator)

            case _:
                show_main_message("Choix invalide")


def run_authenticated_menu(authenticated_collaborator):
    while True:
        choice = prompt_authenticated_menu(authenticated_collaborator)

        match authenticated_collaborator.role, choice:
            case _, "0":
                show_main_message("Déconnexion réussie")
                break

            case _, "1":
                run_client_menu(authenticated_collaborator)

            case _, "2":
                run_contract_menu(authenticated_collaborator)

            case _, "3":
                run_event_menu(authenticated_collaborator)

            case Role.MANAGEMENT, "4":
                run_collaborator_menu(authenticated_collaborator)

            case _:
                show_main_message("Choix invalide")


def run_client_menu(authenticated_collaborator):
    while True:
        choice = prompt_client_menu(authenticated_collaborator)

        match authenticated_collaborator.role, choice:
            case _, "0":
                break
            case _, "1":
                list_clients(authenticated_collaborator)
            case Role.SALES, "2":
                create_client(authenticated_collaborator)
            case Role.SALES, "3":
                update_client(authenticated_collaborator)
            case Role.SALES, "4":
                delete_client(authenticated_collaborator)
            case _:
                show_main_message("Choix invalide")


def run_contract_menu(authenticated_collaborator):
    while True:
        choice = prompt_contract_menu(authenticated_collaborator)

        match authenticated_collaborator.role, choice:
            case _, "0":
                break
            case _, "1":
                list_contracts(authenticated_collaborator)
            case Role.MANAGEMENT, "2":
                create_contract(authenticated_collaborator)
            case Role.MANAGEMENT, "3":
                update_contract(authenticated_collaborator)
            case Role.MANAGEMENT, "4":
                delete_contract(authenticated_collaborator)
            case Role.SALES, "3":
                update_sales_contract(authenticated_collaborator)
            case Role.SALES, "5":
                list_filtered_sales_contracts(authenticated_collaborator)
            case _:
                show_main_message("Choix invalide")


def run_event_menu(authenticated_collaborator):
    while True:
        choice = prompt_event_menu(authenticated_collaborator)

        match authenticated_collaborator.role, choice:
            case _, "0":
                break
            case _, "1":
                list_events(authenticated_collaborator)
            case Role.SALES, "2":
                create_event(authenticated_collaborator)
            case Role.MANAGEMENT, "3":
                assign_event_support(authenticated_collaborator)
            case Role.MANAGEMENT, "4":
                delete_event(authenticated_collaborator)
            case Role.MANAGEMENT, "5":
                list_events_without_support(authenticated_collaborator)
            case Role.SUPPORT, "3":
                update_support_event(authenticated_collaborator)
            case Role.SUPPORT, "5":
                list_assigned_support_events(authenticated_collaborator)
            case _:
                show_main_message("Choix invalide")


def run_collaborator_menu(authenticated_collaborator):
    while True:
        choice = prompt_collaborator_menu(authenticated_collaborator)

        match authenticated_collaborator.role, choice:
            case _, "0":
                break
            case Role.MANAGEMENT, "1":
                list_collaborators(authenticated_collaborator)
            case Role.MANAGEMENT, "2":
                create_collaborator(authenticated_collaborator)
            case Role.MANAGEMENT, "3":
                update_collaborator(authenticated_collaborator)
            case Role.MANAGEMENT, "4":
                delete_collaborator(authenticated_collaborator)
            case _:
                show_main_message("Choix invalide")
