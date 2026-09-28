# Journal de bord — Sprint 3 CISIA · InduSense 4.0

> **Livrable certifiant** : prouve, module par module, *ce que j'ai fait · ma preuve · la compétence visée · une difficulté*. Sert d'antisèche pour l'oral (C1→C9), à raconter en **contexte → problème → choix → preuve → limite**.

**Règles de remplissage**
- **Une preuve** = une commande qui répond, un résultat chiffré, un fichier produit ou une capture (rangée dans `preuves/`, numérotée par module).
- **Aide IA** : noter l'aide reçue, séparer *fait observé · hypothèse · correctif · preuve*, et savoir réexpliquer chaque commande sans aide.
- **Jamais** de secret ni de donnée nominative.
- **Dates** : les dates du modèle (cohorte précédente, J1 = 24/08) sont remplacées par mes dates réelles au fil des modules.
- À relire : [notice de préparation](docs/notice_preparation_et_controles_sprint3.md) · [mémo métriques](docs/memo_metriques_sans_confusion.md).

---

## Mes entrées

### Préparation — §0.1 à 0.4 (avant module 23)

- Ce que j'ai fait : clone du dépôt `CISIA_24082026_Parcours`, création de la branche personnelle `ismael-sall`, contrôle d'entrée du poste (§0.2)
- Ma preuve : `FORMATION/JALON_ACTUEL.md` → `# Jalon actuel : 00-reconstruction-fin-sprint2` · `git branch --show-current` → `ismael-sall` · contrôle express : Python 3.14.7 (hors venv projet), uv 0.12.5, Git 2.55.0, VS Code trouvé, WSL VERSION 2, Docker 29.7.2 (moteur arrêté, non bloquant avant J3)
- Compétence(s) : — (logistique, pas encore de module noté)
- Aide IA reçue : Claude Code a exécuté le clone, la création de branche et la commande de contrôle express à ma demande, puis expliqué le résultat (notamment pourquoi `docker --version` répond alors que le moteur Docker est arrêté)
- Difficulté / question : Docker Desktop pas démarré — à faire avant le module 27 (J3)

### Hors TP — rangement du dépôt (28/09/2026)

> Actions techniques qui ne font pas partie d'un module noté. Tracées à part pour ne pas les confondre avec le travail M23.

**Action 1 — Commit de sauvegarde avant changement de jalon**
- Commande : `git add -A` puis `git commit -m "travail avant nouveau jalon"` → commit `0ea6620`
- Pourquoi : le [README FORMATION](FORMATION/README.md) impose, au début de chaque demi-journée, d'enregistrer son travail avant de récupérer un nouveau jalon. Sans ce commit, la fusion du jalon pourrait entrer en conflit avec des fichiers non enregistrés, ou les écraser.
- Résultat : 14 fichiers commités, `journal_de_bord.md` **et** 13 supports de formation qui se trouvaient dans `data/Docs/`.
- Commentaire : ces 13 fichiers n'étaient pas prévus. `git add -A` ajoute **tout** ce qui n'est pas ignoré par `.gitignore`, sans distinction. Ce n'est pas grave (rien de secret, c'est de la documentation), mais c'est une erreur de méthode.
- À retenir : **toujours relire `git status` avant `git add -A`**, pour savoir exactement ce qu'on va commiter.

**Action 2 — Déplacement de `data/Docs/` vers `docs/` à la racine**
- Commande : `git mv data/Docs docs` puis commit `c4812d9` (« docs: deplacer data/Docs vers docs a la racine »)
- Pourquoi : le dossier `data/` doit contenir **les données du projet** (Gold dataset, etc.), pas les supports de cours. Une documentation se place par convention dans `docs/` à la racine. Mélanger les deux brouille la lecture du dépôt, et plus tard le versioning DVC (M24), qui cible les données.
- Pourquoi `git mv` plutôt que couper/coller : Git enregistre un **renommage** (`rename ... (100%)`) et non « suppression + création ». L'historique de chaque fichier reste donc suivi.
- Vérification faite avant : recherche de `data/Docs` dans tout le dépôt → **aucune référence**, donc aucun lien cassé.
- Résultat : 13 fichiers renommés, contenu identique (`0 insertions, 0 deletions`), arbre de travail propre.
- Aide IA reçue : Claude Code a exécuté le commit, la recherche de références et le `git mv`.

### J1 — lun. 28/09/2026 *(date prévue dans le modèle : 24/08)*

