# Journal de bord — Sprint 3 CISIA · InduSense 4.0

> **Livrable certifiant** : prouve, module par module, *ce que j'ai fait · ma preuve · la compétence visée · une difficulté*. Sert d'antisèche pour l'oral (C1→C9), à raconter en **contexte → problème → choix → preuve → limite**.

**Règles de remplissage**
- **Une preuve** = une commande qui répond, un résultat chiffré, un fichier produit ou une capture, rangée dans `preuves/` sous la forme `<module>_<étape>_<quoi>.<ext>` (ex. `23_tp2_pytest_temporal.txt`, `24_ci_verte.png`) et liée depuis l'entrée du module (📎).
- **Sorties terminal** : enregistrées en `.txt` (en-tête : date, branche, commit, puis `PS> commande` et sa sortie exacte). **Captures** : seulement pour ce qui est visuel (page web, CI, dashboard), en vérifiant qu'aucun secret n'apparaît.
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
- [x] TP 2 — anti-fuite : `shift(1)` avant `rolling` dans `features/temporal.py`
- [x] TP 3 — normalisation des IDs machine (`normalize_machine_id`)
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

📎 **Preuve brute** : [preuves/23_p1_squelette.txt](preuves/23_p1_squelette.txt), sorties exactes des commandes ci-dessous + `verifier_jalon.ps1`, rejouées le 28/09/2026 à 12:05 sur le commit `a2aceba` (commandes en lecture seule, résultats identiques à la première exécution).

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
  - *Ma reformulation :* L'import d'indusense permet de s'assurer du bon fonctionnement des tests, de la CLI et de l'API. Le chemin affiché permet d'identifier l'emplacement du code.
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

*Audit du contrat (sans modification) :* 📎 [preuves/23_tp1_audit_pyproject.txt](preuves/23_tp1_audit_pyproject.txt)
- `Select-String -Path .\pyproject.toml -Pattern 'requires-python','optional-dependencies','indusense\s*='` → lignes **35** (`requires-python = ">=3.13,<3.14"`), **64** (`[project.optional-dependencies]`), **85** (`indusense = "indusense.cli:main"`) : les trois éléments du contrat sont présents.
- `git diff -- pyproject.toml uv.lock` → **aucune sortie** (code retour 0) : ni le manifeste ni le verrou n'ont été modifiés. L'environnement reste reproductible.

**TP 2 — Anti-fuite : `shift(1)` avant `rolling`** *(pas-à-pas R2, lignes 567-575 dans VS Code · lien C3)*

📎 **Preuve brute** : [preuves/23_tp2_pytest_temporal.txt](preuves/23_tp2_pytest_temporal.txt) (test en mode verbeux + démonstration avec / sans `shift(1)` + code de la démo)

