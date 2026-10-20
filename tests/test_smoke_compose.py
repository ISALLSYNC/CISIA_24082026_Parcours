# [PÉDAGOGIE] ============================================================================
# [PÉDAGOGIE] FICHIER — tests/test_smoke_compose.py
# [PÉDAGOGIE] MODULE  — M28 — smoke tests de la stack Docker Compose
# [PÉDAGOGIE] RÔLE    — Vérifier, sur la VRAIE stack démarrée (conteneur, réseau, port publié),
# [PÉDAGOGIE]           que l'essentiel répond : /health 200, prédiction 401 sans clé, 200 avec.
# [PÉDAGOGIE] THÉORIE — un smoke test (« test de fumée ») est court et rapide : on allume, on
# [PÉDAGOGIE]           vérifie qu'il n'y a « pas de fumée », avant des tests plus poussés
# [PÉDAGOGIE]           • contrairement aux tests du M25 (TestClient, en mémoire), il passe par HTTP
# [PÉDAGOGIE]           • la clé vient du .env (settings), jamais écrite dans le test
# [PÉDAGOGIE] PIÈGE   — Ce test dépend du réseau : sans stack lancée (CI GitHub), il est SAUTÉ, pas
# [PÉDAGOGIE]           échoué. Il ne prouve donc quelque chose que stack démarrée.
# [PÉDAGOGIE] GARDE   — Toutes les lignes marquées [PÉDAGOGIE] sont des commentaires : elles
# [PÉDAGOGIE]           guident la lecture sans changer l'exécution.
# [PÉDAGOGIE] ============================================================================

"""Smoke tests M28 : la stack Compose démarrée répond correctement."""

from __future__ import annotations

import json
from pathlib import Path

import httpx
import pytest

from indusense.config import settings

# [PÉDAGOGIE] CIBLE — l'API publiée par Compose sur le port 8000 du PC (ports: ["8000:8000"]).
BASE_URL = "http://127.0.0.1:8000"
# [PÉDAGOGIE] ENTRÉE — la même requête valide qu'aux M25 et M27 (8 relevés de MACH-07).
PAYLOAD = json.loads((Path(__file__).resolve().parents[1] / "payload.json").read_text("utf-8"))
EXPECTED_FIELDS = {"machine_id", "proba_panne", "decision", "model_version", "threshold"}


def _stack_is_up() -> bool:
    """La stack Compose est-elle lancée ? Sinon on SAUTE les tests au lieu d'échouer."""
    try:
        return httpx.get(f"{BASE_URL}/health", timeout=2).status_code == 200
    except httpx.HTTPError:
        return False


# [PÉDAGOGIE] GARDE — appliqué aux 3 tests du fichier : en CI (pas de Compose), ils sont sautés.
pytestmark = pytest.mark.skipif(not _stack_is_up(), reason="stack Compose non démarrée")


def test_health_returns_200() -> None:
    """La liveness de l'API conteneurisée répond 200."""
    assert httpx.get(f"{BASE_URL}/health", timeout=5).status_code == 200


def test_predict_without_key_returns_401() -> None:
    """Sans clé d'API, la prédiction est refusée (garde-fou M26 actif dans la stack)."""
    response = httpx.post(f"{BASE_URL}/predict-tabular", json=PAYLOAD, timeout=5)
    assert response.status_code == 401


def test_predict_with_key_returns_200() -> None:
    """Avec la clé du .env, la prédiction répond 200 et respecte le contrat de sortie."""
    response = httpx.post(
        f"{BASE_URL}/predict-tabular",
        json=PAYLOAD,
        headers={"X-API-Key": settings.api_key},
        timeout=10,
    )
    assert response.status_code == 200
    # [PÉDAGOGIE] ORACLE — un 200 vide ne serait pas une réussite : on vérifie les 5 champs.
    assert set(response.json()) == EXPECTED_FIELDS
