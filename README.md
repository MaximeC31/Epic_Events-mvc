# Epic Events

CRM interne local développé en Python avec une architecture MVC.

Le projet centralise la gestion des collaborateurs, clients, contrats et événements selon les permissions des équipes gestion, commerciale et support.

## Fonctionnalités

- Authentification individuelle par email et mot de passe haché avec bcrypt.
- Consultation de tous les clients, contrats et événements par les collaborateurs actifs.
- Gestion : création, modification et suppression des collaborateurs et des contrats.
- Gestion : affectation, remplacement ou retrait du support d'un événement, filtre des événements sans support et suppression d'événements.
- Commercial : création et modification de ses clients ; suppression possible si aucun contrat ne les référence.
- Commercial : modification des montants et de la signature des contrats de ses clients, sans changement de client.
- Commercial : filtres de ses contrats non signés ou non entièrement payés.
- Commercial : création d'événements pour ses clients ayant signé un contrat.
- Support : filtre et modification de ses événements attribués (dates, lieu, participants et notes).
- Validation des données, transactions SQLAlchemy et journalisation des exceptions avec Sentry.

Les suppressions demandent une confirmation. Un contrat lié à un événement ne peut pas être supprimé ; les références des collaborateurs sont protégées par les clés étrangères.

## Stack

- Python 3.14.7 pour l'environnement de développement.
- PostgreSQL (version locale utilisée : 18.6).
- SQLAlchemy 2 et Psycopg 3.
- bcrypt pour les mots de passe.
- python-dotenv pour la configuration locale.
- Sentry SDK pour la journalisation.

Les versions des dépendances sont fixées dans `requirements.txt`.

## Installation

Prérequis : Python correspondant à `.python-version`, PostgreSQL et une base accessible avec un compte applicatif non-superutilisateur.

Depuis la racine du projet :

```bash
python3 -m venv .venv
.venv/bin/python3 -m pip install -r requirements.txt
cp .env.example .env
```

Créer la base et le compte applicatif avec un compte administrateur PostgreSQL. Exemple à adapter, dans `psql` :

```sql
CREATE ROLE epic_events LOGIN PASSWORD 'REMPLACER_PAR_UN_MOT_DE_PASSE';
CREATE DATABASE epic_events OWNER epic_events;
```

Le schéma choisi doit déjà exister et le compte applicatif doit pouvoir y créer les tables. Pour un schéma `public` préexistant, vérifier ses droits dans la base `epic_events`.

Renseigner le fichier `.env` :

```dotenv
DATABASE_URL=postgresql+psycopg://epic_events:MOT_DE_PASSE@localhost:5432/epic_events
SENTRY_DSN=
SENTRY_ENVIRONMENT=development
```

Encoder les caractères spéciaux du mot de passe dans l'URL. L'application utilise `DATABASE_URL` ; le champ `DATABASE_PASSWORD` du modèle `.env.example` n'est pas lu séparément. Ne pas versionner `.env` ni les identifiants réels.

## Démarrage et authentification

```bash
.venv/bin/python3 main.py
```

Au démarrage, l'application crée les tables manquantes. Si aucun collaborateur n'existe, un formulaire permet de créer le premier compte gestion. Ce démarrage peut donc écrire dans la base.

Se connecter ensuite avec l'email et le mot de passe du collaborateur. Les comptes inactifs sont refusés. Le menu affiche les actions propres au rôle et permet la déconnexion.

`create_all()` ne crée ni la base ni le schéma et ne migre pas les tables existantes. Une ancienne contrainte autorisant un montant total de contrat nul doit être alignée séparément avec la règle actuelle `total_amount > 0`.

## Permissions et règles métier

