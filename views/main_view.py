from models.collaborator import Role


def show_main_menu():
    print("\n=== Epic Events ===")
    print("1. Se connecter")
    print("2. Quitter")

    return input("Veuillez saisir votre choix : ").strip()


def show_authenticated_menu(collaborator):
    print(f"\n=== {collaborator.first_name} {collaborator.last_name} ({collaborator.role.value}) ===")

    match (collaborator.role):
        case Role.MANAGEMENT:
            print("1. Voir tous les clients")
            print("2. Voir tous les contrats")
            print("3. Voir tous les événements")
            print("4. Créer un collaborateur")
            print("5. Supprimer un collaborateur")
            print("6. Se déconnecter")
        case Role.SALES:
            print("1. Voir tous les clients")
            print("2. Voir tous les contrats")
            print("3. Voir tous les événements")
            print("4. Se déconnecter")
        case Role.SUPPORT:
            print("1. Voir tous les clients")
            print("2. Voir tous les contrats")
            print("3. Voir tous les événements")
            print("4. Se déconnecter")
        case _:
            pass

    return input("Veuillez saisir votre choix : ").strip()


def show_main_message(message):
    print(message)