**Module 23 — Refactoring & structure projet** · *C6* · *(en cours)*

> **Objectif du module** : sortir la logique du notebook vers un **package Python** (`src/indusense`) importable, testé et **sans fuite temporelle**.
> **Sources suivies** : [fiche jalon 01](FORMATION/JALONS/01-j1-matin-m23.md) · [pas-à-pas R2, §23](docs/pas_a_pas_apprenant_sprint3_AELION_20260928_R2.md) · [guide multiplateforme §5](FORMATION/GUIDE_MULTIPLATEFORME_APPRENANT.md).

**Avancement**
- [x] Étape 0a — récupération du jalon 01
- [x] Étape 0b — vérification du jalon 01
- [x] Point 1 — contrôle du squelette
- [x] TP 1 — structure & `pyproject.toml` (lecture, sans modification)
- [ ] TP 2 — anti-fuite : `shift(1)` avant `rolling` dans `features/temporal.py`
- [ ] TP 3 — normalisation des IDs machine (`normalize_machine_id`)
- [ ] Extension (facultative d'après le pas-à-pas R2) : extraire `clean_sensor_data` dans `features/cleaning.py`
- [ ] Preuve finale + commit M23 + QCM J1 (questions 1-3)

**Étape 0a — Récupérer le jalon 01**
- Commande : `powershell -ExecutionPolicy Bypass -File .\scripts\formation\mettre_a_niveau.ps1 -Jalon 01`
- Pourquoi : chaque demi-journée démarre sur un **jalon officiel** (branche publique `jalon/01`), pour que tout le groupe parte du même état de code.
- Ce que fait le script : (1) il crée une **branche de secours** pointant sur mon état actuel, (2) il fait un `git pull` de `jalon/01` dans ma branche `ismael-sall`. Il ne supprime ni ne réécrit aucun commit.
- Résultat : branche de secours `sauvegarde/ismael-sall/20260928-112927` · fusion `ort` **sans conflit** · seul `FORMATION/JALON_ACTUEL.md` a changé (passage de `00-reconstruction-fin-sprint2` à `01-j1-matin-m23`).
- Commentaire : le jalon 01 ne livre pas de nouveau code. Il marque le point de départ du M23, et le travail consiste à **comprendre et prouver** ce qui existe déjà.

**Étape 0b — Vérifier le jalon reçu**
- Commande : `powershell -ExecutionPolicy Bypass -File .\scripts\formation\verifier_jalon.ps1 -Jalon 01`
- Pourquoi : s'assurer que l'état reçu **fonctionne** avant de travailler dessus. Si quelque chose casse plus tard, je saurai que ce n'était pas cassé au départ.
- Ce que fait le script :
  1. crée l'environnement virtuel `.venv` (il n'existait pas) avec **Python 3.13.15** ;
  2. installe **48 paquets** aux versions exactes de `uv.lock` (pandas 3.0.4, scikit-learn 1.9.0, pytest 9.1.1, ruff 0.15.20…), dont le package du projet `indusense-sprint3-starter==0.1.0` ;
  3. lance les tests → **`12 passed in 7.88s`** ;
  4. lance le linter → **`All checks passed!`** ;
  5. conclut : **`Jalon verifie : jalon/01`**.
- Commentaire : 12 tests verts et un linter propre signifient que le socle est sain. Toute régression ultérieure viendra de mes modifications.

**Point 1 — Contrôle du squelette** *(pas-à-pas R2, « Montrer le squelette »)*

| Commande | À quoi elle sert | Résultat obtenu | Ce que ça prouve |
|---|---|---|---|
| `uv --version` | Vérifier que le gestionnaire de paquets est installé | `uv 0.12.5` | L'outil est disponible |
| `uv sync --frozen --extra dev` | Installer les dépendances **exactement** comme dans `uv.lock` ; `--frozen` interdit de modifier le lock ; `--extra dev` ajoute les outils de dev (pytest, ruff, black, pre-commit) | `Checked 48 packages` | L'environnement est déjà conforme au lock : rien à installer ni à changer |
| `Test-Path .\pyproject.toml` | Le fichier qui **définit le package** (nom, version, Python requis, dépendances, commande `indusense`) doit exister | `True` | Le projet est un package installable |
| `Test-Path .\uv.lock` | Le fichier qui **verrouille les versions** exactes doit exister | `True` | Environnement reproductible sur tous les postes |
| `uv run python -c "import indusense; print(indusense.__file__)"` | Importer le package et afficher **d'où** il est chargé | `C:\Users\issal\CISIA_24082026_Parcours\src\indusense\__init__.py` | Le package est installé **et** c'est bien la copie de `src/` qui est utilisée |
| `uv run python --version` | Contrôler la version de Python du `.venv` | `Python 3.13.15` | Conforme à l'exigence `requires-python = ">=3.13,<3.14"` |

