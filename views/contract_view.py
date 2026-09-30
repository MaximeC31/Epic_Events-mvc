def show_contracts(contracts):
    print("\n=== Liste des contrats ===")
    for contract in contracts:
        client = contract.client
        salesperson = client.sales_contact

        print(f"\nContrat: {contract.id}")
        print(f"Client: {client.first_name} {client.last_name} ({client.company_name})")
        print(f"Commercial: {salesperson.first_name} {salesperson.last_name}")
        print(f"Montant total: {contract.total_amount:.2f} €")
        print(f"Montant restant: {contract.remaining_amount:.2f} €")
        print(f"Date de création: {contract.created_at.strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"Statut: {'Signé' if contract.is_signed else 'Non signé'}")
        print("-")


def show_empty_contract_list():
    print("\nAucun contrat n'est enregistré.")


def show_contract_error(message):
    print(f"\nErreur: {message}")


def prompt_contract_client_selection(clients):
    print("\n=== Création d'un contrat ===")
    print("Clients disponibles :")
    for client in clients:
        print(f"ID {client.id} - {client.first_name} {client.last_name} ({client.company_name})")

    return input("ID du client (0 = annuler) : ").strip()


def prompt_contract_amount():
    return input("Montant total en euros (virgule décimale) : ").strip()


def show_contract_creation_cancelled():
    print("\nAnnulation de la création")


def show_contract_creation_success():
    print("\nContrat créé avec succès")


def prompt_contract_id_for_deletion():
    print("\n=== Choix du contrat à supprimer ===")
    return input("ID du contrat (0 = annuler) : ").strip()


def prompt_contract_deletion_confirmation(contract):
    print("\n=== Suppression d'un contrat ===")
    print(f"ID : {contract.id}")
    print(f"Client : {contract.client.first_name} {contract.client.last_name}")
    print(f"Montant total : {contract.total_amount:.2f} €")
    print(f"Montant restant : {contract.remaining_amount:.2f} €")
    print(f"Statut : {'Signé' if contract.is_signed else 'Non signé'}")
    return input("Tapez oui pour confirmer : ").strip() == "oui"


def show_contract_deletion_cancelled():
    print("\nAnnulation de la suppression")


def show_contract_deletion_success():
    print("\nContrat supprimé avec succès")


def prompt_contract_id_for_modification():
    print("\n=== Choix du contrat à modifier ===")
    return input("ID du contrat (0 = annuler) : ").strip()


def prompt_contract_modification(contract, clients):
    print("\n=== Modification du contrat ===")
    print(f"ID : {contract.id}")
    print(f"Client : {contract.client.first_name} {contract.client.last_name} (ID {contract.client_id})")
    print(f"Montant total : {contract.total_amount:.2f} €")
    print(f"Montant restant : {contract.remaining_amount:.2f} €")
    print(f"Date de création : {contract.created_at.strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"Statut : {'Signé' if contract.is_signed else 'Non signé'}")
    print("Choisir le nouveau client parmi :")
    for client in clients:
        print(f"ID {client.id} - {client.first_name} {client.last_name} ({client.company_name})")
    print("Valeur vide indique conserver la valeur actuelle")

    client_choice = input("ID du client : ").strip()
    total_choice = input("Montant total en euros (virgule décimale) : ").strip()
    remaining_choice = input("Montant restant en euros (virgule décimale) : ").strip()
    status_choice = input("Statut (0 = non signé, 1 = signé) : ").strip()
    return client_choice, total_choice, remaining_choice, status_choice


def show_contract_modification_cancelled():
    print("\nAnnulation de la modification")


def show_contract_modification_unchanged():
    print("\nAucune modification effectuée")


def show_contract_modification_success():
    print("\nContrat modifié avec succès")
