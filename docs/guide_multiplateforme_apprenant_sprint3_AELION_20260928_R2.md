# Guide multiplateforme apprenant - Sprint 3 CISIA

> **Correction R2 du 28/09/2026 :** les deux sources Python du laboratoire Vision ont été refusées par Dendreo. Les PDF servent à la lecture ; obtenir les fichiers exécutables auprès du formateur avant le TP.

> **Mise à jour AELION du 28/09/2026 - version à utiliser.** Dans l'extranet Dendreo/AELION, ouvrez : **Concevoir et implémenter une solution d’IA > Public - Participants de l'ADF > Tous les Participants > ressources > Sprint 3**. Sous-dossiers : `01_PRESENTATIONS_PPTX` · `02_PRESENTATIONS_PDF` · `03_GUIDES_FICHES_ET_REVISION` · `04_FICHIERS_A_COMPLETER` · `05_DONNEES_ET_EXERCICES` · `06_Schéma_et_DAT` · `corrigé` · `fiches de révision autres sprints`.
>
> Les exercices sont distribués **en fichiers individuels**. Dans `05_DONNEES_ET_EXERCICES`, choisissez `M25_API`, `TP_PAYGUARD`, `TP_INDU_SENSE`, `VISION_METRICS`, `GAME_DAY` ou `PERFORMANCE_ET_DIVERS`. PayGuard et Vision sont déjà extraits : ne cherchez aucun ZIP. Les noms `data__...`, `scripts__...` et `tests__...` désignent les sous-dossiers à recréer ; retirez le suffixe `.txt` des fichiers de code et de configuration après téléchargement. Consultez `MODE_EMPLOI_FICHIERS_INDIVIDUELS.md` et `MANIFESTE_EXERCICES_INDIVIDUELS.json` pour les noms et empreintes.
>
> Le bundle Git GameDay complet n'est pas publié dans l'espace public ; attendez la remise par le formateur pour cette activité. Cette mise à jour remplace les anciens chemins de pack, les commandes d'extraction ZIP et les consignes de recherche de bundle dans les pages antérieures.



**Révision du 5 septembre 2026 :** ce guide est réconcilié sur le guide canonique du dépôt corrigé (socle local 1d6f0b5). Lire `notice_preparation_et_controles_sprint3.md` et `memo_metriques_sans_confusion.md` avant les ateliers. Pour MLflow : extras dev ET mlops, puis `uv run --no-sync`.


Version locale du 23 août 2026. Ce guide complète le pas à pas apprenant sans
modifier les objectifs, les preuves ni les résultats attendus. Choisissez une
colonne au début du Sprint et gardez le même terminal pendant une séquence.

| Poste | Terminal recommandé dans VS Code | Type de commandes |
|---|---|---|
| Windows | Windows PowerShell 5.1 ou PowerShell 7 | blocs `powershell` |
| macOS | zsh, terminal par défaut | blocs `bash` |
| Linux | bash | blocs `bash` |

Sous macOS, le terminal interactif reste zsh. Lorsqu'une commande commence par
`bash scripts/...`, c'est volontaire : le script est exécuté par bash. Sous WSL,
suivez la colonne Linux et gardez le dépôt dans votre dossier Linux, par exemple
`~/CISIA`, plutôt que dans `/mnt/c/...`.

## 1. Ouvrir le bon terminal et le bon dossier

Dans VS Code, choisissez **Fichier > Ouvrir le dossier**, sélectionnez le dépôt
ou le TP demandé, puis **Terminal > Nouveau terminal**.

### Windows - PowerShell

```powershell
Get-Location
Test-Path -LiteralPath .\pyproject.toml
Test-Path -LiteralPath .\uv.lock
$PSVersionTable.PSVersion
```

### macOS - zsh ou Linux - bash

```bash
pwd
test -f ./pyproject.toml && echo "pyproject.toml: OK"
test -f ./uv.lock && echo "uv.lock: OK"
printf 'shell=%s\n' "$SHELL"
```

Si un fichier attendu est absent, n'installez rien et ne créez pas un nouveau
projet : rouvrez le bon dossier dans VS Code.

## 2. Préflight commun

Requis dès J1, avec les mêmes commandes sur les trois systèmes :

```text
git --version
uv --version
uv sync --frozen --extra dev
uv run python --version
uv run pytest -q
uv run ruff check .
```

Docker n'est requis qu'avant J3. A ce moment, ajoutez :

