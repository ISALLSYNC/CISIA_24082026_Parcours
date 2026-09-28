# Stratégie de versioning — InduSense

> Livrable M24 (fiche TD 24, étape 6). Créé à partir du modèle [docs/versioning_strategy.md](docs/versioning_strategy.md),
> complété avec les **preuves réellement obtenues** le 28/09/2026 sur la branche `ismael-sall`.
> Détail et sorties brutes : [journal_de_bord.md](journal_de_bord.md) (section M24) et [preuves/](preuves/).

## Vue d'ensemble

| Objet | Source de vérité | Identifiant / version | Stockage | Preuve de restauration |
|---|---|---|---|---|
| **Code** | Branche Git `ismael-sall` → PR vers `main` | Hash de commit (ex. `caeb24e`) · `uv.lock` pour les dépendances | Git (fork `ISALLSYNC/CISIA_24082026_Parcours`) | `git switch --detach <commit>` puis `uv sync --frozen --extra dev --extra mlops` · CI verte sur une machine neuve : [PR #1](https://github.com/ISALLSYNC/CISIA_24082026_Parcours/pull/1), [run 36441665863](https://github.com/ISALLSYNC/CISIA_24082026_Parcours/actions/runs/36441665863) |
| **Données** | Pointeur `data/gold/gold_dataset.csv.dvc` versionné par Git | md5 **`637be8d3825023160de0980761c9a9e8`** · 287 704 octets | DVC, remote `localstore` = `..\dvc-store` (hors dépôt) | `dvc status` → *up to date* · `dvc status -c` → *in sync* ([preuves/24_dvc.txt](preuves/24_dvc.txt)). Aller-retour `dvc pull` après vidage du cache : **non rejoué** (TD avancé) |
| **Modèle** | Pointeur `artifacts/models/rf.joblib.dvc` + `model_metadata.json` + registre MLflow | md5 **`2779890061870d6a08d6efdf733da094`** · registre `indusense-rf` **v1** et **v2** | DVC (fichier) + MLflow (runs, métriques, versions) | `dvc status -c` → *in sync* · 2 runs `FINISHED`, 2 versions `READY` ([preuves/24_mlflow.txt](preuves/24_mlflow.txt)) |
| **Secrets** | Aucun dans le dépôt | Jamais dans Git | `.env` local (ignoré par `.gitignore`, ligne 40) · secrets GitHub Actions pour la CI (aucun utilisé à ce jour) | Hook **gitleaks** : bloque une clé d'exemple AWS (`leaks found: 1`), passe à chaque commit ([preuves/24_tp1_gitleaks_demo.txt](preuves/24_tp1_gitleaks_demo.txt)) |

## Code

Toute modification passe par une **PR**. La PR doit avoir une **CI verte** : ruff, black, pytest, build.

- **Local** : hooks pre-commit (ruff `--fix`, black, gitleaks) avant chaque commit et chaque push.
- **CI** ([.github/workflows/ci.yml](.github/workflows/ci.yml)) : job `quality` (`uv sync --frozen`, ruff, black `--check`, pytest), puis job `build` (`needs: quality`, `uv build`, wheel publié sous `indusense-wheel`).
- **Dépendances** : `uv.lock` n'est **jamais** modifié en salle ; toutes les commandes utilisent `--frozen`.

## Données

Les datasets volumineux sont suivis avec **DVC**. Git conserve les **pointeurs**, pas les fichiers lourds.

- `git rm --cached` puis `dvc add` : le Gold et le modèle sont sortis de Git (commit `96ba527`) ; les `.gitignore` locaux créés par DVC l'emportent sur la règle `!artifacts/models/rf.joblib` du `.gitignore` racine.
- Remote **local** `..\dvc-store`, chemin relatif dans `.dvc/config` (`../../dvc-store`) : portable, aucun `C:\` en dur.
- *Limite* : les versions **antérieures** au commit `96ba527` restent dans l'historique Git ; le remote n'existe que sur ce poste (pas de `dvc pull` possible pour un collègue ni pour la CI).

## Modèle

Les artefacts modèle sont accompagnés de `model_metadata.json`. Promotion : **Candidate → Staging → Production → Archived**.

- Serveur MLflow local : `mlflow server --backend-store-uri sqlite:///mlflow.db --host 127.0.0.1 --port 5000` (`mlflow.db` ignoré par Git).
- Expérience `indusense-maintenance`, modèle enregistré `indusense-rf`. Aucune promotion de stage faite (`stage=None`) : non exigée.

| Version registre | `run_id` | Split | PR-AUC | ROC-AUC | Précision / Rappel / F1 |
|---|---|---|---|---|---|
| **v1** | `dc83b65fafd0484eb87efa7587b67590` | stratifié (**fuite**) | 0.4336 | 0.8531 | 0 / 0 / 0 |
| **v2** | `ac4544af25d14f50bb5edd7e518cca3a` | temporel par machine (**honnête**) | 0.1036 | 0.2475 | 0 / 0 / 0 |

Paramètres communs ([params.yaml](params.yaml)) : 200 arbres, graine 42, 20 % de test (1516 / 380 lignes), seuil 0.975, Gold `637be8d38250`.

- **Lecture** : le split stratifié paraît bon uniquement à cause de la **fuite**. Évalué sur le futur (split temporel), le modèle fait **moins bien que le hasard** (ROC-AUC < 0.5 ; PR-AUC < taux de panne 0.13). L'artefact de référence est celui du run **temporel** (évaluation honnête).
- **Constat 1** : précision, rappel et F1 à 0 dans les deux runs : le seuil 0.975 est calibré sur le train (*hypothèse* : sur-apprentissage de la forêt aléatoire). Comparaison faite sur PR-AUC / ROC-AUC, indépendants du seuil.
- **Constat 2** : le fichier `rf.joblib` livré est **identique** dans les deux runs (même md5) : il est entraîné sur tout le Gold avec la graine 42 ; le split ne change que l'évaluation.
- **Décision** : ce modèle **ne doit pas être promu** en Staging/Production en l'état. Suite : investigation documentée (features, dérive dans le temps, données par machine), puis candidat comparé en champion / challenger — jamais de réentraînement aveugle.

## Secrets

Aucun secret dans Git. Secrets locaux dans `.env`, secrets CI dans **GitHub Actions secrets**.

- `.env` ignoré par Git ; `.env.example` documente les **noms** de variables, sans valeur.
- Un secret commité est **compromis à vie** (il reste dans l'historique) : il faut le **révoquer**, pas seulement supprimer le fichier.
- Même un fichier de **preuve** peut contenir un secret : la clé d'exemple AWS a été masquée dans la preuve gitleaks avant commit.

## Questions à trancher

1. **Quel commit produit quel modèle ?** Le pointeur `artifacts/models/rf.joblib.dvc` du commit `96ba527` (et inchangé depuis) référence le md5 `2779890061870d6a08d6efdf733da094`. Les deux runs MLflow ont été lancés depuis le commit `193be25` : MLflow l'enregistre **automatiquement** dans le tag `mlflow.source.git.commit = 193be25fb9347e981c3d708d220c60a0e8097069` (avec `mlflow.source.git.branch = ismael-sall`), et le script ajoute le tag `gold_md5 = 637be8d38250`. Le lien **commit ↔ données ↔ run ↔ version du registre** est donc complet.
2. **Quelle empreinte identifie le Gold utilisé ?** md5 `637be8d3825023160de0980761c9a9e8` (pointeur `data/gold/gold_dataset.csv.dvc`), repris en abrégé `637be8d38250` dans `model_metadata.json` et dans les tags MLflow.
3. **Comment rejouer un run sans modifier `uv.lock` ?** `uv sync --frozen --extra dev --extra mlops`, puis `uv run --frozen python scripts/demo_versioning.py --no-dvc --tracking-uri http://127.0.0.1:5000 --split temporal` ; vérifier ensuite `git diff --exit-code -- uv.lock`.
4. **Comment restaurer code, données et modèle ensemble ?** `git switch --detach <commit>` (code + pointeurs), `uv sync --frozen …` (dépendances), `dvc checkout` ou `dvc pull` (fichiers correspondant aux pointeurs). *Procédure non rejouée de bout en bout à ce jour* (aller-retour prévu au TD avancé).

## Contrat d'expérience vision — rappel cohorte de juin

> Section imposée par la fiche TD 24. Elle concerne un modèle **vision** que je n'ai pas produit : aucune valeur n'est inventée.

| Champ | Valeur / preuve |
|---|---|
| run_id MLflow | à produire |
| méthode / score | à produire : MSE, SSIM validée ou PatchCore réel |
| split ou hash ; résolution ; seed | à produire |
| seuil et calibration | seuil propre à chaque score ; à produire |
| carte d'erreur / artefact | chemin à produire |
| durée ; pic mémoire ; énergie/CO2e | à mesurer, jamais extrapoler |
| statut | **MESURES=NOT_READY** tant que les preuves manquent |

Pour comparer deux méthodes, garder split/hash, scène, résolution, seed et budget identiques ; pour étudier la résolution, ne faire varier que ce facteur. MSE et SSIM n'ont pas la même échelle : leur seuil se calibre séparément. Les coûts tabulaires ne sont pas des coûts vision et ne sont pas recopiés ici.
