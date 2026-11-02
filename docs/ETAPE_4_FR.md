# Étape 4 — Stress Scenario Lab (simulation pédagogique)

## Installation sur votre projet existant

1. Télécharger `Credit_Insurance_Risk_Monitor_Etape_4_Ajouts.zip`.
2. Dans **le dossier racine du projet** déjà ouvert dans VS Code, exécuter :

```bash
unzip -o ~/Downloads/Credit_Insurance_Risk_Monitor_Etape_4_Ajouts.zip -d .
python3 build_dashboard.py
python3 -m unittest discover -s tests -v
open dashboard/index.html
```

La commande `unzip -o` remplace `build_dashboard.py` et `dashboard/template.html`,
mais **conserve vos données originales**, votre dossier `outputs`, `run.py` et
vos modules des étapes 1–3. La page autonome générée s'appelle `dashboard/index.html`.

## Démonstration

- Cliquer sur **Stress Scenarios** dans la barre latérale.
- Sans choc (0 jour, 0 %), les écarts par rapport à la base doivent tous être nuls.
- Choisir **+30 jours** et **−20 % des limites**.
- Observer les écarts des retards >30 jours, dépassements, alertes critiques et taux d'utilisation.
- Sélectionner **Automobile**, puis revenir à **Tous les secteurs**.
- Cliquer sur **Exporter le scénario (CSV)**.
- Cliquer sur Executive Overview et Early Warning Center pour vérifier que les deux pages précédentes fonctionnent.

## Méthodologie

Les 30 combinaisons sont calculées par Python à la construction du dashboard (5 décalages d'échéance × 6 réductions uniformes des limites) :

- On **ne change ni les montants facturés, ni les paiements déjà réalisés, ni le montant restant dû**.
- L'hypothèse d'augmentation du retard **déplace artificiellement les échéances de factures impayées vers le passé** de 0, 15, 30, 45 ou 60 jours. C'est un choc *statique* sur le vieillissement du portefeuille, **pas une projection temporelle ou un changement juridique d'échéance**.
- L'hypothèse de réduction des limites applique une décote uniforme de 0, 10, 20, 30, 40 ou 50 % aux montants approuvés dans la simulation, **sans prétendre que la couverture d'assurance est effectivement réduite**.
- L'encours restant dû ne change pas. Le dépassement est recalculé comme somme des `max(encours_par_limite − limite_scenario, 0)`.
- Les retards >30 jours correspondent aux montants impayés avec jours de retard *après choc* supérieurs à 30.
- Les alertes sont **réévaluées par la même fonction `src.alerts.build_alerts` que l'étape 3**.
- La page navigateur consomme les résultats pré-calculés : elle ne réimplémente pas les règles en JavaScript.

L'ensemble est **pédagogique et entièrement synthétique** ; il ne permet pas de déduire une PD, une LGD, un sinistre, une nouvelle capacité de couverture réelle, ni une perte attendue.

## Réponses possibles à un recruteur

**Pourquoi cette simulation ?** Pour montrer la sensibilité de l'exposition et des alertes à des hypothèses explicites, aider à identifier les limites dont la surveillance doit être renforcée.

**Pourquoi des règles plutôt qu'un modèle de machine learning ?** Parce que le périmètre disponible ne contient pas de cible de défaut observée ni de données réelles permettant de valider un modèle prédictif.

**Quelle est la différence entre une simulation et une prévision ?** La simulation déplace des hypothèses sur un cliché de données figé ; une prévision demanderait une dynamique des paiements, des comportements de clients, des dates et des paramètres validés.
