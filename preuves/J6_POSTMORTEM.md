# Post-mortem Game Day — indusense-gameday · solo : ismael-sall

> Branche de réparation : `reparation-ismael-sall` · branche cassée `J6-gameday` (`4f78a52`) ·
> état certifié `v1.0-sain` (`88d5af5`) · journée du 20/10/2026.
> Règle suivie : diagnostiquer → corriger → prouver → commiter.

## Résumé et impact

- **Incident** : une « maintenance du week-end » (`b2711eb`) a introduit **15 défauts** répartis dans
  6 familles (environnement, documentation, données, features, API / sécurité, infra, CI), dont un
  test affaibli et une CI rendue incapable d'échouer.
- **Impact** : installation impossible pour tout nouvel arrivant (Python 3.99) · pipeline qui **perdait
  372 lignes** en silence et **fuyait** l'information du futur · API qui refusait les clés valides et
  bloquait dès la 3ᵉ requête · supervision aveugle (API et Grafana injoignables, cible drift DOWN) ·
  statut CI vert **sans valeur**.
- **Résultat** : 15 pannes réparées en **22 commits** sur `reparation-ismael-sall` · `pytest` **32
  passed** avec des tests **identiques à `v1.0-sain`** · jointure **65 625 lignes / 1,76 %** · API
  200 / 401 / 429 · **2 cibles UP** · Grafana sur 3000. Seuls diffèrent encore de `v1.0-sain` : le
  durcissement légitime (actions CI, Dockerfile, dépendances, `uv.lock`) et le briefing officiel.

### Qui aurait attrapé chaque panne ? (la leçon de la journée)

| Détection possible | Pannes | Nombre |
|---|---|---|
| **CI**, si elle avait tourné honnêtement (PR, sans `\|\| true`) | 1, 4, 5, 7, 8, 9, 11 | 7 |
| **Revue de code** seulement | 2, 6, 10, 12, 13, 14, 15 | 7 |
| **Rien de fiable** aujourd'hui | 3 | 1 |

Une seule panne sur les « gardiens » (15 : `|| true`) neutralisait les 7 détections de la CI.

## Chronologie horodatée

