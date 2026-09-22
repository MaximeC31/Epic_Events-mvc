from models.collaborator import Role


def show_main_menu():
    print("\n=== Epic Events ===")
    print("1. Se connecter")
    print("2. Quitter")

    return input("Veuillez saisir votre choix : ").strip()


def show_authenticated_menu(collaborator):
    print(f"\n=== {collaborator.first_name} {collaborator.last_name} ({collaborator.role.value}) ===")
    print("1. Voir tous les clients")
    print("2. Voir tous les contrats")
    print("3. Voir tous les événements")

    if collaborator.role is Role.MANAGEMENT:
        print("4. Créer un collaborateur")
        print("5. Se déconnecter")
    else:
        print("4. Se déconnecter")

    return input("Veuillez saisir votre choix : ").strip()


def show_main_message(message):
    print(message)
