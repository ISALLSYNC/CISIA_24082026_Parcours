# Glossaire détaillé — Sprint 3 InduSense 4.0

> **But** : relire chaque terme important du TP avec sa **définition**, son **rôle** (à quoi il sert dans le projet) et un **exemple**.
> **Sources** : `pas_a_pas_apprenant_sprint3_AELION_20260928_R2.md`, `prerequis_express_et_glossaire_sprint3.md`, `memo_metriques_sans_confusion.md`, et le travail réel consigné dans `journal_de_bord.md`.
> **Lecture des exemples** : sans marque = vécu dans **notre** TP (M23 → M32) · 📘 = exemple **tiré du cours**, module pas encore réalisé (M33 → J6).
> Rédigé le 13/10/2026 · mis à jour le 19/10/2026 (M30, M31-M32 réalisés : exemples réels et nouveaux termes).

---

## 0. Outils transverses (tout le sprint)

| Terme | Définition | Rôle | Exemple |
|---|---|---|---|
| **Terminal / PowerShell 5.1** | Fenêtre où l'on tape des commandes texte. PowerShell 5.1 est la version livrée avec Windows. | Lancer tous les outils (uv, git, docker). | PowerShell 5.1 ne connaît pas `&&` → on enchaîne avec `;`. |
| **uv** | Gestionnaire d'environnement et de dépendances Python. | Installer **exactement** les mêmes versions partout, sans « activer » de venv. | `uv sync --frozen --extra dev`, puis `uv run pytest -q`. |
| **`uv run`** | Exécute une commande **dans l'environnement du projet**. | Garantir qu'on utilise le Python 3.13 du projet, pas celui du système. | `uv run python --version` → `3.13.x` (fait foi). |
| **Lockfile (`uv.lock`)** | Fichier qui fige la version exacte de chaque dépendance. | Reproductibilité : même environnement sur chaque poste et en CI. | `uv.lock` fixe black **26.5.1** et ruff **0.15.20**. |
| **`--frozen`** | Option de uv : utilise `uv.lock` tel quel, interdit de le recalculer. | Empêcher une modification involontaire des versions. | Toutes les commandes du TP : `uv run --frozen …` ; preuve : `git status --short -- uv.lock` vide. |
| **Extra (dépendances optionnelles)** | Groupe de dépendances installé seulement sur demande. | Ne pas alourdir l'installation de base. | `--extra dev` (pytest, ruff…) · `--extra mlops` (DVC, MLflow). |
| **Git / commit** | Outil de versionnement ; un commit fige une version du code. | Historique, retour arrière, collaboration. | `c9678c8 chore(pre-commit): aligner les versions des hooks…` |
| **Branche personnelle** | Ligne de travail à son nom, à côté de `main`. | Travailler sans toucher `main` ni les branches `jalon/*`. | `ismael-sall`. |
| **Jalon** | Branche `jalon/NN` livrée par le formateur au début d'une demi-journée. | Apporter le matériel du module suivant **sans** écraser notre travail (fusion). | `jalon/07` → marqueur `07-j4-matin-m29-m30`. |
| **Fusion (merge) / conflit** | Combiner deux branches ; conflit = même zone modifiée des deux côtés. | Intégrer un jalon en gardant nos commits. | Jalon 07 : 2 conflits (`ci.yml`, `test_smoke_compose.py`), résolus en gardant **notre** version. |
| **Branche de sauvegarde** | Copie de la branche avant une opération risquée. | Pouvoir revenir en arrière si la fusion tourne mal. | `sauvegarde/ismael-sall/<horodatage>`. |
| **Remote / fork** | Dépôt distant ; fork = copie du dépôt sous notre compte GitHub. | Pousser notre travail et faire tourner la CI sans toucher au dépôt du formateur. | `origin` = dépôt du formateur · `fork` = `ISALLSYNC/CISIA_24082026_Parcours`. |
| **Commit ciblé** | Commit qui n'ajoute que des fichiers nommés explicitement. | Éviter d'embarquer un secret, une donnée ou un fichier généré. | `git add .pre-commit-config.yaml journal_de_bord.md preuves/…` (jamais `git add .`). |
| **Definition of Done (DoD)** | Liste des conditions à remplir pour dire qu'une tâche est finie. | Savoir objectivement quand s'arrêter. | M24 : tests + ruff + black + pre-commit verts, 2 pointeurs DVC, 2 `run_id`, 0 secret. |

---

## 1. M23 — Refactoring & structure projet

