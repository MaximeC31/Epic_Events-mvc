import sys

from controllers.login_controller import run_login
from views.main_view import show_main_menu


def run():
    choice = show_main_menu()

    match choice:
        case "1":
            run_login()
        case "2":
            print("Fermeture de l'application")
            sys.exit(0)
        case _:
            print("Choix invalide")
            sys.exit(1)
