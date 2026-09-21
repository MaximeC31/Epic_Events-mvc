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
    print("Aucun événement à afficher.")


def show_event_error(message):
    print(f"Erreur : {message}")
