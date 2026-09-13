def show_clients(client_rows):
    print("\nTous les clients :")
    for row in client_rows:
        print(f"\nPrénom: {row['first_name']}, Nom: {row['last_name']}")
        print(f"Email: {row['email']}, Téléphone: {row['phone']}, Entreprise: {row['company']}")
        print(f"Créé le: {row['created_at']}, Dernier contact: {row['last_contact_at']}")
        print(f"Commercial associé: {row['salesperson_name']}")
        print("-")


def show_empty_client_list():
    print("Aucun client n'est enregistré.")


def show_client_error(message):
    print(f"Erreur : {message}")