| Heure | Observation ou action | Preuve | Décision |
|---|---|---|---|
| 11:25 | Jalon 11 intégré dans Parcours ; bundle vérifié (SHA-256 conforme) | `Jalon verifie : jalon/11` | Démarrer le Game Day |
| 11:27 | Clone `CISIA_J6_GAMEDAY_ismael-sall` créé, branche `reparation-ismael-sall` | `demarrer_gameday.ps1` → « Game Day pret » | Phase 0 : observer sans toucher |
| 11:30 | 4 commits entre `v1.0-sain` et `J6-gameday` ; seul remote `bundle-local` (push désactivé) | `git log --oneline --decorate`, `git remote -v` | Ne jamais pousser vers le bundle |
| 11:31 | « maintenance du week-end » (`b2711eb`) touche **12 fichiers dans 6 familles**, dont le code, un test et la CI | `git show --name-status b2711eb` | Suspect principal ; trier aussi les 3 commits de « durcissement » |
| 11:32 | 15 fichiers modifiés au total ; 1 créé (`BRIEFING.md`), 0 supprimé ou renommé | `git diff --stat --summary v1.0-sain J6-gameday` | Classement par familles ci-dessous |
| 11:40 | **Phase 1** — `uv sync --frozen --extra dev` échoue : « No interpreter found for Python >=3.99, <4.0 » | message d'erreur uv | Lire `pyproject.toml` et son historique |
| 11:43 | `requires-python` changé par `b2711eb` seulement ; `2871686` a déplacé des dépendances **avec** mise à jour de `uv.lock` (légitime) | `git show <commit> -- pyproject.toml` | Corriger **une ligne**, garder le durcissement ; Python 3.13 (seul compatible avec `uv.lock` `==3.13.*`) |
| 11:47 | Correctif appliqué : `uv sync` OK, Python 3.13.15, `import indusense` OK, `uv.lock` inchangé | commit `7c20663` | Passer au README |
| 11:50 | README : `uv sync --extra all` (extra inexistante, sans `--frozen`) ; tag `v1.1-sain` cité alors qu'absent | `git tag` → `v1.0-sain` seul ; extras = `dev`, `mlops` | Restaurer la commande certifiée et `v1.0-sain` |
| 11:53 | README corrigé, commande re-jouée : code 0, verrou intact | commit `07bd322` | Chercher `v1.1-sain` ailleurs |
| 11:56 | `v1.1-sain` aussi dans `BRIEFING.md` et `CONTRIBUTING.md`, en contradiction avec le briefing officiel du kit | `git grep v1.1-sain` → 6 lignes | Aligner les deux fichiers sur `v1.0-sain` |
| 11:57 | Plus aucune mention de `v1.1-sain` ; `CONTRIBUTING.md` identique à `v1.0-sain` | commit `d208af6` · `git grep` → 0 | **Phase 1 terminée** → phase 2 |
| 12:00 | **Phase 2** — loaders / temporel : **3 failed, 10 passed** | `pytest tests/test_loaders.py tests/test_temporal.py tests/test_temporal_gold.py` | Traiter un échec à la fois |
| 12:01 | `loaders.py` : 3 sabotages (padding, UTC, tolérance 90 → 5) | `git diff v1.0-sain -- loaders.py` | Corriger dans l'ordre des tests |
| 12:03 | `M-2` → `MACH-2` au lieu de `MACH-02` → padding restauré | commit `15dc32f` · 5 variantes vertes | — |
| 12:05 | `TypeError: can't compare offset-naive and offset-aware` → `utc=True` restauré | commit `86a8ac3` · test vert | Le commit avait d'abord échoué (guillemets) → message passé par fichier |
| 12:07 | Tolérance 5 min : **65 253** lignes, **2,32 %** (aucun test rouge) vs 90 min : **65 625**, **1,76 %** | mesure sur `data/drift_source` | Restaurer 90 min — commit `70941e3` |
| 12:09 | `roll2_mean` = 25,0 au lieu de 15,0 : `shift(1)` supprimé (fuite temporelle) | `git diff v1.0-sain -- temporal.py` | Restaurer — commit `6ef8f13` (BOM ajouté par erreur) puis `aa56d66` (octet pour octet) |
| 12:10 | **13 passed** ; `loaders.py` et `temporal.py` identiques à `v1.0-sain` | pytest · `git diff v1.0-sain` vide | **Phase 2 terminée** → pause déjeuner |
| 13:44 | **Phase 3** — suite complète : **5 failed, 27 passed** (4 × 401 dans `test_api`, 1 verdict PSI) | `uv run pytest -q` | Vérifier le rapport d'astreinte avant d'agir |
| 13:45 | Rapport d'astreinte **confirmé** mais **mal interprété** : la clé n'a pas changé, l'en-tête oui (`X-Api-Token`) ; rate limit à 2/min ; test de sécurité affaibli | `git diff v1.0-sain -- api/ tests/test_security.py` | Corriger code, puis restaurer le test |
| 13:47 | En-tête `X-API-Key` restauré → encore **2 échecs 429** (message de commit trop optimiste) | commit `f614ceb` · pytest | Le rate limit bloque la suite |
| 13:47 | Rate limit 60 / 60 s restauré → `test_api` + `test_security` : 10 passed | commit `3cd6683` | Restaurer le test affaibli |
| 13:48 | Assertion `in (200, 429)` → `== 429` restaurée depuis `v1.0-sain` | commit `4e50236` · `git diff v1.0-sain -- tests/` vide | Test de nouveau capable d'échouer |
| 13:49 | Seuils PSI inversés (0,25 / 0,10) → restaurés (0,10 / 0,25) | commit `4c0ea41` · 0,18 → « à surveiller » | — |
| 13:49 | **32 passed**, tests identiques à `v1.0-sain` | `uv run pytest -q` | **Phase 3 terminée** → phase 4 |
| 13:51 | **Phase 4A** — `drift_windows.py` : **64 535** lignes, panne_v1 5,18 %, réelle 4,81 % | sortie du script | Conforme |
| 13:52 | `train_drift_model.py` : seuil **0,04** (support : 0,03) ; rappels F1/F2/F3/janv. 0,753 / 0,738 / 0,051 / 0,802 (support : 0,822 / 0,811 / 0,092 / 0,868) ; PSI F2 **6,834**, F3 0,002, janv. 6,203 / 0,001 | `evaluate_drift.py` ×5 | Chercher la cause avant de « corriger » |
| 13:54 | Hypothèse « dépendances mises à jour » **réfutée** : scikit-learn, NumPy, pandas, SciPy, joblib identiques dans les deux `uv.lock` | comparaison des verrous | — |
| 13:55 | **L'état certifié lui-même** contient `"seuil": 0.04` et les mêmes rappels (`v1.0-sain:artifacts/drift_threshold.json`, `suivi_fenetres.csv`) ; même résultat sur mon dépôt Parcours (M34) | `git show v1.0-sain:…` | **Pas de panne** : écart entre le support et le tag certifié → question au formateur |
| 13:56 | Fichiers régénérés (contenu équivalent, CRLF / ordre) restaurés à l'état certifié | `git restore` · clone propre | **Phase 4A terminée** → 4B |
| 13:57 | Stack Parcours (M33-M34) et son exporteur arrêtés pour libérer 8000 / 9090 / 3000 / 9109 | `docker compose down` (sans `-v`) · ports libres | Démarrer la stack du Game Day |
| 14:00 | `.env` créé depuis `.env.example`, ignoré par Git ; `docker compose config --quiet` OK ; `up -d --build` (222 s) | `git check-ignore .env` | Tester maillon par maillon |
| 14:01 | Exporteur 200 · API **injoignable** depuis l'hôte mais **200 à l'intérieur** du conteneur · cible drift **DOWN** (`localhost:9109`) · Grafana muet sur 3000, **répond sur 300** | `curl` par maillon · page Targets | 3 pannes de câblage |
| 14:02 | Diff confirmé : `8000:80`, `300:3000`, `targets: ["localhost:9109"]` | `git diff v1.0-sain -- docker-compose.yml monitoring/prometheus.yml` | Corriger un par un |
| 14:03 | Correctifs `6f6a756`, `3cf041b`, `fe30d9c` appliqués (recréation api / grafana, redémarrage Prometheus) | `/health` 200 · `/ready` 200 · **2 cibles UP** · Grafana 200 sur 3000 | — |
| 14:04 | API : sans clé **401**, avec `X-API-Key` **200**, `X-Api-Token` 401 ; rafale : 59 × 200 puis **429** (60 / min) ; dashboard drift alimenté (10 séries) | requêtes HTTP · Prometheus | **Phase 4 terminée** → phase 5 |
| 14:05 | **Phase 5** — `git diff v1.0-sain -- .github/` : la maintenance a remplacé `uv run pytest -q` par **`uv run pytest -q \|\| true`** ; le reste (versions d'actions, `--extra mlops`, Trivy) vient du durcissement | diff par commit | Prouver avant de corriger |
| 14:06 | Déclencheurs **inchangés** : `push` sur `main` + `pull_request` → **aucun contrôle n'a tourné** sur la branche de maintenance ; le vert d'Actions était celui de `main` | bloc `on:` des deux versions | 1ʳᵉ « chose invisible » dans un diff |
| 14:07 | Test volontairement faux : avec `\|\| true` → code **0** (vert) ; sans → code **1** (rouge) | `bash` hors dépôt | 2ᵉ « chose invisible » : un statut vert qui ne prouve rien |
| 14:08 | Restaurer le workflow **à l'identique** casserait la CI : les tests drift importent SciPy, déplacé dans l'extra `mlops` | `pyproject.toml` · `drift.py` | Retirer **seulement** `\|\| true` — commit `0fb7cef` |
| 14:09 | Étapes CI rejouées localement : install, ruff, black, pytest → code 0, **32 passed** ; branche propre, **22 commits** ; seul reste vs `v1.0-sain` = durcissement légitime + briefing officiel | `git status` · `git diff --stat v1.0-sain` | **Phase 5 terminée** → post-mortem et restitution |

### Classement des fichiers modifiés (phase 0)

| Famille | Fichiers |
|---|---|
| Environnement | `pyproject.toml`, `uv.lock` |
| Documentation | `README.md`, `CONTRIBUTING.md`, `BRIEFING.md` |
| Code | `src/indusense/api/main.py`, `api/security.py`, `data/loaders.py`, `features/temporal.py`, `monitoring/drift.py` |
| Tests | `tests/test_security.py` |
| Infra | `docker-compose.yml`, `monitoring/prometheus.yml`, `Dockerfile` |
| CI | `.github/workflows/ci.yml` |

## Pannes traitées

| # | Symptôme observé | Cause racine | Correctif (commit) | Comment l'éviter ? |
|---|---|---|---|---|
| 1 | Installation impossible : « No interpreter found for Python >=3.99 » | `requires-python` passé à `>=3.99,<4.0` (version inexistante) dans `b2711eb` | Retour à `>=3.13,<3.14` — `7c20663` | CI `uv sync --frozen` bloquante ; revue obligatoire de `pyproject.toml` |
| 2 | README : commande d'installation non reproductible | `uv sync --extra all` : extra inexistante, `--frozen` retiré (`b2711eb`) | Commande certifiée `uv sync --frozen --extra dev --extra mlops` — `07bd322` | Tester les commandes de la doc en CI |
| 3 | Documentation renvoyant vers un point de retour introuvable | Tag `v1.1-sain` cité dans README, BRIEFING, CONTRIBUTING (`7e55d6a`, `4f78a52`), absent du dépôt | Alignement sur `v1.0-sain` et le briefing officiel — `07bd322`, `d208af6` | Vérifier en CI que tout tag cité existe |
| 4 | `M-2` normalisé en `MACH-2` (test rouge) | padding `:02d` retiré dans `normalize_machine_id` : une machine, deux noms → mesures orphelines | `15dc32f` | Test paramétré sur les variantes (existait) |
| 5 | `TypeError` naïf / tz-aware dans la jointure | `utc=True` + `tz_localize(None)` retirés dans `load_pressure` | `86a8ac3` | Contrat temporel explicite (UTC) testé |
| 6 | **Silencieux** : 65 253 lignes, résidu 2,32 % | tolérance `merge_asof` 90 → 5 min | `70941e3` | **Test de volumétrie** sur les chiffres certifiés (65 625 / 1,76 %) — absent aujourd'hui |
| 7 | Fuite temporelle : `roll2_mean` 25,0 au lieu de 15,0 | `shift(1)` supprimé avant `rolling` | `6ef8f13` + `aa56d66` | Test anti-fuite (existait) ; revue obligatoire de `features/` |
| 8 | API : 401 avec une clé valide (rapport d'astreinte) | en-tête `X-API-Key` renommé `X-Api-Token` dans le code seul (doc, tests, config inchangés) | `f614ceb` | Le contrat d'en-tête est une constante unique, testée |
| 9 | 429 dès la 3ᵉ requête | `rate_limit` abaissé de 60 à **2** requêtes / min (déni de service auto-infligé) | `3cd6683` | Politique de débit versionnée et testée sur sa valeur |
| 10 | **Test vert pour de mauvaises raisons** | assertion affaiblie en `in (200, 429)` (« TODO : test instable ? ») | `4e50236` (restauration depuis `v1.0-sain`) | **Protection de `tests/`** (revue obligatoire, CODEOWNERS) ; comparer `tests/` au tag certifié |
| 11 | `verdict_psi(0.18)` = « OK RAS » | seuils PSI inversés : bande « à surveiller » inatteignable | `4c0ea41` | Test des 3 bandes (existait) |
| 12 | API injoignable depuis l'hôte (200 à l'intérieur) | publication `8000:80` au lieu de `8000:8000` | `6f6a756` | Smoke test Compose sur le port **publié** en CI |
| 13 | Grafana muet sur :3000 | publication `300:3000` | `3cf041b` | Smoke test des interfaces sur leurs ports documentés |
| 14 | Cible Prometheus `indusense-drift` DOWN | `localhost:9109` = le conteneur Prometheus lui-même ; il faut `host.docker.internal:9109` | `fe30d9c` | Alerte « cible DOWN » (`up < 1`) sur chaque job |
| 15 | **CI verte alors que tout était cassé** | (a) CI déclenchée seulement sur `main` / PR : rien n'a tourné sur la branche ; (b) étape Tests en `pytest -q \|\| true` : code retour avalé | `0fb7cef` | **Protection de `.github/`** (revue obligatoire) ; CI exigée sur toute PR ; interdire `\|\| true` sur une étape de contrôle |
| — | *Non-panne* : seuil 0,04 et rappels ≠ support (0,03 ; 0,822…) | l'**état certifié** contient lui-même 0,04 et ces rappels ; écart du support | aucun (ne pas « corriger » un état certifié) | Question au formateur |

## Cause racine et facteurs contributifs

- **Cause racine prouvée** : un commit de « maintenance » non relu (`b2711eb`, 12 fichiers dans 6
  familles) a modifié en même temps le code, un test **et** la CI, sur une branche où **aucun contrôle
  ne se déclenchait** (CI limitée à `main` et aux PR).
- **Facteurs contributifs** : `|| true` dans l'étape Tests · test de rate limit affaibli
  (`in (200, 429)`) · absence de test de volumétrie (panne 6 invisible) · absence de smoke test de la
  stack en CI (pannes 12 à 14) · documentation renvoyant vers un tag inexistant (`v1.1-sain`).
- **Ce qui a limité l'impact** : le tag certifié `v1.0-sain` (point de comparaison et source de
  restauration) · les **chiffres certifiés** (65 625 / 1,76 %) · des tests existants qui échouaient
  dès qu'on les lançait · un bundle Git local, utilisable sans GitHub.