```text
docker --version
docker compose version
```

La version qui fait foi est `uv run python --version`, attendue en Python 3.13.x.
Avec `uv run`, il n'est pas nécessaire d'activer manuellement `.venv`.

Activation facultative, uniquement si le formateur la demande :

```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

```bash
# macOS zsh et Linux bash
source .venv/bin/activate
```

Si `uv` manque avant la formation :

```powershell
# Windows avec WinGet
winget install --id=astral-sh.uv -e
```

```bash
# macOS avec Homebrew
brew install uv
```

```bash
# macOS ou Linux, installateur officiel Astral
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Fermez puis rouvrez le terminal après installation. Pendant une séquence de
cours, ne lancez pas un installateur ou une commande `sudo` improvisée : signalez
le blocage et utilisez le plan B du formateur.

Pour Docker, Windows et macOS utilisent normalement Docker Desktop. Linux peut
utiliser Docker Desktop ou Docker Engine avec le plugin Compose. Dans tous les
cas, la commande attendue est `docker compose`, jamais l'ancien
`docker-compose`.

Si le pack demande encore d'appliquer le correctif dépôt sur macOS/Linux,
commencez par un `git status --short` vide, puis utilisez le patch fourni :

```bash
patch_file="/chemin/vers/correctif_depot_sprint3/correctif_depot_sprint3.patch"
git apply --check "$patch_file"
git apply "$patch_file"
uv sync --frozen --extra dev
uv run pytest -q
```

Si `git apply --check` échoue, ne forcez pas. La correction peut être déjà
présente ou le dépôt peut contenir du travail différent ; montrez le diagnostic
au formateur.

## 3. Traductions indispensables

| Besoin | Windows PowerShell | macOS zsh | Linux bash |
|---|---|---|---|
| Afficher le dossier | `Get-Location` | `pwd` | `pwd` |
| Lister les fichiers | `Get-ChildItem` | `ls -la` | `ls -la` |
| Tester un fichier | `Test-Path .\fichier` | `test -f ./fichier` | `test -f ./fichier` |
| Lire un fichier | `Get-Content .\fichier` | `cat ./fichier` | `cat ./fichier` |
| Copier `.env` s'il manque | `if (-not (Test-Path .\.env)) { Copy-Item .\.env.example .\.env }` | `test -f .env \|\| cp .env.example .env` | `test -f .env \|\| cp .env.example .env` |
| Variable temporaire | `$env:NOM = "valeur"` | `export NOM='valeur'` | `export NOM='valeur'` |
| GET HTTP en échec explicite | `Invoke-RestMethod http://127.0.0.1:8000/health` | `curl -fsS http://127.0.0.1:8000/health` | `curl -fsS http://127.0.0.1:8000/health` |
| Chercher du texte | `Select-String -Path .\fichier -Pattern 'mot'` | `grep -n 'mot' ./fichier` | `grep -n 'mot' ./fichier` |
| Dossier temporaire | `$env:TEMP` | `${TMPDIR:-/tmp}` | `${TMPDIR:-/tmp}` |

Les chemins écrits avec `/`, par exemple `scripts/train_model.py`, fonctionnent
avec Python, Git et Docker sur les trois systèmes. Les chemins `C:\...`, les
cmdlets `Get-Content`, `Copy-Item`, `Test-Path` et `Invoke-RestMethod` sont propres
à PowerShell.

## 4. Git et jalons de demi-journée

Les commandes Git de base sont communes :

```text
git clone URL_ANNONCEE_PAR_LE_FORMATEUR
cd NOM_DU_DEPOT
git switch -c prenom-nom
git status
git add -A
git commit -m "travail avant nouveau jalon"
```

Ne travaillez jamais directement sur `main` ni sur une branche `jalon/...`.
Avant chaque mise à niveau, le dépôt doit être propre.

### Windows

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\formation\mettre_a_niveau.ps1 -Jalon 03
powershell -ExecutionPolicy Bypass -File .\scripts\formation\verifier_jalon.ps1 -Jalon 03
```

En cas de conflit :

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\formation\mettre_a_niveau.ps1 -Jalon 03 -Rattrapage
```

### macOS ou Linux

```bash
bash scripts/formation/mettre_a_niveau.sh 03
bash scripts/formation/verifier_jalon.sh 03
```

En cas de conflit :

```bash
bash scripts/formation/mettre_a_niveau.sh 03 --rattrapage
```