- **Pourquoi importer `indusense` ?**
  - Avec le **layout `src/`**, le code n'est pas importable juste parce qu'on se trouve à la racine du projet : il faut qu'il soit **installé** (ici en mode éditable par `uv sync`).
  - Si l'import réussit, l'installation et la configuration du package sont correctes.
  - Le chemin affiché (`__file__`) garantit qu'on exécute **le code qu'on modifie**, et non une autre copie (ancien clone, vieux `site-packages`).
  - Conséquence : les tests tournent contre le package **installé**, comme en production. Une erreur de packaging (fichier oublié, mauvaise config) est donc détectée tôt.
  - C'est un prérequis pour tout le reste : tests, CLI `indusense` et, plus tard, l'API font tous `from indusense... import ...`.
  - *Ma reformulation :* …
  - *Nuance vue au TP 1 :* `pyproject.toml` contient `pythonpath = ["src"]` dans `[tool.pytest.ini_options]`, donc **pytest** ajoute lui-même `src/` au chemin Python. Les tests trouveraient le code même sans installation. C'est la commande `import indusense` hors pytest, et la CLI `indusense`, qui prouvent l'installation.

**TP 1 — Structure du projet & `pyproject.toml`** *(lecture seule, aucun fichier modifié)*

*Classement de ce qui existe :*