## Détection, restauration et rollback

- **Signal initial** : `uv sync --frozen --extra dev` → « No interpreter found for Python >=3.99 ».
- **Correctif** : 15 correctifs ciblés, un par commit, en restaurant chaque ligne sabotée depuis
  `v1.0-sain` sans annuler le durcissement légitime ; tests restaurés par `git restore --source v1.0-sain`.
- **Test de restauration** : `pytest -q` 32 passed · `git diff v1.0-sain -- tests/` vide · jointure
  65 625 / 1,76 % · stack : `/health` et `/ready` 200, 2 cibles UP, Grafana 200, 401 / 200 / 429.
- **Test de rollback** : non joué. Le point de retour existe (`v1.0-sain`, vérifié par `git tag`) ;
  la documentation pointe désormais vers lui et non vers `v1.1-sain`.

## Ce qui m'a fait perdre / gagner du temps

- **Gagné** : comparer **systématiquement** au tag certifié (`git diff v1.0-sain`) · traiter **un
  échec à la fois** · tester la stack **maillon par maillon** au `curl` (l'API marchait, seul son port
  publié était faux) · vérifier le rapport d'astreinte au lieu de le croire.
- **Perdu** : des pièges d'outillage Windows / PowerShell (guillemets dans un message de commit, BOM
  ajouté par une redirection, échappement `%%`) ; une hypothèse fausse (« les dépendances ont changé »)
  avant de trouver que l'état certifié contenait lui-même le seuil 0,04.