Les deux variantes créent une branche `sauvegarde/...` avant la fusion. Le mode
rattrapage annule une fusion conflictuelle et crée une branche
`rattrapage/...`; il ne supprime et ne réécrit aucun commit.

Si vous choisissez de résoudre un conflit au lieu du mode rattrapage, gardez la
séquence suivante : `git status`, ouverture de chaque fichier signalé,
suppression des marqueurs `<<<<<<<`, `=======` et `>>>>>>>`, puis `git add`.
Dans `.github/workflows/ci.yml`, conservez notamment l'installation
`uv sync --frozen --extra dev`. Lancez ensuite `uv run pytest -q` et
`uv run ruff check .` avant le commit de résolution. N'utilisez jamais
`git reset --hard` pour sortir d'un conflit de formation.

Le nombre `03` cible la branche publique `jalon/03`. Un ancien slug complet tel
que `03-j2-matin-m25` reste accepté, mais le numéro court est la notation de
référence pour les douze demi-journées.

`FORMATION/JALON_ACTUEL.md` est un témoin livré par la branche : ne le modifiez
pas à la main pour faire passer le vérificateur. En cas d'écart, le script
affiche désormais la branche locale et le marqueur réellement lu, puis indique
la commande de mise à niveau à relancer.

## 5. M23 - package, tests et qualité

Ces commandes sont communes :

```text
uv run pytest tests/test_package.py tests/test_loaders.py tests/test_temporal.py -q
uv run ruff check .
uv run indusense --help
```

Ouvrez les fichiers depuis l'Explorateur VS Code. Les chemins affichés avec `/`
restent valides sous Windows.

Pour la démonstration Gitleaks sur macOS/Linux :

```bash
cat > fuite_demo.txt <<'EOF'
# Valeurs d'exemple publiques et invalides.
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
EOF
git add -f -- fuite_demo.txt
uv run pre-commit run gitleaks --files fuite_demo.txt
git restore --staged -- fuite_demo.txt
rm -- fuite_demo.txt
```

## 6. M24 - pre-commit, DVC et MLflow

Commandes communes :

```text
uv sync --frozen --extra dev --extra mlops
uv run pre-commit run --all-files
uv run pytest -q
git diff --exit-code -- uv.lock
```

Remote DVC local de démonstration :

```powershell
# Windows
$dvcRemote = Join-Path $env:TEMP 'cisia-dvc-store'
uv run python scripts/demo_versioning.py --remote "$dvcRemote"
```

```bash
# macOS et Linux
dvc_remote="${TMPDIR:-/tmp}/cisia-dvc-store"
uv run python scripts/demo_versioning.py --remote "$dvc_remote"
```

N'ajoutez jamais une vraie clé, un jeton ou un mot de passe dans Git, DVC ou une
capture d'écran.

## 7. M25 - API FastAPI

Ouvrez deux terminaux VS Code. Dans le terminal 1, commande commune :

```text
uv run uvicorn indusense.api.main:app --reload --port 8000
```

Dans le terminal 2 :

```powershell
# Windows
Invoke-RestMethod http://127.0.0.1:8000/health
Start-Process http://127.0.0.1:8000/docs
```

```bash
# macOS
curl -fsS http://127.0.0.1:8000/health
open http://127.0.0.1:8000/docs
```

```bash
# Linux
curl -fsS http://127.0.0.1:8000/health
xdg-open http://127.0.0.1:8000/docs >/dev/null 2>&1 &
```

Si l'ouverture automatique du navigateur échoue, copiez simplement l'URL dans
Chrome ou Firefox. Arrêtez Uvicorn avec `Ctrl+C` dans le terminal 1.

Pour M25, téléchargez les fichiers individuels du dossier AELION `05_DONNEES_ET_EXERCICES/M25_API`. Retirez le suffixe `.txt` de `APPLIQUER_PREUVES_M25.py.txt`, placez le dossier M25 à côté du clone, puis lancez depuis la racine du clone :

```text
uv sync --frozen --extra dev
uv run --frozen python ../M25_API/APPLIQUER_PREUVES_M25.py .
```

Les trois scripts M25 dont le texte a été refusé par AELION sont aussi disponibles comme PDF lisibles dans ce même dossier ; demandez les fichiers source au formateur si leur exécution est requise.

## 8. M26 - sécurité

La suite de preuves est commune :

```text
uv run pytest tests/test_api.py tests/test_security.py -q
uv run python
```

