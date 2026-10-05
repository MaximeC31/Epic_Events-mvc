from getpass import getpass

from models.collaborator import Role


def show_collaborators(collaborators):
    if not collaborators:
        print("\nAucun collaborateur à afficher")
        return

    print("\n=== Collaborateurs ===")
    for collaborator in collaborators:
        print(
            f"ID {collaborator.id} - {collaborator.first_name} {collaborator.last_name} "
            f"- {collaborator.email} - {collaborator.role.value} "
            f"- {'actif' if collaborator.is_active else 'inactif'}"
        )


def prompt_collaborator_creation():
    print("\n=== Création d'un collaborateur ===")
    first_name = input("Prénom : ").strip()
    last_name = input("Nom : ").strip()
    email = input("Email : ").strip()
    password = getpass("Mot de passe : ")
    password_confirmation = getpass("Confirmez le mot de passe : ")

    roles = list(Role)
    print("Rôles disponibles :")
    for role_number, role in enumerate(roles, start=1):
        print(f"{role_number}. {role.value}")
    role_choice = input("Insérez le numéro du rôle : ").strip()

    return first_name, last_name, email, password, password_confirmation, role_choice


def show_collaborator_creation_success():
    print("\nCollaborateur créé avec succès")


def prompt_collaborator_id_for_deletion():
    print("\n=== Choix du collaborateur à supprimer ===")
    return input("ID du collaborateur (0 = annuler) : ").strip()


def prompt_collaborator_deletion_confirmation(collaborator):
    print("\n=== Suppression d'un collaborateur ===")
    print(f"ID : {collaborator.id}")
    print(f"Identité : {collaborator.first_name} {collaborator.last_name}")
    print(f"Email : {collaborator.email}")
    print(f"Rôle : {collaborator.role.value}")
    print(f"Statut : {'actif' if collaborator.is_active else 'inactif'}")
    return input("Tapez oui pour confirmer : ").strip() == "oui"


def show_collaborator_deletion_cancelled():
    print("\nAnnulation de la suppression")


def show_collaborator_deletion_success():
    print("\nCollaborateur supprimé avec succès")


def prompt_collaborator_id_for_modification():
    print("\n=== Choix du collaborateur à modifier ===")
    return input("ID du collaborateur (0 = annuler) : ").strip()


def prompt_collaborator_modification(is_self_update, collaborator):
    print("\n=== Modification du collaborateur ===")
    print(f"ID : {collaborator.id}")
    print(f"Identité : {collaborator.first_name} {collaborator.last_name}")
    print(f"Email : {collaborator.email}")
    print(f"Rôle : {collaborator.role.value}")
    print(f"Statut : {'actif' if collaborator.is_active else 'inactif'}")

    print("Valeur vide = conserver la valeur actuelle.")
    first_name_input = input("Prénom : ").strip()
    last_name_input = input("Nom : ").strip()
    email_input = input("Email : ").strip()

    if not is_self_update:
        roles = list(Role)
        print("Rôles disponibles :")
        for role_number, role in enumerate(roles, start=1):
            print(f"{role_number}. {role.value}")
        role_choice = input("Insérez le numéro du rôle : ").strip()

        status_choice = input("Insérez le statut (0 = inactif, 1 = actif) : ").strip()
    else:
        role_choice = ""
        status_choice = ""

    return first_name_input, last_name_input, email_input, role_choice, status_choice


def show_collaborator_modification_cancelled():
    print("\nAnnulation de la modification")


def show_collaborator_modification_unchanged():
    print("\nAucune modification effectuée")


def show_collaborator_modification_success():
    print("\nCollaborateur modifié avec succès")


def show_collaborator_error(message):
    print(f"\nErreur : {message}")