| Rôle                           | Actions principales                                                                                             |
| ------------------------------ | --------------------------------------------------------------------------------------------------------------- |
| Tous les collaborateurs actifs | Lecture globale des clients, contrats et événements                                                             |
| Gestion                        | Administration des collaborateurs et contrats ; affectation et suppression des événements ; filtre sans support |
| Commercial                     | Gestion de ses clients ; modification et filtrage de leurs contrats ; création d'événements sur contrat signé   |
| Support                        | Consultation filtrée et modification de ses événements attribués                                                |

Le rôle et le statut sont rechargés en base avant chaque action protégée. Les controllers revérifient l'appartenance des clients/contrats ou l'affectation des événements avant les écritures concernées. Ces contrôles ne constituent pas un verrou contre les modifications concurrentes ; le menu peut conserver l'identité et le rôle affichés à la connexion.

- Téléphone client : numéro français à dix chiffres (fixe ou mobile), ou numéro international avec `+` et 7 à 15 chiffres. Espaces, points, tirets et groupes entre parenthèses sont acceptés, par exemple `01 23 45 67 89`, `+678 123 456 78` ou `+1 (234) 567-8901`. Le format saisi est conservé ; la validation ne garantit pas l'existence du numéro.
- Montants : total strictement positif, restant entre zéro et le total ; saisie avec virgule et au plus deux décimales.
- Dates d'événement : `JJ/MM/AAAA HH:MM`, fin supérieure ou égale au début ; dates passées autorisées.
- Participants : entier entre zéro et `2147483647` ; lieu obligatoire, notes facultatives.
- Plusieurs événements peuvent partager un contrat signé ; le paiement complet n'est pas requis.
- Dans les formulaires de modification, une saisie vide conserve la valeur actuelle. Pour les notes d'un événement, `0` les efface.

## Journalisation Sentry

Créer un projet **Python** dans Sentry, puis ajouter son DSN dans `.env` :

```dotenv
SENTRY_DSN=https://<cle>@<serveur-sentry>/<projet>
SENTRY_ENVIRONMENT=development
```

## Commandes utiles et vérification

```bash
# Démarrer la CLI
.venv/bin/python3 main.py
```

La compilation écrit des caches de bytecode et ne vérifie ni les imports ni le comportement. Aucun runner de tests automatisés, lint ou typecheck n'est configuré ; les parcours métier et refus d'accès sont vérifiés manuellement.

## Parcours principal

1. Initialiser le premier gestionnaire, puis créer les comptes commerciaux et supports.
2. Un commercial crée un client, automatiquement associé à son compte.
3. La gestion crée un contrat pour ce client.
4. La gestion ou le commercial responsable enregistre sa signature et suit les montants.
5. Le commercial crée un événement sur ce contrat signé.
6. La gestion affecte un support actif à l'événement.
7. Le support consulte ses événements et met à jour les informations d'organisation.

## Données de démonstration

Le jeu préparé dans la base locale comprend **7 collaborateurs, 14 clients, 21 contrats et 28 événements** : clients sans contrat, contrats signés/non signés et soldés/partiellement payés/impayés, événements passés/futurs et avec/sans support.

Ces données ne sont pas incluses dans le dépôt et aucun script de peuplement n'est fourni. Une nouvelle installation initialise son propre compte gestion ; elle ne dispose pas automatiquement des comptes ou exemples de la base de développement.

## Structure

Le [schéma relationnel de la base de données](database-schema.png) présente les tables, leurs champs, les clés et les cardinalités.

![Schéma relationnel de la base de données Epic Events](database-schema.png)

- `main.py` : point d'entrée et initialisation de la journalisation.
- `models/` : mappings SQLAlchemy, relations, validation des formats, schéma et sessions transactionnelles.
- `controllers/` : authentification, routage des menus, permissions métier et opérations de persistance.
- `views/` : formulaires et affichage de la CLI.
- `decorators.py` : vérification du collaborateur et de ses rôles autorisés.
- `monitoring.py` : configuration Sentry et masquage des erreurs SQL.
- `.env.example` : modèle de configuration sans identifiants réels.
- `requirements.txt` : dépendances Python fixées.
