# Étape 2 : Executive Risk Overview (tableau de bord autonome)

## Objectif
Transformer les fichiers de l'étape 1 en un tableau de bord professionnel que l'on peut ouvrir dans un navigateur, **sans installer de bibliothèque**.

## Installation sur Mac, dans le dossier du projet déjà ouvert dans VS Code
1. Décompresser l'archive `Credit_Insurance_Risk_Monitor_Etape_2_Ajouts.zip`.
2. Copier son contenu (`build_dashboard.py`, dossier `dashboard`, nouveau fichier dans `docs` et `tests`) dans **le dossier `credit-insurance-risk-monitor` déjà existant**, sans supprimer vos anciens fichiers. Autoriser la fusion des dossiers, pas le remplacement du projet entier.
3. Dans le terminal VS Code, depuis le dossier racine du projet :

```bash
python3 run.py --as-of 2026-10-31
python3 build_dashboard.py
open dashboard/index.html
```

Si la commande `open` n'est pas disponible, double-cliquer sur `dashboard/index.html` dans le Finder.

## Ce qui doit fonctionner
- 4 indicateurs recalculés en fonction des filtres.
- Filtres secteur, région, profil de risque et statut de la limite.
- Répartition par ancienneté des factures (tranches mutuellement exclusives).
- Exposition par secteur.
- Classement des dix acheteurs les plus exposés et export CSV.
- Informations de qualité des données.

## Tester
```bash
python3 -m unittest discover -s tests -v
```

## Comment le tableau de bord est produit
- `run.py` construit `outputs/*.csv` et `outputs/kpis.json` à partir de SQLite.
- `build_dashboard.py` vérifie leur cohérence et insère leurs données dans `dashboard/template.html`.
- Le fichier généré `dashboard/index.html` est autonome : aucune API, aucun serveur et aucune connexion Internet ne sont nécessaires.
- Si vous changez la date d'arrêté, exécutez à nouveau `run.py` **puis** `build_dashboard.py`.

## Limites méthodologiques
- Données de démonstration synthétiques, pas de données réelles d'assureur.
- Le taux de retards est volontairement élevé dans cette simulation : ne pas le présenter comme un taux du marché.
- Les catégories de risque de l'acheteur sont données par le générateur ; ce ne sont pas des scores estimés ni validés.
- Le statut de la limite est un attribut du jeu actuel, sans historique de changement de statut.
- Cette étape ne comporte pas encore l'alerte explicable ni les stress scenarios.

## Vérification visuelle pour la publication
Pour vos futures captures LinkedIn : afficher la page avec les filtres réinitialisés, zoom navigateur à 80–100 %, et conserver le badge « SIMULATED DATA ». Ne pas publier de résultats comme s'ils représentaient le marché marocain.
