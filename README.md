# Cléora

Conciergerie intelligente — premier prototype de phase 1 avec PMS simulé.

**[Guide de lancement et limites](docs/DEMARRAGE.md)**

- FastAPI + PostgreSQL : deux propriétaires, quatre logements, dix réservations fictives.
- Next.js/React : tableau de bord, réservations, conversations et simulateur.
- Création, modification et annulation des séjours, déduplication des événements.
- Brouillons FAQ hors ligne ou Mistral optionnel.
- SMS et emails simulés, exemple n8n manuel. Aucun envoi réel.
- Tests d'isolation et du cycle de réservation dans GitHub Actions.

## Lancement
Copier `.env.example` vers `.env`, remplir les trois valeurs obligatoires puis :

```bash
docker compose up --build
```

Ouvrir http://localhost:3000 et saisir le token du propriétaire choisi.

Prototype local uniquement : authentification Supabase Auth, intégrations réelles Brevo/Twilio,
worker de rappels et connexion PMS réelle restent à développer. Aucun projet Supabase existant n'a été modifié.
