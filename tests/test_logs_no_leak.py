# [PÉDAGOGIE] ============================================================================
# [PÉDAGOGIE] FICHIER — tests/test_logs_no_leak.py
# [PÉDAGOGIE] MODULE  — M26 — TP 3 « preuve complémentaire » : non-divulgation dans les logs
# [PÉDAGOGIE] RÔLE    — Prouver que ni la clé d'API ni le contenu des requêtes n'apparaissent dans
# [PÉDAGOGIE]           les journaux (logs) de l'API, y compris sur les chemins d'erreur.
# [PÉDAGOGIE] THÉORIE — un log bavard est une fuite (menace « I » de STRIDE)
# [PÉDAGOGIE]           • on envoie des valeurs MARQUÉES, faciles à retrouver si elles fuient
# [PÉDAGOGIE]           • on capture TOUS les logs (loguru + logging standard) pendant les appels
# [PÉDAGOGIE]           • un second test vérifie que le détecteur sait trouver une fuite (sinon
# [PÉDAGOGIE]             « rien trouvé » ne prouverait rien)
# [PÉDAGOGIE] LIMITE  — Ce test NE PROUVE PAS qu'un audit logging existe : il reste Planifié v0.
# [PÉDAGOGIE] GARDE   — Toutes les lignes marquées [PÉDAGOGIE] sont des commentaires : elles
# [PÉDAGOGIE]           guident la lecture sans changer l'exécution.
# [PÉDAGOGIE] ============================================================================

import logging
from contextlib import contextmanager

import pandas as pd
from fastapi.testclient import TestClient
from loguru import logger

from indusense.api import security
from indusense.api.main import app
from indusense.api.model_store import ModelBundle, get_model_bundle
from indusense.config import settings
from indusense.features.temporal import add_temporal_features
from indusense.models.tabular import select_features, train_model

# [PÉDAGOGIE] MARQUEURS — valeurs inventées, uniques, faciles à repérer dans un texte de log.
FAKE_KEY = "cle-a-ne-pas-logger-123"
MARKED_MACHINE = "MACH-4242"
MARKED_TEMPERATURE = 123.456


def _bundle() -> ModelBundle:
    """Faux modèle jouet (même recette que `_bundle` de test_api.py), injecté à la place du vrai."""
    stamps = pd.date_range("2025-01-01", periods=60, freq="h")
    df = pd.DataFrame(
        {
            "machine": "MACH-01",
            "timestamp": stamps,
            "temperature": range(60),
            "pressure_bar": range(180, 240),
        }
    )
    df["panne"] = (df["temperature"] > 40).astype(int)
    feats = add_temporal_features(df).dropna()
    x, y = select_features(feats, "panne"), feats["panne"]
    return ModelBundle(
        model=train_model(x, y, n_estimators=10), version="test", threshold=0.5, target_col="panne"
    )


def _readings(n: int, temperature: float = 50.0) -> list[dict]:
    """Relevés horaires valides ; le dernier porte la température marquée."""
    stamps = pd.date_range("2025-02-01", periods=n, freq="h")
    rows = [
        {"timestamp": ts.isoformat(), "temperature": temperature, "pressure_bar": 195.0}
        for ts in stamps
    ]
    rows[-1]["temperature"] = MARKED_TEMPERATURE
    return rows


@contextmanager
def _captured_logs():
    """Capture tout ce qui est journalisé : loguru (avec son contexte) + logging standard."""
    lines: list[str] = []
    # [PÉDAGOGIE] loguru : on écrit le message ET le contexte (`extra`, ex. request_id).
    sink_id = logger.add(lambda msg: lines.append(str(msg)), format="{message} | {extra}")

    class _ListHandler(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            lines.append(f"{record.name}: {record.getMessage()}")

    handler = _ListHandler(level=logging.DEBUG)
    root = logging.getLogger()
    old_level = root.level
    root.addHandler(handler)
    root.setLevel(logging.DEBUG)
    try:
        yield lines
    finally:
        logger.remove(sink_id)
        root.removeHandler(handler)
        root.setLevel(old_level)


def _leaks(lines: list[str], secrets: list[str]) -> list[str]:
    """Renvoie les secrets retrouvés dans au moins une ligne de log."""
    return [secret for secret in secrets if any(secret in line for line in lines)]


def test_logs_do_not_leak_api_key_or_payload():
    """Aucun log ne contient la clé d'API ni les valeurs envoyées (200, 401 et 422)."""
    secrets = [settings.api_key, FAKE_KEY, MARKED_MACHINE, str(MARKED_TEMPERATURE)]
    security._hits.clear()  # [PÉDAGOGIE] quota remis à zéro : le test ne dépend pas des autres
    app.dependency_overrides[get_model_bundle] = _bundle
    try:
        with _captured_logs() as lines:
            # [PÉDAGOGIE] `with TestClient(app)` lance le démarrage (lifespan) : il journalise au
            # [PÉDAGOGIE] moins le chargement du modèle, donc la capture ne peut pas être vide.
            with TestClient(app) as client:
                ok = client.post(
                    "/predict-tabular",
                    headers={"X-API-Key": settings.api_key},
                    json={"machine_id": MARKED_MACHINE, "readings": _readings(8)},
                )
                wrong_key = client.post(
                    "/predict-tabular",
                    headers={"X-API-Key": FAKE_KEY},
                    json={"machine_id": MARKED_MACHINE, "readings": _readings(8)},
                )
                invalid = client.post(
                    "/predict-tabular",
                    headers={"X-API-Key": settings.api_key},
                    json={"machine_id": MARKED_MACHINE, "readings": _readings(3)},
                )
    finally:
        app.dependency_overrides.pop(get_model_bundle, None)
        security._hits.clear()

    # [PÉDAGOGIE] ORACLE 1 — les 3 chemins ont bien été parcourus (succès, clé refusée, invalide).
    assert (ok.status_code, wrong_key.status_code, invalid.status_code) == (200, 401, 422)
    # [PÉDAGOGIE] ORACLE 2 — la capture n'est pas vide : sinon « aucune fuite » ne prouverait rien.
    assert lines, "aucun log capturé : le test ne prouverait rien"
    # [PÉDAGOGIE] ORACLE 3 — aucun secret ni aucune valeur marquée dans les logs.
    assert _leaks(lines, secrets) == []


def test_leak_detector_catches_a_logged_secret():
    """Contrôle du détecteur : une valeur volontairement journalisée est bien retrouvée."""
    with _captured_logs() as lines:
        logger.info(f"fuite volontaire de test : {FAKE_KEY}")
    # [PÉDAGOGIE] ORACLE — si ce test échoue, le test précédent ne vaut rien.
    assert _leaks(lines, [FAKE_KEY]) == [FAKE_KEY]
