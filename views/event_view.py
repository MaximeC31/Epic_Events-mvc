def show_event_list(events):
    print("\n=== Liste des événements ===")

    for event in events:
        print(f"\nID Événement : {event['id']}")
        print(f"ID Contrat : {event['contract_id']}")
        print(f"Client : {event['client_name']} (Contact : {event['client_contact']})")
        print(
            f"Date/Heure : {event['start_time'].strftime('%d/%m/%Y %H:%M')}"
            f" - {event['end_time'].strftime('%d/%m/%Y %H:%M')}"
        )
        support_responsible = event.get("support_responsible") or "Non affecté"
        print(f"Responsable Support : {support_responsible}")
        print(f"Lieu : {event['location']}")
        print(f"Nombre de participants : {event['participant_count']}")
        notes = event.get("notes") or "Aucune note"
        print(f"Notes : {notes}")


def show_empty_event_list():
    print("Aucun événement à afficher.")


def show_event_error(message):
    print(f"Erreur : {message}")