Dans l'interpréteur Python qui vient de s'ouvrir, saisir ces lignes puis quitter :

```python
from inspect import signature
from indusense.api.security import rate_limit_dependency as dep
print(signature(dep))
exit()
```

Les statuts 400, 401, 413, 422 et 429 doivent être produits par les mêmes tests
sur les trois systèmes. Ne mettez jamais la clé API dans le code ou le journal
Git.

## 9. M27 et M28 - Docker et Compose

Créer `.env` localement :

```powershell
# Windows
if (-not (Test-Path -LiteralPath .\.env)) {
    Copy-Item -LiteralPath .\.env.example -Destination .\.env
}
```

```bash
# macOS et Linux
test -f .env || cp .env.example .env
```

Les commandes Docker sont communes :

```text
docker run --rm hello-world
docker build -t indusense-api:m27 .
docker run --rm -d --name indusense-m27 -p 8000:8000 --env-file .env indusense-api:m27
docker inspect indusense-m27 --format '{{.Config.User}}'
docker stop indusense-m27
docker compose config -q
docker compose up -d --build
docker compose ps
docker compose down
```

`docker compose down` supprime les conteneurs et le réseau, mais conserve les
volumes nommés `pgdata`, `prometheus_data` et `grafana_data`. Les données
PostgreSQL, l'historique Prometheus et les personnalisations Grafana retrouvent
donc leur état au prochain `up`. La commande `docker compose down -v` efface ces
volumes : ne l'utilisez que pour une remise à zéro volontaire, après validation
du formateur.

Tester l'API :

```powershell
# Windows
Invoke-RestMethod http://127.0.0.1:8000/health
```

```bash
# macOS et Linux
curl -fsS http://127.0.0.1:8000/health
```

Sur macOS Apple Silicon, n'ajoutez pas spontanément `--platform linux/amd64` :
utilisez d'abord les images multi-architectures prévues. Sous Linux, si Docker
répond `permission denied` sur `/var/run/docker.sock`, ne relancez pas tout avec
`sudo`; arrêtez-vous et demandez la validation du formateur.

## 10. M29 et M30 - Prefect et idempotence

Au debut du jalon 07, `flows/pipeline.py` est volontairement absent : creez-le
pendant M29. Sa version de reference n'apparait qu'au jalon 08. Ne lancez la
premiere commande ci-dessous qu'apres cette creation.

Avant toute commande Prefect, forcez l'orchestration locale afin de ne pas
heriter d'un profil Prefect Cloud actif sur le poste :

```powershell
# Windows
$env:PREFECT_PROFILE = 'ephemeral'
$env:PREFECT_SERVER_ANALYTICS_ENABLED = 'false'
$env:PREFECT_CLOUD_ENABLE_ORCHESTRATION_TELEMETRY = 'false'
```

```bash
# macOS et Linux
export PREFECT_PROFILE=ephemeral
export PREFECT_SERVER_ANALYTICS_ENABLED=false
export PREFECT_CLOUD_ENABLE_ORCHESTRATION_TELEMETRY=false
```

Commandes communes, apres creation de `flows/pipeline.py` :

```text
uv run python flows/pipeline.py
uv run python scripts/demo_prefect_idempotence.py
git status --short
```

La preuve d'idempotence livrée à partir du **jalon 07** est autonome et utilise
SQLite. Elle n'a besoin ni de Docker ni de PostgreSQL :

```text
uv run python scripts/demo_prefect_idempotence.py --reset
uv run python scripts/demo_prefect_idempotence.py
uv run python scripts/demo_prefect_idempotence.py --new 2
uv run python scripts/demo_prefect_idempotence.py --show
```

La deuxième exécution sans `--new` doit conserver le même nombre de lignes.
`--new 2` ajoute deux horodatages **synthétiques** par machine afin de montrer
la différence entre une nouvelle clé métier et la reprise d'une clé existante.
Cette démonstration n'est pas un connecteur d'ingestion industrielle et n'écrit
pas dans le service PostgreSQL du Compose.

À partir du **jalon 08**, `uv run python flows/pipeline.py --serve` enregistre un
déploiement local et relit périodiquement les fichiers du répertoire configuré.
Le parcours ne livre pas de producteur de nouvelles données : dans un système
réel, un équipement, une API ou un bus dépose d'abord un lot validé de façon
atomique. Le flow le détecte au run suivant ; un watermark et une clé métier
stable empêchent les doublons. Ne présentez donc pas la planification Prefect
comme une ingestion automatique à elle seule.

