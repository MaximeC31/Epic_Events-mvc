from getpass import getpass


def show_setup_form():
    print("\n=== Première configuration ===")
    first_name = input("Prénom : ").strip()
    last_name = input("Nom : ").strip()
    email = input("Email : ").strip()
    password = getpass("Mot de passe : ")
    password_confirmation = getpass("Confirmez le mot de passe : ")

    return first_name, last_name, email, password, password_confirmation


def show_setup_success():
    print("Compte gestion créé avec succès")


def show_setup_error(message):
    print(f"Erreur : {message}")
