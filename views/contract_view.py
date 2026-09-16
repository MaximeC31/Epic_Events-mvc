def show_contracts(contract_rows):
    print("\n=== Liste des contrats ===")
    for contract in contract_rows:
        print(f"\nContrat: {contract['id']}")
        print(f"Client: {contract['client_name']} ({contract['company']})")
        print(f"Commercial: {contract['salesperson_name']}")
        print(f"Montant total: {contract['total_amount']:.2f} €")
        print(f"Montant restant: {contract['remaining_amount']:.2f} €")
        print(f"Date de création: {contract['created_at'].strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"Statut: {'Signé' if contract['is_signed'] else 'Non signé'}")
        print("-")


def show_empty_contract_list():
    print("Aucun contrat n'est enregistré.")


def show_contract_error(message):
    print(f"Erreur: {message}")
