# ClauseWatch – Starter Kit v4 (complet)

## Démarrage (une seule fois)
```bash
make setup && make bootstrap
```
Puis poussez sur GitHub (privé recommandé) et activez **Actions**.
(Optionnel) Activez **Pages** pour publier automatiquement `frontend`.

## Automatisation
- **Daily-Automation** (07:00 Paris) : bootstrap → self-check → pipeline → auto-repair → commit des pages générées.
- **CI** : lint + tests de fumée à chaque push/PR.

## Où voir les résultats ?
- Pages `.astro` générées dans `frontend/pages/updates/`.
- Onglet **Actions** pour l’historique et les logs.

## Personnalisation (plus tard)
- Ajoutez des fetchers réels dans `data_sources/`.
- Branchez un envoi d’emails en ajoutant des secrets SMTP (facultatif).