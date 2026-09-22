from getpass import getpass


def show_create_collaborator_form():
    print("\n=== Création d'un collaborateur ===")
    first_name = input("Prénom : ").strip()
    last_name = input("Nom : ").strip()
    email = input("Email : ").strip()
    password = getpass("Mot de passe : ")
    password_confirmation = getpass("Confirmez le mot de passe : ")

    print("\nSélectionnez un rôle :")
    print("1. Gestion")
    print("2. Commercial")
    print("3. Support")
    role_choice = input("Choix du rôle (1-3) : ").strip()

    return first_name, last_name, email, password, password_confirmation, role_choice


def show_collaborator_creation_success():
    print("Collaborateur créé avec succès")


def show_collaborator_creation_error(message):
    print(f"Erreur : {message}")
