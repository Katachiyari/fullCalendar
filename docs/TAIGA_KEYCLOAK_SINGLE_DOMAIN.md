# Taiga + Keycloak (single domain)

Objectif: OpsHub reste sur `/` et Taiga est accessible sous `/kanban/` sur le même domaine. Keycloak est accessible sous `/id/`.

## Démarrage

Depuis la racine du projet:

- `docker compose up -d --build`

Accès:

- OpsHub: `http://localhost/`
- Taiga: `http://localhost/kanban/`
- Keycloak: `http://localhost/id/`

## SSO (OIDC)

Taiga est configuré avec le plugin OIDC pour rediriger vers Keycloak.

- Point d’entrée OIDC (Taiga) : `http://localhost/kanban/api/oidc/authenticate/`
- Callback OIDC (Taiga) : `http://localhost/kanban/api/oidc/callback/`
- Discovery (Keycloak) : `http://localhost/id/realms/opshub/.well-known/openid-configuration`

La page de login Taiga affiche un bouton **OpsHub SSO** (plugin front chargé via `conf.json`).

## Créer le compte admin Taiga

Taiga nécessite un superuser côté backend.

- `docker compose run --rm taiga-manage createsuperuser`

## Notes

- Taiga est configuré en mode **subpath** via `TAIGA_SUBPATH` (par défaut: `/kanban`).
- Le routage est fait par le container `gateway` (nginx). Taiga tourne derrière `taiga-gateway`.
- Keycloak tourne en mode dev et sert son UI sous `/id/`.

## Variables utiles

Tu peux surcharger via un `.env` local (compose le charge automatiquement):

- `TAIGA_DOMAIN` (défaut: `localhost`)
- `TAIGA_SUBPATH` (défaut: `/kanban`)
- `TAIGA_SECRET_KEY` (à changer en prod)
- `TAIGA_OIDC_CLIENT_ID` (défaut: `taiga`)
- `TAIGA_OIDC_CLIENT_SECRET` (doit matcher le client OIDC Keycloak)
- `TAIGA_OIDC_AUTH_ENDPOINT` (défaut: `http://localhost/id/realms/opshub/protocol/openid-connect/auth`)
- `KEYCLOAK_ADMIN` / `KEYCLOAK_ADMIN_PASSWORD`

Note: pour éviter les problèmes d'accès à `github.com` pendant les builds, les images Taiga custom téléchargent le plugin OIDC depuis l’endpoint zip `codeload.github.com`.