| Couche | Emplacement | Contenu observé | Rôle |
|---|---|---|---|
| **data** | `src/indusense/data/loaders.py` | `normalize_machine_id`, `load_temperature`, `load_pressure`, `load_incidents`, `load_machines`, `build_dataset`, `add_machine_criticality` | Lire les fichiers bruts, harmoniser les IDs machine, assembler le dataset |
| **features** | `src/indusense/features/temporal.py` | `add_temporal_features` | Créer les variables temporelles (lags, moyennes glissantes) **sans fuite** → TP 2 |
| **models** | `src/indusense/models/tabular.py` | `select_features`, `train_model`, `predict_proba`, `save_model`, `load_model` | Entraîner, prédire, sauvegarder / recharger le Random Forest |
| **cli** | `src/indusense/cli.py` | commandes `check-data`, `build-gold`, `train`, `predict` + `main()` | Interface en ligne de commande (Typer) qui enchaîne les couches ci-dessus |
| **config** | `src/indusense/config.py` | classe `Settings` (pydantic-settings) | Chemins et paramètres centralisés, surchargeables par variables d'environnement |
| **api** | *absent* | — | Normal : l'API FastAPI arrive au **M25** (jalon 03) |
| tests | `tests/` | `test_package.py`, `test_loaders.py`, `test_temporal.py` | Vérifier l'import du package, les loaders et l'anti-fuite |
| données | `data/raw/` · `data/sample/` · `data/gold/` | CSV / TSV / SQL bruts · petit échantillon · `gold_dataset.csv` | Entrées du pipeline : brut → Gold (niveau « propre, prêt à l'usage ») |
| artefacts | `artifacts/models/` | `rf.joblib` + `model_metadata.json` | Modèle entraîné et sa fiche d'identité (features, seuils…) |

- Commentaire : la séparation **data → features → models → cli** suit le flux réel : on charge, on transforme, on entraîne/prédit, on expose. Chaque couche est testable seule. C'est l'intérêt du refactoring par rapport au notebook, où tout est mélangé dans des cellules.
- Commentaire : le code (`src/`), les données (`data/`) et les résultats (`artifacts/`) sont **séparés**. Au M24, DVC versionnera `data/` et `artifacts/` à part, Git gardant le code.

*`pyproject.toml` bloc par bloc :*

| Bloc | Valeur clé | Explication |
|---|---|---|
| `[build-system]` | `hatchling` | Outil qui **construit** le package (le transforme en « wheel » installable) |
| `[project]` | `name = "indusense-sprint3-starter"` · `version = "0.1.0"` | Identité du package distribué (≠ nom importé `indusense`) |
| `requires-python` | `">=3.13,<3.14"` | Seules les versions 3.13.x sont garanties → d'où le contrôle `python --version` |
| `dependencies` | pandas, numpy, scikit-learn, joblib, pydantic-settings, typer, loguru | Ce dont le code a besoin **pour tourner** (runtime). Bornes minimales (`>=`) : `uv.lock` fige les versions exactes |
| `[project.optional-dependencies] dev` | pytest, ruff, black, pre-commit | Outils de **développement** seulement, installés avec `--extra dev`. Ils ne partent pas en production |
| `[project.scripts]` | `indusense = "indusense.cli:main"` | Crée la commande `indusense` qui appelle la fonction `main()` de `cli.py` |
| `[tool.hatch.build.targets.wheel]` | `packages = ["src/indusense"]` | Dit à hatchling où est le code → c'est ce qui rend le **layout `src/`** installable |
| `[tool.ruff]` / `[tool.ruff.lint]` | `line-length = 100` · `select = ["E","F","I","UP","B"]` · `ignore = ["B008"]` | Règles du linter : erreurs de style (E), bugs (F), ordre des imports (I), syntaxe moderne (UP), pièges courants (B). B008 (« appel de fonction dans une valeur par défaut ») est ignoré : aucun cas dans le code actuel, mais c'est le style habituel de Typer (`typer.Option(...)`) et de FastAPI (`Depends(...)`, M25) — *hypothèse, raison non documentée dans le dépôt* |
| `[tool.black]` | `line-length = 100` | Formateur automatique, même limite que ruff pour qu'ils ne se contredisent pas |
| `[tool.pytest.ini_options]` | `testpaths = ["tests"]` · `pythonpath = ["src"]` | pytest ne cherche les tests que dans `tests/` et ajoute `src/` au chemin |

*Audit du contrat (sans modification) :*
- `Select-String -Path .\pyproject.toml -Pattern 'requires-python','optional-dependencies','indusense\s*='` → lignes **35** (`requires-python = ">=3.13,<3.14"`), **64** (`[project.optional-dependencies]`), **85** (`indusense = "indusense.cli:main"`) : les trois éléments du contrat sont présents.
- `git diff -- pyproject.toml uv.lock` → **aucune sortie** (code retour 0) : ni le manifeste ni le verrou n'ont été modifiés. L'environnement reste reproductible.

**Compétence(s)** : C6 (implémenter / intégrer les briques) · lien C3 (features sans fuite, au TP 2)

**Aide IA reçue** : Claude Code a lancé la mise à niveau, la vérification du jalon et les commandes de contrôle du squelette. Il a ensuite expliqué le rôle de chaque commande, le sens de `--frozen` et l'intérêt de l'import de `indusense`. **Je dois savoir réexpliquer chaque ligne du tableau ci-dessus sans aide.**

**Difficultés / questions**
- Le jalon 01 a été lancé **sans attendre le signal du formateur**. C'est réversible via la branche `sauvegarde/ismael-sall/20260928-112927`, et sans impact ici puisque le jalon ne change que le marqueur.
- **Incohérence entre supports** : la fiche jalon 01 demande d'extraire `clean_sensor_data`, alors que le pas-à-pas R2 la classe en extension facultative. → À confirmer avec le formateur.
- La fiche TD 23, citée par le pas-à-pas pour le code de `cleaning.py`, **n'est pas dans le dépôt**. → À demander.

**Module 24 — CI/CD, tests & versioning** · *C6*
- Ce que j'ai fait : …
- Ma preuve : … (CI verte · `gitleaks` bloque · `dvc status`)
- Compétence(s) : C6
- Difficulté / question : …

### J2 — mar. 25/08

**Module 25 — API REST (FastAPI)** · *C7*
- Ce que j'ai fait : …
- Ma preuve : … (`/health` 200 · `/predict-tabular` 200 · `/docs`)
- Compétence(s) : C7 (architecture / intégration) · C6
- Difficulté / question : …

**Module 26 — Sécurité & menaces** · *C2*
- Ce que j'ai fait : …
- Ma preuve : … (401 sans clé · 429 rate limit · 413 payload)
- Compétence(s) : C2 (risques) · C6
- Difficulté / question : …

### J3 — mer. 26/08

**Module 27 — Conteneurisation (Docker)** · *C6*
- Ce que j'ai fait : … / Ma preuve : … (`docker build` · image non-root) / Compétence(s) : C6 / Difficulté : …

**Module 28 — Déploiement local & compose** · *C6 · C7*
- Ce que j'ai fait : … / Ma preuve : … (`docker compose up -d --wait` · api + db *healthy* · 3 smoke tests verts) / Compétence(s) : C6, C7 / Difficulté : …

### J4 — mar. 01/09

*(Matin : M29 puis M30. Après-midi : M31-M32 en **passe 1 sur `tp_payguard`**.)*

**Module 29 — Orchestration Prefect (design)** · *C6 · C7*
- Ce que j'ai fait : … / Ma preuve : … (design du flow `ingest→feature→predict→store` + flow « hello ») / Compétence(s) : C6, C7 / Difficulté : …

**Module 30 — Implémentation du flow** · *C6*
- Ce que j'ai fait : … / Ma preuve : … (2 runs → 0 doublon, `count(*)` stable) / Compétence(s) : C6 / Difficulté : …

### J5 — mer. 02/09

*(Matin : M31-M32, **passe 2 InduSense dans le miroir officiel `tp_drift_indusense`**. Après-midi : M33 puis M34 et clôture du bloc technique.)*

**Module 31 — Data drift & métriques** · *C3 · C8* · travail réparti entre J4 après-midi et J5 matin
- Ce que j'ai fait : … / Ma preuve nominale J5 : … (miroir `tp_drift_indusense` : fenêtre 2 +8 °C → PSI température **≈ 6,845** · fenêtre 3 → rappel **≈ 0,053** avec PSI muet · suite **11 passed**) / Extension éventuelle, à étiqueter : … (`docs/TP_drift.md` : 6,834 / 0,092 / 8 tests ; simulation : ≈ 3,32) / Compétence(s) : C3, C8 / Difficulté : …

**Module 32 — Drift report + alerting (JSON + SQLite)** · *C3 · C8* · travail réparti entre J4 après-midi et J5 matin
- Ce que j'ai fait : … / Ma preuve : … (`reports\drift_report_f2.json` lisible · une ligne SQLite `drift_events` · saine→0 · +8 °C→1 · relance→0 · **11 passed**, sans Evidently) / Compétence(s) : C3, C8 / Difficulté : …

**Module 33 — Observabilité API (Prometheus)** · *C6 · C8*
- Ce que j'ai fait : … / Ma preuve : … (`/metrics` scrapeable · cible `indusense-api` **UP** au scrape · requête **PromQL p95** de latence + taux 5xx · 5 SLI/SLO) / Compétence(s) : C6, C8 / Difficulté : …

**Module 34 — Dashboards & runbooks (Grafana)** · *C6 · C8*
- Ce que j'ai fait : … / Ma preuve : … (dashboard v1 exporté **JSON** importable ≥ 3 panels · 2 alertes Grafana avec `for:` · **runbook joué** jusqu'à résolution) / Compétence(s) : C6, C8 / Difficulté : …

