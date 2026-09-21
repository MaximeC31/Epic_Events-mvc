def show_clients(clients):
    print("\nTous les clients :")
    for client in clients:
        salesperson = client.sales_contact

        print(f"\nPrénom: {client.first_name}, Nom: {client.last_name}")
        print(f"Email: {client.email}, Téléphone: {client.phone}, " f"Entreprise: {client.company_name}")
        print(f"Créé le: {client.created_at}, Dernier contact: {client.last_contact_at}")
        print(f"Commercial associé: {salesperson.first_name} {salesperson.last_name}")
        print("-")


def show_empty_client_list():
    print("Aucun client n'est enregistré.")


def show_client_error(message):
    print(f"Erreur : {message}")