| Terme | Définition | Rôle | Exemple |
|---|---|---|---|
| **Refactoring** | Réorganiser le code **sans changer son comportement**. | Passer du notebook fragile à un code réutilisable et testé. | Le calcul des lags passe d'une cellule de notebook à `add_temporal_features()`. |
| **Package / module** | Package = dossier Python importable ; module = un fichier `.py`. | Organiser le code par responsabilité. | Package `indusense` ; module `features/temporal.py`. |
| **`src/` layout** | Le code vit sous `src/` et non à la racine. | Les tests tournent contre le **package installé**, comme en production → erreurs de packaging détectées. | `src/indusense/…` |
| **`pyproject.toml`** | Fichier d'identité du projet : nom, version Python, dépendances, scripts, réglages des outils. | Point unique de configuration du projet. | `requires-python = ">=3.13,<3.14"` · `[tool.ruff]`. |
| **CLI (`[project.scripts]`)** | Commande terminal exposée par le package. | Lancer l'entraînement / la prédiction sans écrire de Python. | `indusense = "indusense.cli:main"` → `uv run indusense --help` (train / predict). |
| **Feature** | Variable d'entrée du modèle. | Donner au modèle l'information utile. | Lag de température, moyenne glissante par machine. |
| **Fuite de données (leakage)** | Une information du **futur** (ou de la cible) entre dans l'entraînement. | À éviter : elle donne un score faussement excellent. | Moyenne glissante calculée **en incluant** la valeur courante. |
| **`shift(1)` avant `rolling`** | Décaler d'un pas **puis** calculer la moyenne glissante. | Parade anti-fuite : la feature n'utilise que le passé. | `features/temporal.py`, prouvé par `tests/test_temporal.py`. |
| **Split temporel vs stratifié** | Temporel = on teste sur des dates **postérieures** ; stratifié = mélange aléatoire équilibré. | Le split temporel imite la réalité (prédire l'avenir) ; le stratifié peut fuiter. | M24 : deux runs MLflow, `--split stratified` puis `--split temporal`. |
| **`normalize_machine_id`** | Fonction qui uniformise les identifiants de machine. | Éviter qu'une même machine soit vue comme deux machines. | `MACH_01` → `MACH-01` · `M-2` → `MACH-02`. |
| **Gold dataset** | Jeu de données propre, joint et prêt à entraîner. | Base commune à l'entraînement et à l'évaluation. | `data/gold/gold_dataset.csv` (versionné avec DVC). |
| **pytest** | Outil qui exécute les tests automatiques. | Prouver que le code fait ce qu'on attend. | `uv run pytest -q` → `31 passed, 3 skipped` au M29. |
| **ruff (lint)** | Analyseur qui repère les erreurs et le mauvais style. | Qualité homogène, détection précoce. | Erreur **E501** (ligne > 100 caractères) corrigée au M28. |
| **black (formatage)** | Formateur automatique de code Python. | Séparer le style de la logique ; plus de débat de mise en forme. | `uv run black --check .` → « 35 files would be left unchanged ». |

---

## 2. M24 — CI/CD, tests, versioning

| Terme | Définition | Rôle | Exemple |
|---|---|---|---|
| **CI (intégration continue)** | Serveur qui rejoue lint + tests + build à chaque push. | Détecter une régression avant qu'elle n'atteigne `main`. | GitHub Actions, run `38247687470` → **success**. |
| **Workflow / job / step** | Fichier de CI / groupe d'étapes sur une machine / une commande. | Décrire ce que la CI exécute. | `.github/workflows/ci.yml` : jobs `quality` et `build`. |
| **`needs:`** | Dépendance entre jobs. | `build` ne démarre que si `quality` est vert. | `build: needs: quality`. |
| **Wheel / artefact de build** | Paquet Python installable (`.whl`) produit par la CI. | Livrable versionné et téléchargeable. | `uv build` → `dist/*.whl`, publié comme `indusense-wheel`. |
| **pre-commit / hook** | Contrôles automatiques lancés **avant** un commit (et ici avant un push). | Déplacer la détection d'erreur « vers la gauche », au plus près du développeur. | ruff, black, gitleaks ; installés pour `pre-commit` **et** `pre-push`. |
| **`rev:` (version d'un hook)** | Version de l'outil que pre-commit télécharge. **Ne lit pas `uv.lock`.** | Doit être alignée sur `uv.lock`, sinon hook et CI se contredisent. | Incident du 12/10 : black 24.8.0 (hook) contre 26.5.1 (CI) → `rev` aligné. |
| **gitleaks / secret** | Détecteur de secrets (clés, mots de passe) dans le code. | Filet de sécurité contre les fuites ; **pas une garantie**. | Sentinelle AWS factice → `RuleID: aws-access-token`, `leaks found: 1`. |
| **Révoquer un secret** | Invalider la clé chez le fournisseur. | Un secret poussé reste dans l'**historique Git** : le supprimer ne suffit pas. | Règle du cours : secret exposé = compromis → révocation. |
| **`.gitignore`** | Liste des fichiers que Git ignore. | Ne jamais versionner secrets, bases locales, fichiers générés. | `.env`, `mlflow.db`, `mlruns/`, `predictions.db`. |
| **DVC** | Outil de versionnement des **gros fichiers** (données, modèles). | Git garde un petit pointeur ; le contenu va sur un remote. | `dvc add data/gold/gold_dataset.csv artifacts/models/rf.joblib`. |
| **Pointeur `.dvc` / remote DVC** | Petit fichier texte (empreinte md5) suivi par Git / stockage du contenu réel. | Retrouver la version exacte d'une donnée à partir d'un commit. | `rf.joblib.dvc` ; remote relatif `..\dvc-store`. |
| **MLflow (tracking)** | Outil qui enregistre chaque entraînement : paramètres, métriques, artefacts. | Comparer et retrouver les expériences. | Serveur local `--backend-store-uri sqlite:///mlflow.db` (nous : port **5001**, le 5000 était occupé). |
| **Run / `run_id`** | Une exécution d'entraînement / son identifiant unique. | Relier un modèle à ses paramètres et à ses scores. | Deux `run_id` relevés au M24 (split stratifié, split temporel). |
| **Registre (registry) / version de modèle** | Catalogue des modèles enregistrés, chacun avec des versions numérotées. | Savoir quel modèle est en service et revenir à un précédent. | Modèle `indusense-rf` : deux versions enregistrées au M24 (une par run). |
| **Stage MLflow** | Étiquette de cycle de vie : Staging → Production → Archived. | Gouverner la promotion d'un modèle. | Aucune promotion exigée au M24. |
| **`model_metadata.json` / `metrics.json` / `params.yaml`** | Fichiers décrivant le modèle, ses scores et ses paramètres. | Traçabilité lisible sans ouvrir MLflow. | Produits par `scripts/demo_versioning.py`. |
| **`versioning_strategy.md`** | Document : comment on versionne Code / Données / Modèle / Secrets. | Expliquer la reproductibilité = code + données + modèle **ensemble**. | Fichier à la racine du dépôt. |
| **Pull Request (PR) draft** | Demande de fusion en brouillon. | Faire tourner la CI et faire relire avant fusion. | PR draft #1 sur le fork. |

---

## 3. M25 — API REST (FastAPI)

| Terme | Définition | Rôle | Exemple |
|---|---|---|---|
| **API REST** | Interface HTTP : des ressources (URL) + des verbes (GET, POST…). | Rendre le modèle interrogeable par le réseau. | `POST /predict-tabular`. |
| **Endpoint** | Une URL + un verbe de l'API. | Point d'entrée d'une action précise. | `/health`, `/ready`, `/predict-tabular`, `/metrics`. |
| **FastAPI** | Framework Python pour écrire des API. | Construire l'API et générer sa documentation. | `src/indusense/api/main.py`. |
| **Uvicorn** | Serveur qui fait tourner l'application FastAPI. | Écouter les requêtes HTTP. | `uv run uvicorn indusense.api.main:app --reload`. |
| **Pydantic v2 / schéma** | Bibliothèque de validation de données / description d'une entrée ou sortie. | Refuser automatiquement un corps de requête invalide (**422**). | `src/indusense/api/schemas.py` : moins de 7 relevés → 422. |
| **Contrat I/O** | Description exacte de ce que l'API reçoit et renvoie. | Accord stable entre l'API et ses clients ; devient les schémas Pydantic. | Sortie : `proba_panne`, `decision`, `model_version`, `threshold`. |
| **`/docs` (Swagger / OpenAPI)** | Page de documentation interactive **générée depuis le code**. | La doc ne peut pas mentir : elle est dérivée du code. | `http://127.0.0.1:8000/docs`. |
| **Liveness (`/health`)** | « Le processus tourne. » | Sonde de vie ; reste **ouverte sans clé**. | `/health` → 200 dès le lancement. |
| **Readiness (`/ready`)** | « Le modèle est chargé, je peux prédire. » | Ne pas envoyer de trafic à une API pas prête. | `/ready` → **503** tant que le modèle manque. |
| **`lifespan`** | Code exécuté au démarrage et à l'arrêt de l'API. | Charger le modèle **une seule fois** (sinon latence énorme). | Chargement de `rf.joblib` au démarrage. |
| **Clé d'API (`X-API-Key`)** | Jeton secret envoyé dans l'en-tête de la requête. | Authentifier le client. | Sans clé → **401**. |
| **`.env` / `.env.example`** | Fichier local des secrets (ignoré par Git) / modèle versionné sans vraies valeurs. | Garder les secrets hors du dépôt. | `INDUSENSE_API_KEY`, `POSTGRES_PASSWORD` dans `.env`. |
| **Codes HTTP** | Nombre qui résume le résultat d'une requête. | Dire précisément ce qui s'est passé. | **200** OK · **400** `Content-Length` illisible · **401** pas de clé · **413** corps trop gros · **422** corps invalide · **429** trop de requêtes · **503** modèle absent. |
| **TestClient** | Client de test de FastAPI qui appelle l'API sans serveur réel. | Prouver les codes d'erreur dans pytest. | `tests/test_api.py` → 12 passed. |
| **Middleware / request-id** | Code exécuté autour de chaque requête / identifiant unique renvoyé dans `X-Request-ID`. | Corréler logs et requêtes ; **ce n'est pas un audit log**. | Réponse avec en-tête `X-Request-ID`. |
| **Payload** | Corps de la requête. | Données envoyées au modèle. | `payload.json`. |
| **Seuil de décision (threshold)** | Valeur de probabilité au-delà de laquelle on déclare « alerte ». | Transformer une probabilité en décision. | API : **0,5** ; calculé au M24 : **0,975** → question au formateur. |
| **Model Card** | Fiche d'identité du modèle à trois niveaux : Métier · Technique / maintenance · Conformité AI Act. | Justifier le modèle, ses limites et sa traçabilité, **sans rien inventer**. | `docs/model_card.md` ; `run_id` réel ou « à produire ». |
| **AI Act** | Règlement européen sur l'IA. | Qualifier le niveau de risque d'un système d'IA. | Statut prudent : « à confirmer avec le référent conformité ». |

---

## 4. M26 — Sécurité & menaces

| Terme | Définition | Rôle | Exemple |
|---|---|---|---|
| **Threat model** | Analyse : qu'est-ce qu'on protège, contre qui, comment. | Prioriser les défenses. | `threat_model.md` (STRIDE sur `/predict-tabular`). |
| **STRIDE** | 6 familles de menaces : usurpation, altération, déni d'action, fuite d'information, déni de service, élévation de privilège. | Grille pour ne pas oublier de menace. | Déni de service → contré par le rate limit. |
| **Actif / menace** | Ce qui a de la valeur / ce qui peut lui nuire. | Base du threat model. | Actif : le modèle ; menace : requêtes massives. |
| **Attack tree** | Arbre des chemins qu'un attaquant peut suivre. | Visualiser où placer les contrôles. | TP 1 du M26. |
| **Contrôle de sécurité** | Mesure qui réduit une menace. | Défense concrète et **testable**. | 5 contrôles : auth, validation, rate limit, taille payload, audit logging. |
| **Implémenté vs Planifié v0** | Contrôle codé **et prouvé** vs seulement prévu. | Ne pas confondre « documenté » et « fait ». | 4 Implémenté (401/422/429/413) + audit logging **Planifié v0**. |
| **Rate limit** | Nombre maximal de requêtes par période. | Contre le déni de service. | 60 requêtes / 60 s par IP ; la 61ᵉ → **429**. |
| **Limite de taille de payload** | Taille maximale du corps de requête. | Empêcher la saturation mémoire. | > 64 Ko → **413**. |
| **Audit logging** | Journal structuré des actions sensibles. | Traçabilité ; **sans** clé, payload ni PII. | Encore Planifié v0. |
| **PII** | Donnée personnelle identifiante. | Ne jamais la journaliser. | Colonnes opérateur des incidents : jamais dans les logs. |
| **Adversarial** | Entrée truquée pour tromper le modèle. | Menace propre au ML. | Valeurs capteurs forgées. |
| **Moindre privilège** | N'accorder que les droits nécessaires. | Limiter les dégâts en cas de compromission. | Conteneur non-root `appuser` (M27). |
| **Risque résiduel** | Ce qui reste comme risque après le contrôle. | Honnêteté du registre. | Colonne de `security_controls.md`. |

---

## 5. M27 — Conteneurisation (Docker)

| Terme | Définition | Rôle | Exemple |
|---|---|---|---|
| **Image Docker** | Paquet **immuable** : application + son environnement d'exécution. | « Ça marche pareil partout ». L'image **contient** le modèle, elle **n'est pas** le modèle. | `indusense:0.1.0` (1,81 Go). |
| **Conteneur** | Instance **en cours d'exécution** d'une image. | Faire tourner l'API isolée. | `docker run -d -p 8000:8000 --name indusense …`. |
| **Couches / cache** | Une image est un empilement de couches réutilisées d'un build à l'autre. | Builds rapides : **dépendances avant le code**. | Changer le code ne réinstalle pas les dépendances. |
| **Dockerfile** | Recette de construction de l'image. | Décrire l'image de façon reproductible. | `Dockerfile` à la racine. |
| **Multi-stage** | Étape `build` (outils lourds) puis étape `runtime` (image finale mince). | Ne pas livrer les outils de compilation. | `build` avec uv → `runtime` `python:3.13-slim`. |
| **Non-root** | Le processus tourne sous un utilisateur sans droits administrateur. | Si l'app est compromise, l'attaquant n'est pas root. | `docker exec indusense whoami` → **appuser** (uid 10001). |
| **`.dockerignore`** | Liste des fichiers exclus de l'image. | Image légère, sans secrets ; Git et Docker sont **deux périmètres distincts**. | `!artifacts/models` : le modèle est gardé. |
| **Variante A** | Le modèle est copié **dans** l'image. | `/ready` 200 dès le démarrage. | md5 du modèle dans l'image = celui de DVC. |
| **`HEALTHCHECK`** | Commande que Docker lance régulièrement pour vérifier le service. | Statut `healthy` / `unhealthy`. | Sonde sur `/health`. |
| **`--host 0.0.0.0`** | Écouter sur toutes les interfaces réseau. | Sinon l'API est injoignable depuis l'extérieur du conteneur. | `CMD uvicorn … --host 0.0.0.0 --port 8000`. |
| **Port mapping (`-p`)** | Relie un port du PC à un port du conteneur. | Accéder à l'API depuis le navigateur. | `-p 8000:8000`. |
| **Tag** | Nom + version d'une image. | Identifier précisément ce qu'on déploie. | `indusense:0.1.0`. |

---

## 6. M28 — Docker Compose

| Terme | Définition | Rôle | Exemple |
|---|---|---|---|
| **Docker Compose** | Outil qui lance **plusieurs conteneurs** décrits dans un fichier. | Démarrer toute la stack d'une commande. | `docker compose up -d --wait`. |
| **Service** | Un conteneur déclaré dans `docker-compose.yml`. | Brique de la stack. | `api`, `db`, `prometheus`, `grafana`. |
| **`depends_on: condition: service_healthy`** | L'API attend que la base soit **prête**, pas seulement lancée. | Éviter la course au démarrage. | `api` attend `db` healthy. |
| **Course au démarrage** | L'API démarre avant que la base accepte les connexions. | Bug **intermittent** à éviter. | « L'API plante une fois sur deux. » |
| **Healthcheck (`pg_isready`)** | Sonde « prêt ? » de PostgreSQL. | Rendre `service_healthy` possible. | `pg_isready -U indusense`. |
| **Réseau Compose** | Réseau privé où les services se joignent **par leur nom**. | Communication entre conteneurs. | `db:5432` et **pas** `localhost` (dans un conteneur, localhost = lui-même). |
| **Volume** | Stockage qui survit à la suppression du conteneur. | Garder les données de la base. | `pgdata` ; `down` le garde, `down -v` l'efface. |
| **PostgreSQL** | Base de données relationnelle serveur. | Stocker les prédictions (M30, mode principal). | Image `postgres:16`. |
| **`INDUSENSE_DB_URL`** | Adresse de connexion à la base (variable d'environnement). | Dire au code où écrire, sans la mettre en dur. | `postgresql+psycopg://…@db:5432/indusense`. |
| **Smoke test** | Test rapide « est-ce que ça fume ? » sur le système démarré. | Vérifier en quelques secondes que la stack répond. | `tests/test_smoke_compose.py` : 3 tests (`/health` 200, 401 sans clé, 200 avec). |
| **`skipif`** | Marqueur pytest qui saute un test si une condition est vraie. | Ne pas faire échouer la suite quand la stack est arrêtée. | Smoke tests « skipped » quand Compose est arrêté. |
| **`docker compose config`** | Valide et affiche la configuration finale. | Détecter une erreur **avant** `up`. | ⚠ son affichage contient les valeurs de `.env` : ne pas le mettre dans une preuve. |

---

## 7. M29 — Orchestration Prefect (design)

| Terme | Définition | Rôle | Exemple |
|---|---|---|---|
| **Orchestration** | Enchaîner automatiquement des étapes avec gestion des pannes. | Plus qu'un cron : retries, observabilité, dépendances. | `ingest → feature → predict → store`. |
| **Prefect** | Bibliothèque Python d'orchestration. | Faire tourner et suivre le pipeline. | Version **3.7.6**. |
| **Task** | Étape unitaire (`@task`). | Brique réessayable du pipeline. | `ping` dans `flows/hello.py`. |
| **Flow** | Fonction (`@flow`) qui orchestre des tasks. | Définir l'ordre et nommer l'exécution. | `hello_flow` (`hello-indusense`). |
| **Run** | Une exécution d'un flow, avec nom, état et logs. | Observabilité. | Run `accelerated-orca` → **Completed**. |
| **Retries / `retry_delay_seconds`** | Nombre de réessais automatiques / délai entre eux. | Survivre à une panne passagère. | `--flaky` : `Retry 1/2 will start 1 second(s) from now` puis succès. |
| **Backoff** | Délai **croissant** entre réessais. | Ne pas marteler une ressource en panne. | Design de `store` : 5 s, 15 s, 45 s. |
| **Erreur transitoire vs déterministe** | Passagère (réessayer peut marcher) vs permanente (réessayer ne change rien). | Ne réessayer **que** le transitoire. | Base injoignable 1 s = transitoire ; fichier absent = déterministe. |
| **Profil `ephemeral`** | Configuration Prefect locale, sans serveur permanent ni Cloud. | Preuve locale, sans compte. | `PREFECT_PROFILE=ephemeral`. |
| **`get_run_logger`** | Logger rattaché au run en cours. | Messages visibles dans le suivi du run. | « Résultat de la task ping : pong:indusense ». |
| **`merge_asof`** | Jointure pandas « à la valeur la plus proche dans le temps ». | Associer chaque température à la pression la plus proche. | `tolerance="90min"`, `direction="nearest"`. |
| **`by="machine"`** | Paramètre de `merge_asof` : ne joindre qu'**au sein de la même machine**. | Éviter la fuite inter-machines. | Sans `by` : **75 %** des lignes (1 440 / 1 920) reçoivent la pression d'une autre machine, **sans erreur**. |
| **Fuite inter-machines** | Mélange de données entre machines lors d'une jointure. | Bug silencieux à éviter (même idée que la fuite du M23). | Piège joué au M29. |
| **Résidu non joint** | Part des lignes sans correspondance dans la jointure. | Mesurer la qualité de la jointure. | Attendu ≈ 1,76 % sur le jeu complet ; 0,00 % sur le jeu du dépôt. |
| **Contrat de task** | Entrée, sortie, effet de bord, retry, clé d'idempotence d'une task. | Figer le design **avant** d'implémenter. | Table des contrats de `docs/flow_design.md`. |
| **Effet de bord** | Action qui modifie l'extérieur (base, fichier). | Seules ces tasks ont besoin de retries / d'idempotence. | `store` écrit en base ; les autres non. |
| **Fonction pure** | Même entrée → même sortie, aucun effet de bord. | Rejouable sans risque. | `feature`. |

---

## 8. M30 — Implémentation du flow

| Terme | Définition | Rôle | Exemple |
|---|---|---|---|
| **Idempotence** | Rejouer une opération ne change pas le résultat. | Relancer un pipeline sans créer de doublons. | 2 runs → lignes **0 → 4** puis **4 → 4** « IDEMPOTENT », en SQLite **et** en PostgreSQL (15 attendues avec le jeu complet). |
| **Clé naturelle** | Colonnes qui identifient une ligne de façon métier. | Base de l'upsert. | `PRIMARY KEY (machine, prediction_ts)` de la table `predictions`. |
| **Upsert** | Insérer **ou** mettre à jour si la clé existe. | Garantir l'idempotence. | `INSERT … ON CONFLICT (machine, prediction_ts) DO UPDATE` — même SQL pour SQLite et PostgreSQL ; `created_at` non écrasé à la relance. |
| **Table `predictions`** | Table qui historise les prédictions. | Garder la trace de ce que le modèle a dit. | 4 lignes (MACH-01 à 04) écrites par `predict_flow.py` ; contrôlées avec `psql` (0 doublon). |
| **SQLite** | Base de données dans un simple fichier, sans serveur. | Base de développement du M30 ; aussi registre MLflow et `drift_events`. | Base **neuve** sous `$env:TEMP\cisia_m30_<horodatage>`, jamais l'ancien `predictions.db`. |
| **SQLAlchemy / psycopg** | Bibliothèque d'accès aux bases / pilote PostgreSQL. | Écrire dans la base depuis Python, quelle que soit la base. | `create_engine(os.environ["INDUSENSE_DB_URL"])` dans `store` ; `engine.dialect.name` → `sqlite` ou `postgresql`. |
| **ISO 8601 (`isoformat`)** | Format texte standard de date-heure. | SQLite n'accepte pas un `pandas.Timestamp` brut. | `_ts_for_driver` : `isoformat()` pour SQLite, `to_pydatetime()` pour PostgreSQL. |
| **`prediction_ts` vs `created_at`** | Heure métier **sans** fuseau / instant d'audit **avec** fuseau. | Ne pas mélanger temps métier et temps technique. | En base PostgreSQL : `timestamp without time zone` / `timestamp with time zone`. |
| **Piège « cible date seule »** | La cible `panne` calculée sur la date sans l'heure (incident placé à minuit). | Fausse les étiquettes, parfois **sans changer le taux**. | Échantillon : taux **identique** (10,42 %) mais **192 / 1 920** étiquettes fausses ; jeu complet : 4,89 % au lieu de 4,7802 %. |
| **Population** | L'ensemble exact de lignes sur lequel on calcule un chiffre. | Un pourcentage n'a de sens qu'avec son dénominateur. | Logs du flow : `joined_rows=1920` (10,42 %) ≠ `gold_rows=1896` (10,55 %). |
| **`COMPOSE_PROJECT_NAME`** | Nom de projet Compose. | Isoler une base neuve des volumes existants. | `cisia_m30_20261013_113546` : volume `pgdata` neuf, données du M28 intactes. |
| **`retry_condition_fn`** | Fonction que Prefect consulte avant de réessayer une task. | Ne réessayer **que** les erreurs transitoires. | `_is_transient` : vrai seulement pour `OperationalError` → URL absente = échec immédiat ; base injoignable = 3 retries (5 / 15 / 45 s). |
| **`cache_policy=NO_CACHE`** | Désactive le cache des résultats d'une task Prefect. | Une task à effet de bord doit **toujours** s'exécuter. | Sur les 4 tasks du flow, `store` en particulier. |
| **Délai de connexion (`connect_timeout`)** | Temps maximal d'attente d'une connexion à la base. | Éviter qu'une base muette bloque longtemps. | Sur ce poste, port fermé → ≈ 130 s par tentative ; `?connect_timeout=3` dans l'URL de test. |
| **Délai de démarrage Prefect** | Temps laissé au serveur temporaire (`ephemeral`) pour démarrer. | Éviter un échec avant même le flow. | Dans le conteneur : 20 s dépassés → `PREFECT_SERVER_EPHEMERAL_STARTUP_TIMEOUT_SECONDS=120`. |
| **Serveur / tableau de bord Prefect** | Serveur local qui conserve l'historique des runs et l'affiche. | Observabilité : runs, graphe des tasks, logs, paramètres. | `prefect server start --host 127.0.0.1 --port 4200` → runs `massive-quail` (0 → 4), `lumpy-elephant` (4 → 4). |
| **Run fantôme** | Run resté « RUNNING » alors que son processus a été tué. | À nettoyer pour garder un historique fiable. | 3 runs (tests de retries interrompus) passés en **Cancelled** via l'API. |

---

## 9. M31-M32 — Data drift & alerting

| Terme | Définition | Rôle | Exemple |
|---|---|---|---|
| **Data drift** | Les données de production s'éloignent de celles d'entraînement. | Détecter qu'un modèle risque de se dégrader. | Fenêtre 2 « capteur +8 °C » du miroir InduSense ; semaine 2 « Vente Flash » de PayGuard. |
| **Covariate drift** | P(X) change : la distribution des entrées bouge. | Détectable **sans** labels. | Fenêtre 2 → PSI température **6,845**, mais rappel tenu (0,784). |
| **Concept drift** | P(y\|X) change : la relation entrée → panne change. | Nécessite des labels ; le PSI peut rester muet. | Fenêtre 3 : PSI **0,002**, rappel **0,053** (24 pannes vues sur 450), ROC-AUC 0,205. |
| **PSI** | Population Stability Index : ampleur d'un écart de distribution. | Mesurer — et **décider** — le drift. | < 0,1 RAS · 0,1-0,25 surveiller · > 0,25 dérive forte (seuil d'alerte de ma drift spec). |
| **KS** | Test de Kolmogorov-Smirnov : significativité de l'écart. | **Confirmer**, pas décider. | Pression : p = 4e-07 pour un PSI de 0,025 → « significatif » sans intérêt métier (grands effectifs). |
| **Référence / binning** | Distribution de comparaison / découpage en intervalles pour le PSI. | Un PSI se cite **toujours** avec population + référence + binning. | 10 intervalles figés sur la référence `normale` (32 177 relevés). |
| **Référence par régime** | Une référence distincte pour chaque mode de fonctionnement, choisie selon le planning métier. | Éviter les fausses alertes sans masquer une vraie dérive. | Janvier (campagne) : **6,213** vs `normale` → **0,001** vs `haute` ; fenêtre 2 reste en dérive forte. |
| **Segmentation par machine** | Calculer le PSI machine par machine. | **Localiser** l'équipement en cause. | Fenêtre 2, MACH-03 seule : PSI **19,469**. |
| **Fenêtre glissante / taille minimale** | Période récente sur laquelle on calcule, recalculée régulièrement ; effectif en dessous duquel on ne conclut pas. | Concilier réactivité et fiabilité du PSI. | Ma drift spec : calcul **quotidien sur 7 jours** (≈ 2 400 relevés), **≥ 2 000** ; pas horaire (≈ 14 relevés). |
| **Seuil gelé** | Seuil de décision fixé une fois pour toutes sur la validation. | Mesurer honnêtement la production (on ne le rechoisit pas sur les données à évaluer). | Miroir : **0,05** (coûts FN 5 000 € / FP 200 €) ; PayGuard : fixé par `train_model.py`. |
| **Evidently** | Bibliothèque de rapports de drift. | Extension optionnelle, **pas** dans le miroir. | Non installée, bonus non ouvert : `drift_lab.py` fait le travail (« repli maison »). |
| **Miroir autonome** | Petit projet séparé (son propre `uv.lock`) pour le TP drift. | Travailler sans dépendre du dépôt fil rouge. | `tp_drift_indusense` (copié dans `C:\CISIA`) → **11 passed** ; PayGuard (dépôt séparé) → **12 passed**. |
| **Rapport JSON de drift** | Résultat du calcul de drift en fichier JSON. | Lisible par l'humain et la machine. | `drift_report_f2.json` : `temperature` drift **true**, `pressure_bar` **false**, `_global` **true**. |
| **`drift_events`** | Table SQLite qui trace chaque alerte de drift. | Historiser les alertes. | **Une seule** ligne : `temperature`, PSI 6,845. |
| **Cooldown** | Délai minimal entre deux alertes sur une même feature. | Ne pas spammer. | `sequence=0 -> 1 -> 0` : la relance à +1 h (< 6 h) n'alerte pas — **la dérive n'a pas disparu**. |
| **Hystérésis** | On ne réarme l'alerte que quand la situation est clairement revenue à la normale. | Éviter le clignotement. | Ma drift spec : une alerte, puis silence **jusqu'à PSI < 0,10**, rappel à 7 jours. |
| **Drift spec** | Document qui fige quoi comparer, avec quoi, à quelle fréquence, quand alerter et que faire. | Rendre la surveillance non arbitraire. | `reports/drift_spec_indusense.md` (6 sections) ; `drift_spec_payguard.md`. |
| **KPI technique vs KPI métier** | Indicateur sur les données (PSI, KS) vs sur le résultat pour le métier (rappel, précision, taux d'alerte). | Le second voit ce que le premier ne voit pas. | KPI métier de ma spec : **rappel < 0,60** → alerte ; le taux de panne (≈ 5 % partout) ne détecte rien. |

---

## 10. M33 — Observabilité (Prometheus) 📘

| Terme | Définition | Rôle | Exemple |
|---|---|---|---|
| **Observabilité** | Capacité à comprendre l'état d'un système depuis l'extérieur. | Savoir si le service va bien, en continu. | Logs, métriques, dashboards. |
| **`/metrics`** | Endpoint qui expose les métriques au format Prometheus. | Être collecté par Prometheus. | 📘 `curl.exe http://localhost:8000/metrics`. |
| **Prometheus / scrape / target** | Collecteur de métriques / lecture périodique / cible collectée. | Historiser les métriques techniques. | 📘 job `indusense-api` sur `api:8000` toutes les 15 s ; cible **UP**. |
| **Instrumentator** | Composant qui instrumente automatiquement FastAPI. | Produire latence et trafic sans code manuel. | 📘 `Instrumentator(should_group_status_codes=False)` pour isoler les 401. |
| **Counter / Gauge / Histogram** | Compteur qui monte / valeur qui monte et descend / répartition (percentiles). | Choisir le bon type de métrique. | 📘 `indusense_predictions_total` (counter) · `indusense_model_loaded` (gauge) · latence (histogram). |
| **Label / cardinalité** | Étiquette d'une métrique / nombre de valeurs distinctes d'un label. | Trop de valeurs = explosion de séries **et** fuite de donnée. | 📘 label `decision` autorisé, `machine_id` interdit. |
| **PromQL** | Langage de requête de Prometheus. | Calculer un SLI. | 📘 `histogram_quantile(0.95, …)` = p95. |
| **p95** | Valeur sous laquelle se trouvent 95 % des mesures. | Mesurer la latence ressentie, sans être trompé par la moyenne. | 📘 p95 de latence de l'API. |
| **SLI / SLO** | Indicateur mesuré / objectif chiffré sur cet indicateur. | Mesurer sans objectif ne sert à rien. | 📘 SLO : p95 < 300 ms ; 5 SLO dans `slo.md`. |
| **Test de charge (Locust)** | Simuler beaucoup d'utilisateurs simultanés. | Observer le comportement sous charge. | 📘 `locust … -u 20 -r 5 -t 30s`. |
| **Exporteur** | Petit programme qui expose des métriques pour Prometheus. | Rendre le drift visible dans Prometheus. | 📘 `export_drift_metrics.py` sur le port 9109. |

---

## 11. M34 — Dashboards & runbooks (Grafana) 📘

| Terme | Définition | Rôle | Exemple |
|---|---|---|---|
| **Grafana** | Outil de tableaux de bord et d'alertes au-dessus de Prometheus. | Visualiser et alerter. | `http://localhost:3000` (ouvert au M28). |
| **Datasource** | Source de données de Grafana. | Indiquer où lire les métriques. | `http://prometheus:9090` (nom de service, pas localhost). |
| **Dashboard / panel** | Tableau de bord / un graphique alimenté par une requête PromQL. | Lecture rapide de l'état du service. | 📘 dashboard Service / Modèle / Données exporté en JSON. |
| **Alert rule** | Condition + durée (`for:`) + destination. | Prévenir quand un SLO est menacé. | 📘 p95 > 300 ms et 5xx > 1 %, en `for: 5m`. |
| **`for:` (anti-flap)** | La condition doit **durer** avant de déclencher. | Éviter les alertes sur un pic isolé. | 📘 `for: 5m` en production, `for: 1m` en exercice. |
| **Pending / Firing / Normal** | États d'une alerte : condition vue / déclenchée / résolue. | Suivre le cycle de vie d'un incident. | 📘 `docker compose stop api` → Firing → `up -d api` → Normal. |
| **Runbook** | Procédure : symptôme → diagnostic → action → escalade. | Réagir vite et de façon fiable à une alerte. | 📘 runbook joué jusqu'au retour Normal ; « un runbook non joué est probablement faux ». |

---

## 12. J6 — Game Day 📘

| Terme | Définition | Rôle | Exemple |
|---|---|---|---|
| **Game Day** | Exercice d'incident simulé en conditions réelles. | S'entraîner à diagnostiquer et réparer. | 📘 « Opération lundi matin ». |
| **Tag (`v1.0-sain`)** | Étiquette Git sur un commit de référence. | Point de comparaison certifié. | 📘 `git diff --stat v1.0-sain J6-gameday`. |
| **Bundle Git** | Dépôt Git empaqueté dans un seul fichier. | Distribuer le scénario sans GitHub. | 📘 remis par le formateur. |
| **Post-mortem** | Analyse écrite d'un incident, sans chercher de coupable. | Apprendre et éviter la répétition. | 📘 rendu en fin de J6. |
| **Retex** | Retour d'expérience collectif. | Améliorer le prochain sprint. | 📘 clôture du Sprint 3. |

---

## 13. Métriques (mémo du cours)

| Terme | Définition | Rôle | Exemple |
|---|---|---|---|
| **TP / FP / FN / TN** | Vrai positif / fausse alerte / panne manquée / vrai négatif (la panne = classe positive). | Base de toutes les métriques de classification. | FN = panne réelle non détectée ; FP = fausse alerte. Le choix du seuil arbitre entre les deux selon les coûts métier. |
| **Accuracy** | (TP + TN) / total. | Trompeuse avec des classes rares. | Prédire toujours « pas de panne » donne une bonne accuracy et un rappel nul. |
| **Précision** | TP / (TP + FP) : parmi les alertes, combien sont de vraies pannes. | Mesurer les fausses alertes. | — |
| **Rappel (recall)** | TP / (TP + FN) : parmi les pannes, combien sont détectées. | Mesurer les pannes manquées. | Rappel fenêtre 3 = 0,053 sous concept drift (miroir InduSense). |
| **PR-AUC** | Aire sous la courbe précision-rappel. | Métrique adaptée aux classes rares. | Benchmark Marine (encadré distinct) : PR-AUC ≈ 0,62. |
| **MAE / RMSE / MBE / MAPE** | Erreurs de régression : absolue moyenne / quadratique / biais signé / relative en %. | Évaluer une prédiction numérique ; ne pas les confondre. | Mémo : MBE = 0 n'implique **pas** une prédiction parfaite. |
| **Prévalence / taux de panne** | Part de lignes en panne dans une population donnée. | Toujours nommer la population. | Starter 10,55 % · jointure complète 4,78 % · gold complet 4,81 %. |