## Les 3 choses que je retiens

1. **La CI ne peut pas tout voir : attention à la confiance aveugle.** Un statut vert ne prouve que
   ce que ses étapes et ses déclencheurs contrôlent réellement ; ici, elle n'avait même pas tourné,
   et `|| true` l'aurait rendue verte de toute façon.
2. **La revue de code reste indispensable.** 7 pannes sur 15 n'étaient visibles qu'en relisant le
   diff, surtout sur les fichiers « gardiens » (`tests/`, `.github/`) et la configuration.
3. **Un état certifié chiffré vaut plus qu'un test vert.** La panne 6 (372 lignes perdues) ne faisait
   échouer aucun test : seuls les chiffres 65 625 et 1,76 % l'ont révélée.

## Actions préventives

| Action | Priorité | Responsable | Échéance | Preuve de clôture |
|---|---|---|---|---|
| Déclencher la CI sur **toute** branche poussée et rendre la PR obligatoire avant fusion | P0 | équipe dev | immédiat | run CI visible sur une branche de test |
| Interdire `\|\| true` (et tout code retour avalé) dans les étapes de contrôle | P0 | équipe dev | immédiat | règle de revue + contrôle du workflow |
| **Revue obligatoire** (CODEOWNERS) sur `tests/`, `.github/`, `pyproject.toml`, `docker-compose.yml`, `monitoring/` | P0 | responsable technique | 1 semaine | branche protégée configurée |
| **Test de volumétrie** : jointure = 65 625 lignes, résidu 1,76 % | P1 | data | 1 semaine | test rouge si la tolérance change |
| **Smoke test de la stack** en CI : `/health` sur le port publié, cibles Prometheus UP, Grafana | P1 | ops | 2 semaines | job CI vert / rouge selon le câblage |
| Exécuter en CI les commandes du README et vérifier que les tags cités existent | P2 | équipe dev | 1 mois | job « doc » dans la CI |
| Écart support / état certifié (seuil 0,03 vs 0,04, rappels) | P2 | formateur | — | réponse du formateur |
