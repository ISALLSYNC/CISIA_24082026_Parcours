# Registre des contrôles de sécurité — M26

> Livrable M26, TP 1. Créé à la racine à partir du modèle [docs/security_controls.md](docs/security_controls.md).
> Menaces associées : [threat_model.md](threat_model.md). Règle : **ne jamais marquer un contrôle « Implémenté » sans
> test rejouable**. Aucune clé ni valeur de `.env` dans ce registre.

| Contrôle | Statut | Code | Preuve actuelle | Risque résiduel | Action suivante |
|---|---|---|---|---|---|
| Auth | Implémenté | 401 | `tests/test_api.py::test_missing_api_key_returns_401` ; `require_api_key` (`src/indusense/api/main.py`) ; message identique clé absente / invalide | Clé de développement par défaut publique dans `config.py` ; une seule clé partagée | Définir `INDUSENSE_API_KEY` hors du code ; une clé par client ; rotation |
| Validation | Implémenté | 422 | `tests/test_api.py::test_insufficient_readings_returns_422` et `::test_predict_invalid_machine_id_returns_422` ; schémas Pydantic v2 (`src/indusense/api/schemas.py`) | Une valeur dans les bornes mais fausse passe (entrée adversariale) | Contrôles de cohérence métier ; surveillance du drift (M31-M32) |
| Rate limit | Implémenté | 429 | `tests/test_security.py::test_rate_limit_blocks_after_limit` (60 acceptées, 61ᵉ bloquée) et `::test_rate_limit_policy_is_not_exposed_as_query_parameters` ; `rate_limit_dependency` (`src/indusense/api/security.py`) | Compteur en mémoire, par processus et par IP (déduit du code) | Compteur partagé si plusieurs instances ; quotas par client |
| Taille payload | Implémenté | 413 | `tests/test_security.py::test_payload_too_large_returns_413` et `::test_invalid_content_length_returns_400` ; `limit_body_size`, `MAX_BODY_BYTES = 64 * 1024` | Contrôle déclaratif : un client qui omet ou falsifie `Content-Length` passe | Limite effective au reverse-proxy ou comptage des octets reçus |
| Audit logging | Planifié v0 | — | Aucune : aucun événement d'audit ni test dédié dans le code (vérifié : aucune occurrence de « audit ») | Répudiation possible : on ne peut pas établir qui a demandé quoi, quand | Événement structuré (horodatage, route, code, `X-Request-ID`, client) **sans** clé, payload ni PII, et un test dédié |

- **4 × Implémenté** (401, 422, 429, 413) et **1 × Planifié v0** (audit logging). L'audit logging n'a pas de code HTTP propre.
- Le `X-Request-ID` **n'est pas** un audit log : il corrèle les requêtes, sans constituer un événement d'audit ni sa preuve.
- `/health` reste libre (liveness) ; `/predict-tabular` et `/predict-image` exigent la clé et le quota.
