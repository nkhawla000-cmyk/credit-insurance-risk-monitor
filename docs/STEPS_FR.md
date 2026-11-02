# Guide de réalisation — Partie 1/4

## Contexte métier
L'assurance-crédit B2B couvre, selon le contrat, le risque de non-paiement des acheteurs d'une entreprise assurée. Le projet distingue donc l'**entreprise assurée** (policyholder) de l'**acheteur débiteur** (buyer) et associe une limite de crédit à leur relation commerciale.

## Prérequis
Python 3.10 ou supérieur. Aucune bibliothèque externe pour cette première étape.

## Déroulement
1. Décompresser le projet dans un dossier.
2. Dans le terminal, se placer dans le dossier contenant `run.py`.
3. Lancer `python3 -m src.generate` : fabrique les cinq fichiers CSV fictifs, reproductibles avec la même graine.
4. Lancer `python3 run.py --as-of 2026-10-31` : contrôle et importe dans SQLite, calcule les indicateurs à la date souhaitée et génère les exports dans `outputs/`.
5. Lancer `python3 -m unittest discover -s tests -v` : teste les règles métier, les clés étrangères et les comportements temporels.
6. Ouvrir `outputs/kpis.json`, `outputs/anomalies.csv` et `outputs/credit_limits_snapshot.csv`. L'objectif est de comprendre et de vérifier les résultats, pas encore de les publier.

## Trois éléments à expliquer lors d'un entretien
1. Une **facture** est rattachée à une ligne de crédit (entreprise assurée ↔ acheteur). Le débiteur n'est pas le souscripteur de l'assurance.
2. Les **paiements datés** permettent de recalculer un solde historique sans incorporer des règlements effectués après la date d'analyse (pas de fuite temporelle).
3. Les **rejets contrôlés** protègent le reporting contre les doublons, les identifiants inconnus et les paiements incohérents ; ils restent consultables dans le journal qualité.

## Ce qu'il reste à faire
Étape 2 : construire un dashboard HTML moderne, ajouter des filtres et du drill-down. Étape 3 : alertes explicables + stress tests pédagogiques. Étape 4 : Power BI, portfolio GitHub et post LinkedIn.
