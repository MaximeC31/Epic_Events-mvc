from getpass import getpass

from models.collaborator import Role


def prompt_collaborator_creation():
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


def prompt_collaborator_id_for_deletion(collaborators):
    if not collaborators:
        print("Aucun collaborateur à afficher")
        return "0"

    for collaborator in collaborators:
        print(f"ID {collaborator.id} - {collaborator.first_name} {collaborator.last_name}")
    return input("ID du collaborateur (0 = annuler) : ").strip()


def prompt_collaborator_deletion_confirmation(collaborator):
    print("\n=== Suppression d'un collaborateur ===")
    print(f"Id : {collaborator.id}")
    print(f"Identité : {collaborator.first_name} {collaborator.last_name}")
    print(f"Email : {collaborator.email}")
    print(f"Rôle : {collaborator.role.value}")
    print(f"Statut : {'actif' if collaborator.is_active else 'inactif'}")
    return input("Tapez oui pour confirmer : ").strip() == "oui"


def show_collaborator_deletion_cancelled():
    print("Annulation de la suppression")


def show_collaborator_deletion_success():
    print("Collaborateur supprimé avec succès")


def prompt_collaborator_id_for_modification(collaborators):
    if not collaborators:
        print("Aucun collaborateur à afficher")
        return "0"

    for collaborator in collaborators:
        print(f"ID {collaborator.id} - {collaborator.first_name} {collaborator.last_name}")
    return input("ID du collaborateur (0 = annuler) : ").strip()


def prompt_collaborator_modification(is_self_update, collaborator):
    print("\n=== Modification du collaborateur ===")
    print(f"Id : {collaborator.id}")
    print(f"Identité : {collaborator.first_name} {collaborator.last_name}")
    print(f"Email : {collaborator.email}")
    print(f"Rôle : {collaborator.role.value}")
    print(f"Statut : {'actif' if collaborator.is_active else 'inactif'}")

    print("Valeur vide indique conserver la valeur actuelle")
    first_name = input("Prénom : ").strip()
    last_name = input("Nom : ").strip()
    email = input("Email : ").strip()

    if not is_self_update:
        roles = list(Role)
        print("Rôles disponibles :")
        for i, role in enumerate(roles, start=1):
            print(f"{i}. {role.value}")
        role_choice = input("Insérez le numéro du rôle : ").strip()

        is_active = input("Insérez le statut (0 = inactif, 1 = actif) : ").strip()
    else:
        role_choice = ""
        is_active = ""

    return first_name, last_name, email, role_choice, is_active


def show_collaborator_modification_cancelled():
    print("Annulation de la modification")


def show_collaborator_modification_unchanged():
    print("Aucune modification effectuée")


def show_collaborator_modification_success():
    print("Collaborateur modifié avec succès")


def show_collaborator_error(message):
    print(f"Erreur : {message}")