## 11. M31 et M32 - PayGuard

Téléchargez les fichiers individuels de `05_DONNEES_ET_EXERCICES/TP_PAYGUARD`. Dans un dossier local court `tp_payguard`, recréez les sous-dossiers `data/`, `data/labels/`, `scripts/` et `tests/` à partir des noms `__`, puis retirez le suffixe `.txt` des fichiers de code, de configuration et du verrou. Vérifiez les empreintes dans `MANIFESTE_EXERCICES_INDIVIDUELS.json`. Ouvrez ensuite le dossier contenant `pyproject.toml` et `uv.lock` dans VS Code, puis suivez le pas-à-pas PayGuard. Ne mélangez pas cet environnement avec celui d'InduSense.

## 12. M31 et M32 - drift InduSense

Le TP autonome et ses scripts `drift_lab.py` et `evaluate_fenetre.py` sont
disponibles à partir du **jalon 09**. Avant toute commande ci-dessous, placez le
terminal dans `FORMATION/EXERCICES/tp_drift_indusense` (ou dans la copie courte
extraite du pack), c'est-à-dire le dossier qui contient son propre
`pyproject.toml`, son `uv.lock` et le sous-dossier `scripts`.

Utilisez un chemin local court :

| Système | Exemple |
|---|---|
| Windows | `C:\CISIA\S3\tp_drift_indusense` |
| macOS | `~/CISIA/S3/tp_drift_indusense` |
| Linux | `~/CISIA/S3/tp_drift_indusense` |

Préflight commun :

```text
uv sync --frozen --extra dev
uv run python --version
uv run python -m pytest tests -q -p no:cacheprovider
```

Les commandes Python sont communes si les chemins utilisent `/` :

```text
uv run python scripts/train_model.py
uv run python scripts/drift_lab.py --fenetre 1 --reference normale
uv run python scripts/drift_lab.py --fenetre 2 --reference normale
uv run python scripts/drift_lab.py --fenetre 3 --reference normale
uv run python scripts/drift_lab.py --fenetre janvier --reference normale
uv run python scripts/drift_lab.py --fenetre janvier --reference haute
uv run python scripts/alerting_demo.py --report-out reports/drift_report_f2.json
```

Lire le rapport et rechercher les garde-fous :

```powershell
# Windows
Get-Content -LiteralPath .\reports\drift_report_f2.json
Select-String -LiteralPath .\scripts\alerting_demo.py -Pattern 'drift_events','cooldown_hours','INSERT INTO'
```

```bash
# macOS et Linux
cat ./reports/drift_report_f2.json
grep -nE 'drift_events|cooldown_hours|INSERT INTO' ./scripts/alerting_demo.py
```

## 13. M33 et M34 - Prometheus, Grafana et Locust

Pour M33-M34, téléchargez `payload.json` et `locustfile.py.txt` depuis `05_DONNEES_ET_EXERCICES/PERFORMANCE_ET_DIVERS`, puis dans `VISION_METRICS` le guide R2, `pyproject.toml.txt`, `uv.lock.txt` et les deux PDF lisibles `lab.py.pdf` et `tests__test_lab.py.pdf`. Dendreo a refusé les deux sources Python exécutables : demandez-les au formateur avant de lancer le laboratoire ou ses tests. Placez le dossier local `PERFORMANCE_ET_DIVERS` à côté du clone avant les commandes suivantes ; vérifiez les empreintes dans le manifeste des exercices.

```powershell
# Windows, depuis la racine du dépôt CISIA
$projectRoot = (Get-Location).Path
$locustfile = (Resolve-Path -LiteralPath '..\PERFORMANCE_ET_DIVERS\locustfile.py').Path
$payload = (Resolve-Path -LiteralPath '..\PERFORMANCE_ET_DIVERS\payload.json').Path
@($projectRoot, $locustfile, $payload) | ForEach-Object { if (-not (Test-Path -LiteralPath $_)) { throw "Introuvable : $_" } }
```

```bash
# macOS ou Linux, depuis la racine du dépôt CISIA
project_root="$(pwd -P)"
locustfile="$(cd ../PERFORMANCE_ET_DIVERS && pwd -P)/locustfile.py"
payload="$(cd ../PERFORMANCE_ET_DIVERS && pwd -P)/payload.json"
for path in "$project_root" "$locustfile" "$payload"; do test -e "$path" || { echo "Introuvable : $path" >&2; exit 1; }; done
```