*Rappel — fuite de données :* une information du **futur** (ou du **présent** qu'on cherche à prédire) entre dans les features d'entraînement. Le modèle « triche » : excellent score en test, mauvais en production, où cette information n'existe pas encore. **Un score trop beau doit inquiéter.**

*Lecture de [temporal.py](src/indusense/features/temporal.py), fonction `add_temporal_features` :*

| Ligne | Code | Rôle | Pourquoi c'est important |
|---|---|---|---|
| [44](src/indusense/features/temporal.py#L44) | `raise ValueError("Colonnes manquantes : …")` | Refuser un DataFrame incomplet | Échec **explicite** plutôt qu'un calcul silencieusement faux |
| [46](src/indusense/features/temporal.py#L46) | `df.sort_values([group_col, timestamp_col])` | Trier par **machine**, puis par **date** | `shift` et `rolling` travaillent sur l'**ordre des lignes**, pas sur les dates. Sans tri, « la ligne précédente » peut être une mesure future ou celle d'une autre machine |
| [54](src/indusense/features/temporal.py#L54) | `grouped.shift(lag)` | Lags 1, 3, 6 : valeur d'il y a 1, 3, 6 mesures | `groupby(machine)` évite qu'un lag « déborde » d'une machine sur la suivante |
| [59](src/indusense/features/temporal.py#L59) | `series.shift(1).rolling(window).mean()` | Moyenne glissante sur 3 ou 6 mesures | Le `shift(1)` **exclut la mesure courante** de la fenêtre : on ne moyenne que le passé strict |

*Pourquoi `shift(1)` **avant** `rolling` — démonstration (température 10, 20, 30, 40 ; fenêtre 2) :*

| Heure | Température | `lag1` | `roll2_mean` **avec** `shift(1)` (code du projet) | `rolling(2)` **sans** `shift(1)` |
|---|---|---|---|---|
| 00:00 | 10 | NaN | NaN | NaN |
| 01:00 | 20 | 10 | NaN | 15 |
| 02:00 | 30 | 20 | **15** = moyenne(10, 20) | **25** = moyenne(20, **30**) ← fuite |
| 03:00 | 40 | 30 | 25 | 35 |

- Sans `shift(1)`, la feature de 02:00 **contient la température de 02:00 elle-même**. Si on prédit une panne à partir de cette mesure, le modèle voit déjà une partie de la réponse.
- Avec `shift(1)`, la feature de 02:00 n'utilise que 00:00 et 01:00 : exactement ce qu'on connaîtra en production au moment de prédire.
- Contrepartie : les premières lignes de chaque machine valent `NaN` (pas assez d'historique). C'est normal et **honnête** ; il faudra les gérer (suppression ou imputation) avant l'entraînement.
- Démo faite avec un script **jetable hors dépôt** : aucun fichier du projet modifié.

*Les 3 tests de [test_temporal.py](tests/test_temporal.py) :*

| Test | Ce qu'il vérifie | Assertion clé |
|---|---|---|
| [`test_temporal_features_do_not_use_current_value`](tests/test_temporal.py#L29) | **Anti-fuite** : la moyenne glissante n'utilise pas la valeur courante | `roll2_mean` à la 3ᵉ ligne `== 15.0` (et non 25.0) · `lag1` de la 1ʳᵉ ligne est `NaN` |
| [`test_temporal_features_sort_by_machine_and_time`](tests/test_temporal.py#L50) | **Tri** : lignes fournies en désordre, 2 machines mélangées | Pour MACH-01, le `lag1` de 01:00 `== 10.0` (sa propre mesure de 00:00, pas celle de MACH-02) |
| [`test_temporal_features_missing_column_raises`](tests/test_temporal.py#L72) | **Robustesse** : colonne `temperature` absente | Lève bien `ValueError` |

- Commande : `uv run pytest tests/test_temporal.py -v` (`-v` au lieu de `-q` pour voir le nom de chaque test dans la preuve)
- Résultat : **`3 passed in 1.58s`**, 0 échec, conforme au résultat attendu du pas-à-pas.
- Ce que ça prouve : la valeur 15.0 attendue par le test est **exactement** celle de la démo avec `shift(1)`. Si quelqu'un retirait le `shift(1)`, la valeur passerait à 25.0 et le test échouerait : le test **protège** contre la régression.
- « Compléter » le test : non nécessaire, les 3 cas demandés par le pas-à-pas (anti-fuite, tri temporel, colonne manquante) sont déjà couverts.
- Hors périmètre : le **split train/test temporel** (entraîner sur le passé, tester sur le futur) est un autre mécanisme anti-fuite, traité dans l'exercice avancé.
- *Ma reformulation :* La fuite de données consiste à utiliser, pour entraîner le modèle, des informations qui ne sont pas encore connues au moment de la prédiction. Le `shift(1)` permet de n'utiliser que les informations connues avant ce moment.

**TP 3 — Normalisation des IDs machine** *(pas-à-pas R2, « TP 3 — Normalisation des machines »)*

📎 **Preuve brute** : [preuves/23_tp3_normalize_machine_id.txt](preuves/23_tp3_normalize_machine_id.txt) (ma prédiction, la sortie réelle, les 6 tests, un cas limite et un cas d'échec)

*Le problème :* les fichiers sources n'écrivent pas l'ID machine de la même façon (`MACH-01`, `MACH_01`, `M-06`, `M-2`…). Pour pandas, `MACH-01` et `MACH_01` sont **deux machines différentes**. Les jointures entre température, pression et incidents rateraient alors des lignes, en silence.

*La solution — [loaders.py:46-56](src/indusense/data/loaders.py#L46-L56), `normalize_machine_id` :*

| Étape | Code | Effet |
|---|---|---|
| 1. Trouver les chiffres | `_DIGITS.search(str(raw))` avec `_DIGITS = re.compile(r"(\d+)")` ([ligne 29](src/indusense/data/loaders.py#L29)) | Récupère la **première suite de chiffres** ; tout le reste (`MACH`, `M`, `-`, `_`) est ignoré |
| 2. Refuser si aucun chiffre | `raise ValueError("machine_id sans numero : …")` | **Fail fast** : un ID inutilisable est bloqué tout de suite au lieu de produire un faux identifiant |
| 3a. Convertir en nombre | `int(match.group(1))` | `"06"` → `6` (retire les zéros en tête) |
| 3b. Écrire sur 2 chiffres | `:02d` | `6` → `"06"`, `2` → `"02"` (complète avec un `0`, **minimum** 2 chiffres) |
| 3c. Reconstruire | `f"MACH-{…}"` | Préfixe **unique** `MACH-` → format standard `MACH-NN` |

*Prédire puis exécuter :*

| Entrée | Ma prédiction (avant exécution) | Sortie réelle | Verdict |
|---|---|---|---|
| `"MACH-01"` | `MACH-01` *(exemple guidé)* | `MACH-01` | ✅ |
| `"MACH_01"` | `01` → corrigé en `MACH-01` (j'avais oublié le préfixe) | `MACH-01` | ✅ |
| `"M-06"` | `MACHINE-06` → corrigé en `MACH-06` (le préfixe est toujours `MACH-`, pas `MACHINE-`) | `MACH-06` | ✅ |
| `"M-2"` | `MACH-02` | `MACH-02` | ✅ du premier coup |

- Commande : `uv run python -c "…print([n(raw) for raw in ids])"` → **`['MACH-01', 'MACH-01', 'MACH-06', 'MACH-02']`**, exactement le résultat attendu par le pas-à-pas et ma prédiction finale.
- Ce que j'ai appris en me trompant : la fonction ne garde **que les chiffres**, puis **reconstruit tout le reste** avec un préfixe fixe. Deux écritures du même ID donnent donc la même sortie.

*Les tests de [test_loaders.py](tests/test_loaders.py) :*

| Test | Cas couverts | Résultat |
|---|---|---|
| [`test_normalize_machine_id_variants`](tests/test_loaders.py#L53) | 5 variantes via `@pytest.mark.parametrize` : `MACH-01`, `MACH_01`, `M-06`, `M-2`, **`M_07`** (un cas en plus de la consigne) | 5 PASSED |
| [`test_normalize_machine_id_without_number_raises`](tests/test_loaders.py#L62) | ID sans chiffre `"NOPE"` → doit lever `ValueError` | PASSED |

- Commande : `uv run pytest tests/test_loaders.py -v -k normalize_machine_id` (`-k` = ne lancer que les tests dont le nom contient `normalize_machine_id`)
- Résultat : **`6 passed, 2 deselected in 1.34s`**, 0 échec. Les 2 tests « deselected » sont les autres tests du fichier, volontairement écartés par `-k`.
- `parametrize` : **un seul** test écrit, exécuté **5 fois** avec des données différentes. Ajouter un nouveau format d'ID = ajouter une ligne, pas un nouveau test.

*Cas limite et cas d'échec (au-delà de la consigne) :*
- `"MACH-123"` → `MACH-123` : `:02d` impose **au moins** 2 chiffres, sans tronquer. Une 100ᵉ machine reste donc distincte.
- `"MACH-XX"` → `ValueError: machine_id sans numero : 'MACH-XX'` : le cas d'échec est bien bloqué. Le code retour 1 de cette commande est **attendu**.
- Limite repérée : seule la **première** suite de chiffres compte. `"LIGNE2-M05"` donnerait `MACH-02` et non `MACH-05`. *Hypothèse non testée, déduite de la lecture du code* : sans conséquence tant que les sources respectent les formats listés.
- *Ma reformulation :* La normalisation consiste à unifier le nommage des machines afin d'éviter que la même machine porte plusieurs noms différents.

**Prérequis Sprint 2 — Contrat I/O (exemple du cours)** *(pas-à-pas R2, « Ouvrir le Sprint 3 — scénario B » · lien C7)*

📎 Fichier analysé : [docs/CONTRAT_IO_EXEMPLE_FICTIF_J1.json](docs/CONTRAT_IO_EXEMPLE_FICTIF_J1.json) · 📎 Preuve : [preuves/23_contrat_io_machine_exemple.txt](preuves/23_contrat_io_machine_exemple.txt)

*Qu'est-ce que c'est ?* Un **contrat I/O** (entrée / sortie) : l'accord écrit entre le modèle (bientôt l'API, M25) et ceux qui l'appellent. Il fixe **ce qu'on envoie** (`request_schema`), **ce qu'on reçoit** (`response_schema`) et les **règles de validation** (types, bornes, champs obligatoires), au format standard JSON Schema.
- **Les schémas** sont la structure de référence, réutilisable au M25.
- **Les valeurs d'exemple** (`MACH-EXEMPLE`, seuil `0.65`, version `EXEMPLE-FICTIF-1`) sont **illustratives** : le fichier le déclare (`"example_only": true`, « ne décrit pas le seuil du dépôt commun et ne prouve aucune prédiction exécutée »). Je ne les cite donc **pas** comme des résultats réels.
- Source indiquée : « Repères du cours Sprint 2, module 22 ». Le fichier n'est cité par aucun autre document du dépôt.

*Requête (`request_schema`) :*

| Champ | Règle | Pourquoi |
|---|---|---|
| `machine_id` | texte non vide, obligatoire | Identifier la machine |
| `readings` | liste d'**au moins 7** mesures | Assez d'historique pour les features (voir ci-dessous) |
| `timestamp` | date ISO 8601 (`2026-09-01T08:00:00Z`) | Trier dans le temps, condition de l'anti-fuite (TP 2) |
| `temperature` | nombre entre **-20 et 200** | Rejeter une valeur physiquement absurde |
| `pressure_bar` | nombre **> 0** et ≤ 400 | Une pression nulle ou négative = capteur défaillant |
| `additionalProperties: false` | aucun champ en plus | Un champ mal orthographié est **refusé** au lieu d'être ignoré en silence |

- **Pourquoi 7 mesures minimum** *(ma déduction, non écrite dans le fichier)* : le modèle utilise `lag6` et `roll6_mean` ([model_metadata.json](artifacts/models/model_metadata.json)). Avec le `shift(1)` du TP 2, une moyenne sur 6 mesures passées exige **6 mesures d'avant + la mesure courante = 7**. En dessous, les features valent `NaN`. Le contrat est donc **cohérent** avec le code anti-fuite.

*Réponse (`response_schema`) :*

| Champ | Règle | Rôle |
|---|---|---|
| `proba_panne` | entre 0 et 1 | Probabilité de panne donnée par le modèle |
| `decision` | `"ok"` ou `"alerte"` uniquement (`enum`) | Décision métier lisible, sans valeur surprise |
| `threshold` | entre 0 et 1 | Seuil utilisé pour décider |
| `model_version` | texte non vide | **Traçabilité** : quel modèle a répondu |

- Règle de décision : `proba_panne ≥ threshold` → `"alerte"`, sinon `"ok"`. Exemple du fichier : 0,72 ≥ 0,65 → alerte.
- Bonne pratique : renvoyer le **seuil** et la **version** dans chaque réponse permet de **revérifier une décision après coup**.

*Confrontation avec le code du dépôt :*

| Écart | Contrat | Code actuel | Conséquence |
|---|---|---|---|
| ID d'exemple | `"MACH-EXEMPLE"` | `normalize_machine_id` exige un chiffre (TP 3) | **Testé** : `ValueError: machine_id sans numero : 'MACH-EXEMPLE'`. L'exemple serait rejeté (fail fast, comportement voulu) |
| Nom de la colonne machine | `machine_id` | `add_temporal_features` attend `machine` par défaut | Renommage nécessaire entre l'API et les features (M25) |
| Fuseau horaire | timestamps en UTC (`Z`) | non vérifié dans les données du dépôt | *À contrôler* : mélanger des dates avec et sans fuseau fait échouer ou fausse le tri |

*Ce qui manque pour un contrat complet :* les réponses d'**erreur** (422 données invalides · 401 · 413 · 429, vues aux M25-M26), les **unités** (°C ? le fichier ne le dit pas) et l'**ordre** attendu des mesures (le code les trie de toute façon).

**Compétence(s)** : C6 (implémenter / intégrer les briques) · lien C3 (features sans fuite, au TP 2)

**Aide IA reçue** : Claude Code a lancé la mise à niveau, la vérification du jalon et les commandes de contrôle du squelette. Il a ensuite expliqué le rôle de chaque commande, le sens de `--frozen` et l'intérêt de l'import de `indusense`. Au TP 2, il a lu `temporal.py` et ses tests, écrit et lancé le script de démonstration avec / sans `shift(1)`, et produit la preuve. Au TP 3, il m'a guidé pas à pas pour **prédire moi-même** la sortie (mes erreurs sont notées dans le tableau), puis a exécuté la vérification, les tests et un cas limite / un cas d'échec. **Je dois savoir réexpliquer chaque ligne du tableau ci-dessus sans aide.**

**Difficultés / questions**
- Le jalon 01 a été lancé **sans attendre le signal du formateur**. C'est réversible via la branche `sauvegarde/ismael-sall/20260928-112927`, et sans impact ici puisque le jalon ne change que le marqueur.
- **Incohérence entre supports** : la fiche jalon 01 demande d'extraire `clean_sensor_data`, alors que le pas-à-pas R2 la classe en extension facultative. → À confirmer avec le formateur.
- La fiche TD 23, citée par le pas-à-pas pour le code de `cleaning.py`, **n'est pas dans le dépôt**. → À demander.
- **Prérequis Sprint 2 (scénario B)** : un contrat I/O **d'exemple** est disponible ([docs/CONTRAT_IO_EXEMPLE_FICTIF_J1.json](docs/CONTRAT_IO_EXEMPLE_FICTIF_J1.json)), mais ses valeurs sont illustratives. → À confirmer avec le formateur : le scénario B me concerne-t-il ? Quel est le **seuil réel** du modèle du dépôt ? Où sont la model card v1 et le contrat validé ?

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
