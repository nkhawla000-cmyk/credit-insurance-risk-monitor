# Power BI — jeux de données exportés

Après `python3 run.py --as-of 2026-10-31`, lancer `python3 export_powerbi.py`.

- `datasets/portfolio_flat.csv` : 140 lignes et un enregistrement par limite ; **premier import conseillé sur Mac** (un seul fichier, pas de relation nécessaire).
- `datasets/dim_limits.csv` : 140 limites, clé `limit_id` unique, dimension de reporting.
- `datasets/fact_exposure.csv` : 140 expositions ponctuelles, clé `limit_id` unique.
- `datasets/fact_invoices.csv` : 840 factures, une par `invoice_id`.
- `datasets/fact_alerts.csv` : alertes explicables, sous-ensemble de limites.
- `datasets/scenario_summary.csv` : 30 scénarios agrégés (grille 5 × 6).
- `datasets/fact_scenarios.csv` : 4 200 combinaisons (scénario × limite).

**Attention à la granularité :** les montants de l'exposition sont répétés sur les factures et les scénarios. Ne pas additionner simultanément des montants de deux tables de faits sans filtre et modèle de relations adéquats. Dans `fact_scenarios`, choisir **exactement un** `scenario_key` avant d'agréger.

Toutes les données sont fictives, en dirhams marocains, arrêtées au 31/10/2026. Aucun `.pbix` n'a été produit automatiquement. Voir [`docs/POWER_BI_FR.md`](../docs/POWER_BI_FR.md).
