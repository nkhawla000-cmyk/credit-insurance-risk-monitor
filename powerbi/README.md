# Power BI — jeux de données exportés

# Credit Insurance Risk Monitor — Power BI

Ce rapport Power BI complète le pipeline de traitement des données développé en Python et le tableau de bord web du projet **Credit Insurance Risk Monitor**.

Il permet d'explorer un portefeuille fictif d'assurance-crédit, d'identifier les expositions nécessitant une attention particulière et d'étudier les effets de scénarios de détérioration des conditions de paiement.

**[Télécharger le rapport Power BI (.pbix)](./Credit_Insurance_Risk_Monitor.pbix)**

Le fichier peut être ouvert directement dans Power BI Desktop.

## 1. Présentation du rapport

Le rapport comporte trois pages interactives.

### Portfolio Intelligence

Cette page présente une vue d'ensemble du portefeuille :

- Suivi des encours et des créances en retard.
- Mesure des dépassements de limites de crédit.
- Analyse du taux d'utilisation des limites.
- Répartition des expositions par secteur et par région.
- Exploration des résultats à l'aide de filtres.

### Early Warning Center

Cette page permet d'identifier les situations nécessitant un examen :

- Classification des alertes selon leur priorité.
- Présentation des critères ayant déclenché les alertes.
- Classement des dossiers selon leur score de priorité.
- Consultation des montants associés aux alertes.

Les alertes reposent sur des règles métier illustratives. Elles ne constituent pas des probabilités de défaut.

### Sensitivity Lab

Cette page étudie les effets de 30 scénarios hypothétiques combinant :

- Des retards de paiement supplémentaires.
- Des réductions des limites de crédit.

Les résultats permettent de comparer les conséquences de ces hypothèses sur les créances en retard, les dépassements, les alertes critiques et l'utilisation des limites.

Les scénarios sont préalablement calculés à partir de données synthétiques.

## 2. Données utilisées

Le rapport repose sur un portefeuille entièrement synthétique, arrêté au **31 octobre 2026**.

Le jeu de données comprend notamment :

| Indicateur | Valeur |
|---|---:|
| Fournisseurs assurés | 8 |
| Acheteurs | 80 |
| Limites de crédit | 140 |
| Factures valides | 840 |
| Alertes métier | 119 |
| Scénarios de sensibilité | 30 |

Les données ne représentent pas un portefeuille réel et ne doivent pas être interprétées comme des statistiques du marché marocain.

## 3. Jeux de données exportés

Les fichiers CSV utilisés pour l'analyse sont disponibles dans le dossier `datasets/`.

- `portfolio_flat.csv` : vue consolidée du portefeuille, avec un enregistrement par limite.
- `dim_limits.csv` : référentiel des 140 limites de crédit.
- `fact_exposure.csv` : données d'exposition.
- `fact_invoices.csv` : données des 840 factures valides.
- `fact_alerts.csv` : alertes générées par les règles métier.
- `scenario_summary.csv` : résultats agrégés des 30 scénarios.
- `fact_scenarios.csv` : résultats détaillés par scénario et par limite.

Pour régénérer les exports depuis la racine du dépôt :

```bash
python run.py --as-of 2026-10-31
python export_powerbi.py
```

**Attention à la granularité :** les montants d'exposition peuvent être répétés dans les tables de factures et de scénarios. Il ne faut pas additionner ces montants entre plusieurs tables sans tenir compte des relations et des filtres. Pour analyser les résultats détaillés de `fact_scenarios.csv`, il faut sélectionner un scénario spécifique.

## 4. Technologies

- **Power BI Desktop** : création des tableaux de bord et des visualisations.
- **DAX** : calcul des indicateurs.
- **Python** : préparation des données et calcul des scénarios.
- **CSV** : stockage des exports destinés au reporting.

Le fichier `mesures.dax` fournit également des définitions DAX de référence.

## 5. Utilisation et limites

Pour consulter le rapport :

1. Télécharger `Credit_Insurance_Risk_Monitor.pbix`.
2. Ouvrir le fichier avec Power BI Desktop.
3. Parcourir les trois pages et utiliser les filtres pour explorer les données.

Le rapport contient un instantané des données préparées pour la démonstration. Les modifications apportées ultérieurement aux fichiers CSV ne sont pas automatiquement répercutées dans le modèle Power BI.

Ce projet est une démonstration académique d'analyse et de suivi des risques. Il ne constitue pas un outil opérationnel de décision de crédit ou d'assurance.

Pour davantage de détails, consulter la [documentation Power BI](../docs/POWER_BI_FR.md).
