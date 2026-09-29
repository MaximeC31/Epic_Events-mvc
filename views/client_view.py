def prompt_client_creation():
    print("\n=== Création d'un client ===")
    first_name = input("Prénom : ").strip()
    last_name = input("Nom : ").strip()
    email = input("Email : ").strip()
    phone = input("Téléphone : ").strip()
    company_name = input("Entreprise : ").strip()

    return first_name, last_name, email, phone, company_name


def show_client_creation_success():
    print("\nClient créé avec succès")


def show_clients(clients):
    print("\nTous les clients :")
    for client in clients:
        salesperson = client.sales_contact

        print(f"\nID: {client.id}, Prénom: {client.first_name}, Nom: {client.last_name}")
        print(f"Email: {client.email}, Téléphone: {client.phone}, " f"Entreprise: {client.company_name}")
        print(f"Créé le: {client.created_at}, Dernier contact: {client.last_contact_at}")
        print(f"Commercial associé: {salesperson.first_name} {salesperson.last_name}")
        print("-")


def show_empty_client_list():
    print("\nAucun client n'est enregistré.")


def show_client_error(message):
    print(f"\nErreur : {message}")


def prompt_client_id_for_deletion():
    print("\n=== Choix du client à supprimer ===")
    return input("ID du client (0 = annuler) : ").strip()


def prompt_client_deletion_confirmation(client):
    print("\n=== Suppression d'un client ===")
    print(f"ID : {client.id}")
    print(f"Identité : {client.first_name} {client.last_name}")
    print(f"Entreprise : {client.company_name}")
    return input("Tapez oui pour confirmer : ").strip() == "oui"


def show_client_deletion_cancelled():
    print("\nAnnulation de la suppression")


def show_client_deletion_success():
    print("\nClient supprimé avec succès")


def prompt_client_id_for_modification():
    print("\n=== Choix du client à modifier ===")
    return input("ID du client (0 = annuler) : ").strip()


def prompt_client_modification(client):
    print("\n=== Modification du client ===")
    print(f"ID : {client.id}")
    print(f"Identité : {client.first_name} {client.last_name}")
    print(f"Email : {client.email}")
    print(f"Téléphone : {client.phone}")
    print(f"Entreprise : {client.company_name}")
    print("Valeur vide indique conserver la valeur actuelle")

    first_name = input("Prénom : ").strip()
    last_name = input("Nom : ").strip()
    email = input("Email : ").strip()
    phone = input("Téléphone : ").strip()
    company_name = input("Entreprise : ").strip()
    return first_name, last_name, email, phone, company_name


def show_client_modification_cancelled():
    print("\nAnnulation de la modification")


def show_client_modification_unchanged():
    print("\nAucune modification effectuée")


def show_client_modification_success():
    print("\nClient modifié avec succès")
