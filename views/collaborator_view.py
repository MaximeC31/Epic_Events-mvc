from getpass import getpass

from models.collaborator import Role


def show_create_collaborator_form():
    print("\n=== Création d'un collaborateur ===")
    first_name = input("Prénom : ").strip()
    last_name = input("Nom : ").strip()
    email = input("Email : ").strip()
    password = getpass("Mot de passe : ")
    password_confirmation = getpass("Confirmez le mot de passe : ")

    roles = list(Role)
    print("Rôles disponibles :")
    for i, role in enumerate(roles, start=1):
        print(f"{i}. {role.value}")
    role_choice = input("Insérez le numéro du rôle : ").strip()

    return first_name, last_name, email, password, password_confirmation, role_choice


def show_collaborator_creation_success():
    print("Collaborateur créé avec succès")


def show_collaborator_creation_error(message):
    print(f"Erreur : {message}")
