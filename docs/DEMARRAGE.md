# Cléora : premier prototype de phase 1

## Démarrer
Prérequis : Git et Docker avec Compose. Aucun compte Airbnb ou PMS nécessaire.

```bash
git clone https://github.com/droidmonster-glitch/CLEORA.git
cd CLEORA
git switch codex/phase1-mock-pms
cp .env.example .env
```

Sur Windows PowerShell : utiliser `Copy-Item .env.example .env`.
Remplir les trois valeurs obligatoires dans .env : mot de passe PostgreSQL et deux tokens distincts (au moins 24 caractères).
Générer chaque valeur avec `python -c "import secrets; print(secrets.token_hex(24))"`.
Ne pas communiquer ces valeurs ni les committer.

```bash
docker compose up --build
```

Ouvrir http://localhost:3000 et saisir AREZKI_TOKEN ou SARAH_TOKEN.
API interactive : http://localhost:8000/docs (bouton Authorize avec le token).
Les données persistent après un arrêt. `docker compose down` conserve les volumes.
Le prototype écoute uniquement sur localhost.

## Ce qui fonctionne
Deux propriétaires, quatre logements, dix réservations fictives (passées, en cours et futures), messages.
Statuts : pending, confirmed, cancelled. La période du séjour découle des dates.
Création, changement des dates, annulation, contrôle des chevauchements des séjours confirmés.
Événement identique rejoué : pas de nouvel effet. Même identifiant et payload différent : erreur 409.
Transaction PostgreSQL et verrou par propriétaire pour sérialiser les mutations du simulateur.
Journal de notifications email/SMS simulées ; modification et annulation des rappels du simulateur.
Les réservations initiales n'ont pas de rappels précréés : ceux-ci apparaissent après un événement.
FAQ déterministe sans clé IA ; brouillon Mistral optionnel via MISTRAL_API_KEY.
Chaque brouillon reste à valider, aucun envoi externe implémenté.

## Parcours de validation
1. Connexion Arezki : deux logements visibles.
2. Simulateur : créer un séjour sur des dates libres (par exemple dans deux mois).
3. Rejouer le dernier événement : aucun doublon dans le journal.
4. Modifier le séjour : ancien rappel annulé, nouveau rappel planifié.
5. Annuler : aucun rappel actif pour ce séjour.
6. Messages : poser une question parking ; consulter le brouillon.
7. Déconnexion puis token Sarah : les données Arezki ne sont pas visibles.
8. Les tests CI couvrent aussi les accès croisés, dates invalides et chevauchements.

## Supabase
Aucun projet Cléora n'a été identifié lors de l'inspection ; aucun projet existant n'a été modifié.
Le prototype utilise SQLAlchemy/PostgreSQL, sans dépendre du SDK Supabase.
Pour une base Supabase dédiée : configurer DATABASE_URL côté serveur avec la chaîne de connexion
appropriée et SSL. Ne jamais exposer les identifiants DB au frontend.
Avant connexion : appliquer la migration `supabase/migrations/001_demo.sql` avec un rôle administrateur.
Celle-ci bloque les rôles publics Supabase ; le backend utilise un rôle serveur.
L'authentification Supabase Auth et les politiques par utilisateur restent à implémenter.
Les tokens fixes servent uniquement au développement local, pas à un SaaS public.

## n8n, Twilio, Brevo : état exact
`docker compose --profile automation up -d` démarre n8n sur http://localhost:5678.
Importer `n8n/mock-notification.json` pour examiner un événement fictif.
Ce workflow manuel n'est PAS connecté automatiquement au backend.
Twilio et Brevo sont représentés par un journal local, sans appel aux fournisseurs.
Les rappels sont enregistrés, mais aucun worker ne les exécute à échéance.
À compléter : outbox durable, worker avec reprises, intégrations fournisseurs et destinataires autorisés,
workflow n8n authentifié et surveillance des échecs.

## Limites de cette livraison
C'est un prototype exécutable proposé, pas la phase 1 commercialisable complète.
Pas de compte SaaS autonome, envoi réel, modification des fiches, validation/envoi des brouillons,
PMS réel, agent vocal ou serrure. Pas de déploiement public.
Stockage de démonstration : un document JSON par propriétaire, à normaliser par migrations pour la V1.
Le connecteur MockPMSConnector concentre les règles du simulateur ; l'adaptateur Smoobu reste à écrire.
Verrouillage testé séquentiellement ; tests de concurrence et de charge restent nécessaires.
Versions majeures bornées mais fichiers de verrouillage absents : les générer après premier build réussi.
Le code a été rédigé via GitHub ; exécution locale et rendu visuel non disponibles dans cette session.
Ne considérer les tests comme réussis qu'après consultation des résultats GitHub Actions.

Sources techniques : https://nextjs.org/docs/app/getting-started/installation ;
https://docs.mistral.ai/api/endpoint/chat ; https://docs.n8n.io/hosting/installation/docker/
