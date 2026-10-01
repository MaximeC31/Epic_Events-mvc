def show_event_list(events):
    print("\n=== Liste des événements ===")

    for event in events:
        client = event.contract.client
        client_name = f"{client.first_name} {client.last_name}"
        client_contact = f"{client.email} / {client.phone}"
        support = f"{event.support.first_name} {event.support.last_name}" if event.support else "Non affecté"

        print(f"\nID Événement : {event.id}")
        print(f"ID Contrat : {event.contract_id}")
        print(f"Client : {client_name} (Contact : {client_contact})")
        print(
            f"Date/Heure : {event.start_datetime.strftime('%d/%m/%Y %H:%M')}"
            f" - {event.end_datetime.strftime('%d/%m/%Y %H:%M')}"
        )
        print(f"Responsable Support : {support}")
        print(f"Lieu : {event.location}")
        print(f"Nombre de participants : {event.number_of_participants}")
        notes = event.notes or "Aucune note"
        print(f"Notes : {notes}")


def show_empty_event_list():
    print("\nAucun événement à afficher.")


def show_event_error(message):
    print(f"\nErreur : {message}")


def prompt_event_contract_selection(contracts):
    print("\n=== Création d'un événement ===")
    print("Contrats signés de vos clients :")
    for contract in contracts:
        client = contract.client
        print(f"ID {contract.id} - {client.first_name} {client.last_name} ({client.company_name})")
    return input("ID du contrat (0 = annuler) : ").strip()


def prompt_event_creation():
    start_choice = input("Date de début (JJ/MM/AAAA HH:MM) : ").strip()
    end_choice = input("Date de fin (JJ/MM/AAAA HH:MM) : ").strip()
    location = input("Lieu : ").strip()
    participants_choice = input("Nombre de participants : ").strip()
    notes = input("Notes (facultatives) : ").strip()
    return start_choice, end_choice, location, participants_choice, notes


def show_event_creation_cancelled():
    print("\nAnnulation de la création")


def show_event_creation_success():
    print("\nÉvénement créé avec succès")


def prompt_event_id_for_deletion():
    print("\n=== Choix de l'événement à supprimer ===")
    return input("ID de l'événement (0 = annuler) : ").strip()


def prompt_event_deletion_confirmation(event):
    print("\n=== Suppression d'un événement ===")
    show_event_list([event])
    print("Cette suppression est définitive.")
    return input("Tapez oui pour confirmer : ").strip() == "oui"


def show_event_deletion_cancelled():
    print("\nAnnulation de la suppression")


def show_event_deletion_success():
    print("\nÉvénement supprimé avec succès")


def prompt_event_id_for_modification():
    print("\n=== Choix de l'événement à modifier ===")
    return input("ID de l'événement (0 = annuler) : ").strip()


def prompt_event_support_assignment(event, supports):
    print("\n=== Affectation du support ===")
    show_event_list([event])
    if supports:
        print("Supports actifs disponibles :")
        for support in supports:
            print(f"ID {support.id} - {support.first_name} {support.last_name}")
    else:
        print("Aucun support actif disponible.")
    print("Vide = conserver ; 0 = retirer ; ID = affecter un support actif.")
    return input("ID du support : ").strip()


def show_event_modification_cancelled():
    print("\nAnnulation de la modification")


def show_event_modification_unchanged():
    print("\nAucune modification effectuée")


def show_event_modification_success():
    print("\nÉvénement modifié avec succès")
