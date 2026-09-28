from models.collaborator import Role


def prompt_main_menu():
    print("\n=== Epic Events ===")
    print("0. Quitter")
    print("1. Se connecter")

    return input("Veuillez saisir votre choix : ").strip()


def prompt_authenticated_menu(collaborator):
    print(f"\n=== {collaborator.first_name} {collaborator.last_name} ({collaborator.role.value}) ===")
    print("0. Se déconnecter")
    print("1. Clients")
    print("2. Contrats")
    print("3. Événements")
    if collaborator.role == Role.MANAGEMENT:
        print("4. Collaborateurs")

    return input("Veuillez saisir votre choix : ").strip()


def prompt_client_menu(collaborator):
    print("\n=== Clients ===")
    print("0. Retour")
    print("1. Voir tous les clients")
    if collaborator.role == Role.SALES:
        print("2. Créer un client")
        print("3. Modifier mes clients")
        print("4. Supprimer un de mes clients")

    return input("Veuillez saisir votre choix : ").strip()


def prompt_contract_menu(collaborator):
    print("\n=== Contrats ===")
    print("0. Retour")
    print("1. Voir tous les contrats")
    if collaborator.role == Role.MANAGEMENT:
        print("2. Créer un contrat")
        print("3. Modifier un contrat")
        print("4. Supprimer un contrat")
    if collaborator.role == Role.SALES:
        print("3. Modifier les contrats de mes clients")
        print("5. Voir les contrats non signés ou non entièrement payés")

    return input("Veuillez saisir votre choix : ").strip()


def prompt_event_menu(collaborator):
    print("\n=== Événements ===")
    print("0. Retour")
    print("1. Voir tous les événements")
    if collaborator.role == Role.SALES:
        print("2. Créer un événement pour un client avec contrat signé")
    if collaborator.role == Role.MANAGEMENT:
        print("3. Affecter un support à un événement")
        print("4. Supprimer un événement")
        print("5. Voir les événements sans support")
    if collaborator.role == Role.SUPPORT:
        print("3. Modifier mes événements attribués")
        print("5. Voir mes événements attribués")

    return input("Veuillez saisir votre choix : ").strip()


def prompt_collaborator_menu(collaborator):
    if collaborator.role == Role.MANAGEMENT:
        print("\n=== Collaborateurs ===")
        print("0. Retour")
        print("1. Voir les collaborateurs")
        print("2. Créer un collaborateur")
        print("3. Modifier un collaborateur")
        print("4. Supprimer un collaborateur")

    return input("Veuillez saisir votre choix : ").strip()


def show_main_message(message):
    print(f"\n{message}")
