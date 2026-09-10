from getpass import getpass


def show_login_form():
    print("\n=== Connexion ===")
    email = input("Email : ").strip()
    password = getpass("Mot de passe : ")

    return email, password
