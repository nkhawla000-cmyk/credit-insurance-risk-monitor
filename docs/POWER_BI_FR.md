# Guide Power BI (sur Mac et sur Windows)

## A. Sur Mac : démarrer dans le navigateur

Power BI Desktop n'est pas une application macOS native. Utilisez le service Power BI sur https://app.powerbi.com/ (compte Microsoft et droits selon votre organisation).

1. Exécuter dans VS Code : `python3 export_powerbi.py`.
2. Ouvrir le service Power BI dans un navigateur moderne ; aller dans **Mon espace de travail**.
3. Suivre **Nouvel élément → Modèle sémantique → CSV**, puis charger `powerbi/datasets/portfolio_flat.csv`. Les intitulés peuvent varier selon l'interface et la licence.
4. Vérifier que les montants sont reconnus comme nombres et `as_of` comme date (si non, ajuster les types).
5. Cliquer **Créer un rapport**, réaliser une page « Portfolio Overview » :
   - Carte : somme `outstanding_mad`
   - Carte : somme `overdue_mad`
   - Carte : somme `over_limit_mad`
   - Graphique en barres : `sector` / somme `outstanding_mad`
   - Tableau : `buyer_id`, somme `outstanding_mad`, somme `overdue_30_plus_mad`
   - Segments : `sector`, `region`, `risk_band`, `status`
6. Pour le ratio d'utilisation, employer une mesure : `DIVIDE(SUM(Portfolio[outstanding_mad]),SUM(Portfolio[credit_limit_mad]),0)` et formater en pourcentage. Ne pas sommer les pourcentages ligne à ligne.

**Limites :** selon les capacités de votre compte, la création de mesures ou l'édition du modèle sémantique peut être restreinte. Le dashboard HTML reste la démonstration autonome principale tant qu'un rapport Power BI n'est pas effectivement créé et vérifié.

## B. Modèle étoile (Power BI Desktop sous Windows / environnement compatible)

Charger les 5 CSV : `dim_limits`, `fact_exposure`, `fact_invoices`, `fact_alerts`, `fact_scenarios`.
Créer les relations (direction simple, cardinalité indiquée) :

- `DimLimits[limit_id]` **1 → *** `FactExposure[limit_id]` (1 ligne par limite ; vérifier 1:1 si Power BI le propose)
- `DimLimits[limit_id]` **1 → *** `FactInvoices[limit_id]`
- `DimLimits[limit_id]` **1 → *** `FactAlerts[limit_id]` (0 ou 1 alerte par limite)
- `DimLimits[limit_id]` **1 → *** `FactScenarios[limit_id]`

**Granularité et vigilance :** si `FactExposure` et `DimLimits` sont liées au niveau unique de limite, ne pas faire de jointure physique qui reproduit l'exposition pour chaque facture. Pour les scénarios, charger aussi `scenario_summary` séparément ou créer une dimension `DimScenario` à partir des valeurs uniques de `scenario_key` ; avant toute somme dans `FactScenarios`, filtrer **une seule valeur** de `scenario_key` (sinon les montants sont multipliés par 30).

Le CSV `scenario_summary.csv` permet, de manière indépendante, de comparer les 30 hypothèses sans modèle relationnel complexe.

## C. Bonnes pratiques métier

- Tous les montants sont synthétiques en MAD.
- `risk_band` est une étiquette de scénario, pas une probabilité de défaut.
- `over_limit_mad` représente un dépassement de la limite **simulée**, pas une décision d'indemnisation.
- `aging_days` est un choc contrefactuel d'ancienneté, pas une prévision des paiements.
- Les limites sont fictives et leur historique de modifications n'est pas simulé.

## Liens Microsoft

- Power BI Desktop (Windows) : https://learn.microsoft.com/fr-fr/power-bi/fundamentals/desktop-get-the-desktop
- Ajouter un CSV au service : https://learn.microsoft.com/en-us/power-bi/connect-data/service-comma-separated-value-files
- Rapports dans Power BI service : https://learn.microsoft.com/en-us/power-bi/create-reports/power-bi-reports-overview
