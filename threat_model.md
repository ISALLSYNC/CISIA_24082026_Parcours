# Threat model InduSense — M26

> Livrable M26, TP 1 (pas-à-pas R2, « TP 1 — Attack tree & contrôles testables »). Créé à la racine à partir du modèle
> [docs/threat_model.md](docs/threat_model.md), sur l'état du code du jalon 04 (29/09/2026, branche `ismael-sall`).
> Méthode **STRIDE** : 6 familles de menaces (usurpation, altération, déni d'action, fuite d'information, déni de
> service, élévation de privilège). Registre des contrôles : [security_controls.md](security_controls.md).
> Aucune clé, aucune valeur de `.env`, aucun payload réel et aucune donnée personnelle dans ce document.

## Actifs à protéger

- **Le service de prédiction** `/predict-tabular` : sa disponibilité et l'exactitude de ses réponses (une alerte ratée = panne non anticipée).
- **Le modèle** `artifacts/models/rf.joblib` (et `model_metadata.json`) : intégrité et confidentialité (un modèle recopié ou altéré).
- **La clé d'API** (`INDUSENSE_API_KEY`, valeur par défaut de développement dans `config.py`) : elle ouvre l'accès au service.
- **Les données** : relevés capteurs (entrée de l'API), Gold et sources brutes (`data/`) ; la source brute des incidents contient des **données personnelles** d'opérateurs (non utilisées par le modèle, voir Model Card).
- **La chaîne de livraison** : dépôt Git, CI GitHub Actions, remote DVC `localstore`.

## Frontières de confiance

- **Client → API** (HTTP, port 8000) : tout ce qui arrive du client est **non fiable** (en-têtes, corps, paramètres d'URL). C'est ici que s'appliquent clé, taille de corps, rate limit et validation.
- **API → disque** (chargement de `rf.joblib` au démarrage via `lifespan`) : on fait confiance au fichier modèle présent sur le serveur.
- **Données brutes → pipeline d'entraînement** (`data/raw` → Gold → modèle) : hors API, mais une donnée empoisonnée ici fausse tous les modèles suivants.
- **Poste développeur → Git / CI** : ce qui est commité et poussé devient visible et exécuté par la CI.

## Menaces STRIDE

### Sur `/predict-tabular`

| Menace | Scénario concret | Impact | Contrôle existant | Risque résiduel | Action |
|---|---|---|---|---|---|
| **S** — Usurpation | Un client non autorisé appelle `/predict-tabular` | Usage non maîtrisé du service, extraction du modèle | Clé `X-API-Key` → **401** (`require_api_key`) | La clé par défaut `dev-key` est **publique dans le code** ; une seule clé partagée, sans identité par client | Définir `INDUSENSE_API_KEY` hors du code (`.env` / secrets), une clé par client, rotation |
| **T** — Altération | Relevés truqués hors bornes (température 500, pression négative) ou trop courts | Décision faussée | Validation Pydantic v2 → **422** (bornes, ≥ 7 relevés) | Une valeur **dans les bornes** mais fausse (capteur trafiqué) passe | Contrôles de cohérence métier (variations brutales), surveillance du drift (M31-M32) |
| **R** — Déni d'action | Un client nie avoir demandé une prédiction qui a mené à une mauvaise décision | Impossible d'établir qui a fait quoi, quand | **Aucun** : `X-Request-ID` corrèle une requête, mais **n'est pas** un audit log et n'est pas journalisé | Répudiation possible | **Audit logging Planifié v0** : événement structuré (horodatage, route, code, request-id, client) **sans** clé, payload ni PII, + test dédié |
| **I** — Fuite d'information | Un message d'erreur ou un log révèle la clé, le payload ou des données personnelles ; un message 401 différent selon « clé absente » / « clé fausse » renseigne l'attaquant | Compromission de la clé, fuite de données | Même message 401 dans les deux cas (« Cle API absente ou invalide ») ; aucun log applicatif du payload ; `.env` ignoré par Git ; gitleaks en pre-commit | Le test `tests/test_logs_no_leak.py` (TP 3) prouve l'absence de fuite **sur les chemins testés** (200, 401, 422) et pour le code **actuel** ; un nouveau log ajouté ailleurs n'est couvert que s'il passe par ces chemins | Garder le test en CI (il échoue si la clé ou le payload apparaît : vérifié par mutation) ; règle : ne jamais journaliser clé / payload / PII |
| **D** — Déni de service | Inonder l'API de requêtes, ou envoyer un corps énorme | Service indisponible pour la maintenance | Rate limit 60 req/min/IP → **429** ; corps > 64 Ko → **413** ; `Content-Length` illisible → **400** | Limite de corps **déclarative** (un client qui omet ou ment sur `Content-Length` passe) ; compteur **en mémoire, par processus et par IP** (plusieurs processus ou un proxy commun l'affaiblissent) | Limite effective au reverse-proxy ou comptage des octets reçus ; compteur partagé (Redis) si plusieurs instances |
| **E** — Élévation de privilège | Désactiver le quota en ajoutant `?limit=100000` à l'URL | Contournement du rate limit | `rate_limit_dependency` **fermée** : signature `(request)` seule, `limit` / `window` non exposés (test `test_rate_limit_policy_is_not_exposed_as_query_parameters`) | Faible sur ce point | Garder la règle : brancher `Depends(rate_limit_dependency)`, jamais `Depends(rate_limit)` |

### Menaces propres au ML

| Menace | Scénario concret | Impact | Contrôle existant | Risque résiduel | Action |
|---|---|---|---|---|---|
| Entrée **adversariale** | Relevés choisis **dans les bornes** pour obtenir « ok » alors que la machine dérive | Panne non détectée | Validation des bornes seulement | Non couvert | Tests de robustesse ; ne jamais décider sans humain (Model Card) |
| **Extraction** du modèle | Milliers de requêtes pour reconstruire un modèle équivalent | Perte de la valeur du modèle | Clé + rate limit (freine) | Une clé valide et patiente peut extraire lentement | Quotas par client, surveillance des volumes (M33) |

### Sur le pipeline (hors API)

| Menace | Scénario concret | Impact | Contrôle existant | Risque résiduel | Action |
|---|---|---|---|---|---|
| **T** — Empoisonnement des données | Modifier `data/raw` ou le Gold avant un réentraînement | Modèle faussé pour tous | Gold versionné par DVC (md5 `637be8d…` dans le pointeur) : un changement est **visible** (`dvc status`) | Rien n'**empêche** la modification, on la détecte seulement ; remote local non protégé | Revue des changements de données, remote DVC à accès contrôlé |
| **T** — Altération du modèle | Remplacer `rf.joblib` sur le serveur | Prédictions arbitraires | md5 du modèle dans `rf.joblib.dvc` ; tag `gold_md5` et `git.commit` dans MLflow | L'API **ne vérifie pas** le md5 au chargement | Vérifier l'empreinte au démarrage (`/ready` en 503 si elle diffère) |
| **I** — Fuite de secrets par Git | Commiter une clé ou un `.env` | Clé compromise à vie (historique) | `.env` dans `.gitignore` ; **gitleaks** en pre-commit et pre-push | Contournable (`--no-verify`) ; pas de scan de l'historique complet | Ajouter gitleaks en CI ; révoquer toute clé commitée |
| **I** — Données personnelles | La source brute des incidents contient nom, badge, commentaire, équipe d'opérateurs | Atteinte à la vie privée | `load_incidents` ne garde que `machine` et `incident_ts` : aucune PII dans le Gold, le modèle ou l'API | La source brute est dans le dépôt | Pseudonymiser ou retirer ces colonnes à la source ; avis du référent conformité |

## Priorisation : les 5 contrôles

Ordre de priorité (impact × facilité d'exploitation sur `/predict-tabular`) :

1. **Auth** (401) — sans elle, tout le reste est accessible à n'importe qui.
2. **Validation** (422) — refuse les entrées absurdes avant le modèle.
3. **Rate limit** (429) — limite le déni de service et l'extraction.
4. **Taille payload** (413) — évite l'épuisement mémoire par un corps géant.
5. **Audit logging** — traçabilité (répudiation) : **Planifié v0**, pas encore implémenté.

Statut, preuve et risque résiduel de chacun : [security_controls.md](security_controls.md).

## Hors périmètre et hypothèses

- `/health` reste **volontairement ouvert** (sans clé) : c'est la sonde de liveness de l'orchestrateur ; la protéger casserait le monitoring. Il ne renvoie que `{"status":"ok"}`.
- Pas de HTTPS : l'API écoute sur `127.0.0.1` (poste de développement). En production, le chiffrement se ferait au reverse-proxy.
- La conteneurisation (image non-root, secrets hors image) est traitée au **M27**.
- Hypothèse : le serveur et son disque sont de confiance ; les attaques physiques et système sont hors périmètre.
- Analyse faite par lecture du code du jalon 04 et des tests ; les risques marqués « déduit » n'ont pas été testés.
