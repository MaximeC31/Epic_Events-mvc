from getpass import getpass


def show_login_form():
    print("\n=== Connexion ===")
    email = input("Email : ").strip()
    password = getpass("Mot de passe : ")

    return email, password


def show_login_error(message):
    print(f"Erreur : {message}")
