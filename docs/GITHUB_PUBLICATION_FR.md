# Mise en ligne GitHub et démonstration publique

## A. Vérifications dans VS Code

```bash
python3 -m src.generate
python3 run.py --as-of 2026-10-31
python3 export_powerbi.py
python3 build_dashboard.py
python3 -m unittest discover -s tests -v
open dashboard/index.html
```

Vérifier l'affichage des trois pages, les filtres, le bouton « Détails », l'export d'alertes et les scénarios. Toutes les données sont **fictives**.

## B. Créer le dépôt

1. Ouvrir GitHub et créer un dépôt public `credit-insurance-risk-monitor`, **sans** nouveau README/.gitignore (ils sont déjà dans votre dossier).
2. Dans VS Code, ouvrir un terminal à la racine du projet (où se trouve `run.py`).
3. Exécuter une seule fois (remplacer `VOTRE_COMPTE` par votre identifiant GitHub) :

```bash
git init
git branch -M main
git add .
git status
git commit -m "Build explainable trade credit insurance risk monitor"
git remote add origin https://github.com/VOTRE_COMPTE/credit-insurance-risk-monitor.git
git push -u origin main
```

Si Git existe déjà ou si `origin` est configuré, **ne pas réinitialiser ni remplacer le remote à l'aveugle** : utiliser `git status`, `git remote -v`, puis adapter les commandes. GitHub peut demander une authentification dans le navigateur ou un jeton ; ne jamais coller un mot de passe ou token dans ChatGPT.

## C. Activer la démonstration GitHub Pages

Dans le dépôt : Settings → Pages → Build and deployment → **GitHub Actions**. La procédure `.github/workflows/pages.yml` régénère les données synthétiques et publie le dossier `dashboard/`.

L'adresse GitHub Pages est généralement `https://VOTRE_COMPTE.github.io/credit-insurance-risk-monitor/`, à vérifier dans Settings → Pages après la réussite du déploiement. Elle n'existe pas avant la publication.

## D. Captures et présentation

Le README affiche les captures de `assets/`. Une fois le projet ouvert sur votre Mac, vérifier que les captures représentent bien les pages et les paramètres indiqués.

Pour LinkedIn : préparer une vidéo courte ou 3 captures (Overview → Early Warning → Stress Lab), puis publier uniquement lorsque le dépôt et la démonstration publique sont accessibles.

## Protection des données

Ne publier que les CSV fictifs générés localement et les artefacts de démo. Ne pas ajouter d'identifiants, d'API keys, de bases métier réelles, de fichiers confidentiels ou de tokens.