### J6 — jeu. 03/09 — Journée Game Day « Opération lundi matin »

**Game Day — réparer un dépôt cassé, prouver C8/C9** · *C8 · C9*
- Ce que j'ai fait : … (dépôt `J6-gameday` cloné · pannes triées · réparations menées, ex. n/14 pannes)
- Ma preuve : … (CI de nouveau verte · `docker compose up -d --wait` *healthy* · `/health` + `/ready` 200 · dashboard qui remonte)
- Post-mortem (ce qui a cassé, pourquoi, comment l'éviter) : …
- Pitch (la réparation que j'ai expliquée à mon binôme/au groupe) : …
- Compétence(s) : C8 (mesurer/maintenir), C9 (amélioration continue)
- Difficulté / question : …

---

## Bilan de fin de sprint (à relire avant la soutenance)

- **Mon récit projet** (3 phrases) : du **Gold dataset** (S1) au **modèle** (S2), **industrialisé** et **surveillé** (S3)…
- **Mes 3 plus belles preuves** : 1) … 2) … 3) …
- **Mes 2 limites assumées** (le jury adore) : … / …
- **Ce que je ferais ensuite** (C9) : sur dérive, **ouvrir une investigation documentée** (jamais de réentraînement aveugle) → si les **labels** et les **critères** le justifient, entraîner un **candidat**, comparer **champion/challenger**, passer les **gates de validation**, puis **décider humainement** du déploiement · …

*Journal de bord — Sprint 3 CISIA · InduSense 4.0 · AELION. Tiens-le à jour : c'est ta meilleure préparation à l'oral.*