Terminal 1, commande commune à laisser active :

```text
uv run python scripts/export_drift_metrics.py
```

Terminal 2 :

```text
docker compose config -q
docker compose up -d --build
docker compose ps
```

Tester les métriques :

```powershell
# Windows
Invoke-WebRequest http://127.0.0.1:8000/metrics -UseBasicParsing
Invoke-WebRequest http://127.0.0.1:9109/metrics -UseBasicParsing
```

```bash
# macOS et Linux
curl -fsS http://127.0.0.1:8000/metrics | head
curl -fsS http://127.0.0.1:9109/metrics | head
```

Interfaces communes : Prometheus `http://127.0.0.1:9090/targets`, Grafana
`http://127.0.0.1:3000` et Locust `http://127.0.0.1:8089`.

Prometheus tourne dans un conteneur alors que l'exporteur drift tourne sur
l'hôte. Le nom `host.docker.internal` est automatique sur Docker Desktop. Pour
Docker Engine sous Linux, l'entrée suivante est déjà versionnée dans le service
`prometheus` ; vérifiez-la sans modifier le fichier pendant l'exercice :

```yaml
extra_hosts:
  - "host.docker.internal:host-gateway"
```

Vérification portable via l'API de Prometheus :

```powershell
# Windows
(Invoke-RestMethod http://127.0.0.1:9090/api/v1/targets).data.activeTargets |
  Select-Object -ExpandProperty health
```

```bash
# macOS et Linux
curl -fsS http://127.0.0.1:9090/api/v1/targets | uv run python -m json.tool
```

Lancer Locust depuis le même terminal où les chemins ont été définis :

```powershell
# Windows
uv run locust -f $locustfile --host http://127.0.0.1:8000
```

```bash
# macOS et Linux
uv run locust -f "$locustfile" --host http://127.0.0.1:8000
```

## 14. J6 - Game Day hors ligne

Depuis la racine du parcours :

```powershell
# Windows
powershell -ExecutionPolicy Bypass -File .\scripts\formation\demarrer_gameday.ps1 -Binome equipe-1
```

```bash
# macOS et Linux
bash scripts/formation/demarrer_gameday.sh equipe-1
```

Le script clone le bundle local, crée `reparation-equipe-1` et vérifie le tag
`v1.0-sain`. Il refuse une destination déjà présente. Ne fusionnez jamais la
branche cassée dans votre dépôt InduSense habituel.

## 15. Dépannage par système

### Port 8000 déjà occupé

```powershell
# Windows
Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
```

```bash
# macOS
lsof -nP -iTCP:8000 -sTCP:LISTEN
```

```bash
# Linux
ss -ltnp | grep ':8000 '
```

Identifiez d'abord le processus. Ne le terminez que s'il vous appartient et si
vous savez à quel exercice il correspond.

### Script shell illisible sous macOS ou Linux

Utilisez `bash scripts/...` comme indiqué. Si le message contient `$'\r'` ou
`bad interpreter`, le fichier a reçu des fins de ligne Windows : repartez du
jalon officiel au lieu de réécrire le script à la main.

### Chemin trop long ou synchronisé

- Windows : utilisez `C:\CISIA\S3`.
- macOS et Linux : utilisez `~/CISIA/S3`.
- Evitez OneDrive, iCloud Drive, un partage réseau et les chemins contenant de
  nombreuses imbrications pour les environnements Python et les volumes Docker.

### Différence entre l'hôte et un conteneur

`localhost` désigne la machine qui exécute la commande. Depuis votre navigateur,
`127.0.0.1:8000` vise le port publié sur l'hôte. Depuis Prometheus dans Compose,
`api:8000` vise le service `api`, et `host.docker.internal:9109` vise l'exporteur
qui tourne sur l'hôte.

## 16. Ce qui ne change pas selon le système

- mêmes fichiers source et même `uv.lock` ;
- mêmes versions Python et dépendances ;
- mêmes tests et critères de réussite ;
- mêmes statuts HTTP et mêmes preuves ;
- mêmes règles Git, sécurité et absence de secrets ;
- mêmes horaires, pauses et livrables.

Références techniques officielles consultées : documentation d'installation et
d'environnements `uv` sur `https://docs.astral.sh/uv/`, documentation Docker
Compose sur `https://docs.docker.com/compose/`.
