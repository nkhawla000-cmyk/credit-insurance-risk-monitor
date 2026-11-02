# Étape 3 — Early Warning Center

La deuxième page du dashboard est désormais disponible. Le projet travaille **uniquement sur des données synthétiques**.

## Installation (dans le dossier credit-insurance-risk-monitor)

1. Décompresser l'archive « Étape 3 » dans le dossier ouvert sur VS Code.
2. Exécuter : `python3 build_dashboard.py`.
3. Exécuter : `python3 -m unittest discover -s tests -v`.
4. Ouvrir : `open dashboard/index.html` sur macOS.
5. Cliquer sur **Early Warning Center** dans la barre latérale.

Il n'est pas nécessaire de régénérer les données si les sorties de l'étape 2 sont encore présentes.

## Principes de calcul

Une alerte correspond à un couple « entreprise assurée - acheteur » représenté par un identifiant de limite de crédit `limit_id`. L'indice de priorité est la **somme de règles pédagogiques** : dépassement (+4), créances anciennes (+3), retards > 30 jours (+2), suspension (+2), profil de risque simulé élevé (+1 uniquement si un autre signal est déclenché). Les seuils exacts figurent dans `src/alerts.py`.

L'indice n'est **pas** un score de crédit, une probabilité de défaut ou une décision automatisée de garantie. L'état de la couverture doit être confirmé dans les systèmes réels avant toute décision métier.

## Scénario de démonstration

- Cliquer sur **Early Warning Center**.
- Dans « Acheteur ou limite », saisir `L0065`. Cliquer sur « Détails » : plusieurs raisons d'alerte expliquent sa priorité élevée.
- Choisir le secteur Automobile, puis « Critique ». Vérifier que les KPI et la liste se mettent à jour.
- Cliquer sur « Réinitialiser » puis sur « Exporter les alertes (CSV) ».
- Revenir à **Executive Overview** pour vérifier que la première page fonctionne toujours.

Les chiffres affichés ne doivent jamais être présentés comme un constat réel sur le marché marocain de l'assurance-crédit.
