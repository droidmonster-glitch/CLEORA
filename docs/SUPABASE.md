# Connexion au projet Supabase CLEORA

Projet : hewasycyugomgncotgoe (Europe centrale).
URL : https://hewasycyugomgncotgoe.supabase.co

## État appliqué
- Tables cleora_demo_workspaces et cleora_memberships.
- Deux espaces fictifs Arezki / Sarah, chacun avec deux logements et cinq réservations.
- RLS : lecture uniquement de son espace et de son rattachement.
- Aucune écriture client sur les tables, en particulier les rattachements.
- Test SQL d'isolation exécuté dans une transaction annulée ; aucun compte de test conservé.
- Aucun utilisateur Auth permanent créé, aucun email envoyé.
- Le backend valide chaque session via /auth/v1/user avant de rechercher le rattachement.
- Les écritures passent par le backend et ses transactions SQL. La connexion SQL serveur
  doit rester secrète car son rôle peut contourner RLS.

## 1. Configurer le serveur
Copier .env.example en .env.
Dans Supabase > Connect, copier la chaîne PostgreSQL **Session pooler** (compatible IPv4).
Remplacer le schéma postgresql:// par postgresql+psycopg://, compléter le mot de passe
de la base (encoder les caractères spéciaux dans l'URL) et ajouter ?sslmode=require.
Renseigner SUPABASE_DATABASE_URL dans .env. Ne pas envoyer cette valeur dans le chat.
SUPABASE_PUBLISHABLE_KEY est préremplie : cette clé est publique et ne donne aucun droit
de lecture sans session et politique RLS. Ne pas y substituer une clé service_role.

## 2. Créer les deux comptes propriétaires
Dans Supabase > Authentication > Users > Add user > Create new user, créer deux utilisateurs
email/mot de passe avec des adresses que vous contrôlez. Pour ces comptes de test créés par
l'administrateur, confirmer les comptes si nécessaire. Aucun formulaire d'inscription publique
n'est inclus dans le prototype.

Dans le SQL Editor, remplacer les deux adresses ci-dessous par celles des comptes créés,
puis exécuter. Chaque INSERT doit ajouter exactement une ligne ; si aucune ligne,
l'email n'existe pas encore. Les emails doivent être distincts.
Ne jamais associer un compte à un propriétaire via user_metadata.

```sql
insert into public.cleora_memberships(user_id, owner)
select id, 'arezki' from auth.users where lower(email)=lower('compte-arezki@example.invalid');

insert into public.cleora_memberships(user_id, owner)
select id, 'sarah' from auth.users where lower(email)=lower('compte-sarah@example.invalid');

select owner, count(*) from public.cleora_memberships group by owner;
```

Les UUID sont récupérés depuis auth.users, jamais inventés.
Un compte sans rattachement reçoit une erreur 403.

## 3. Lancer
Arrêter auparavant la configuration locale si elle occupe les ports :
```bash
docker compose down
docker compose --env-file .env -f compose.supabase.yaml up --build
```
La deuxième commande démarre FastAPI et Next.js, sans PostgreSQL local.
Ouvrir http://localhost:3000 : le formulaire propose email et mot de passe.
L'API garde les sessions en mémoire côté navigateur, sans localStorage.
Après expiration ou rechargement, se reconnecter ; le renouvellement automatique n'est pas implémenté.
La déconnexion efface la session locale et demande sa révocation à Supabase.
Les jetons d'accès déjà émis peuvent rester utilisables jusqu'à expiration selon Supabase.
Lancer les tests uniquement sur une base dédiée de test, jamais sur ce projet.

## Validation et limites
Le mode local par tokens reste disponible avec compose.yaml.
Le mode Supabase refuse les tokens de démonstration ; vérification auprès du serveur Auth obligatoire.
Les sessions invalides/expirées sont refusées (401), sans accès de secours ; panne Auth : 503.
Les emails/SMS, PMS et rappels restent simulés.
Aucun déploiement applicatif n'a été réalisé et aucune connexion du serveur applicatif à Supabase
n'a pu être vérifiée sans sa chaîne de connexion privée.
Le backend requiert un rôle SQL serveur adapté ; ne pas l'exposer publiquement sans HTTPS,
limitation de débit, gestion des secrets et validation complète des parcours.
Les données du prototype restent stockées en JSON par espace, à normaliser pour la V1.

Source : https://supabase.com/docs/guides/getting-started/tutorials/with-nextjs
