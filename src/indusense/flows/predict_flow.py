# [PÉDAGOGIE] ============================================================================
# [PÉDAGOGIE] FICHIER — src/indusense/flows/predict_flow.py
# [PÉDAGOGIE] MODULE  — M30 — implémentation du flow (design figé au M29 : docs/flow_design.md)
# [PÉDAGOGIE] RÔLE    — Enchaîner ingest → feature → predict → store et historiser les
# [PÉDAGOGIE]           prédictions dans la table `predictions`, SANS DOUBLON à la relance.
# [PÉDAGOGIE] THÉORIE — idempotence = clé naturelle (machine, prediction_ts) + UPSERT
# [PÉDAGOGIE]           • 2 runs sur la même base → même count(*)
# [PÉDAGOGIE]           • seul `store` touche une ressource externe → seul `store` réessaie,
# [PÉDAGOGIE]             et uniquement sur erreur TRANSITOIRE (base injoignable)
# [PÉDAGOGIE] BASE    — choisie par la variable d'environnement INDUSENSE_DB_URL :
# [PÉDAGOGIE]           • sqlite:///C:/chemin/predictions_flow.db      (développement, hôte)
# [PÉDAGOGIE]           • postgresql+psycopg://…@db:5432/indusense     (preuve, dans Compose)
# [PÉDAGOGIE]           Le même SQL d'upsert fonctionne dans les deux bases.
# [PÉDAGOGIE] LANCER  — $env:INDUSENSE_DB_URL = "sqlite:///C:/…/predictions_flow.db"
# [PÉDAGOGIE]           $env:PREFECT_PROFILE = "ephemeral"
# [PÉDAGOGIE]           uv run python -m indusense.flows.predict_flow
# [PÉDAGOGIE] DONNÉES — INDUSENSE_DATA_DIR (défaut data/raw). Le jeu COMPLET (15 machines) donne
# [PÉDAGOGIE]           15 lignes ; l'échantillon du dépôt (4 machines) en donne 4.
# [PÉDAGOGIE] PIÈGE   — Le flow ne réécrit AUCUNE logique métier : il appelle la lib testée
# [PÉDAGOGIE]           (loaders, features, modèle). Il ne fait qu'ORCHESTRER.
# [PÉDAGOGIE] GARDE   — Toutes les lignes marquées [PÉDAGOGIE] sont des commentaires : elles
# [PÉDAGOGIE]           guident la lecture sans changer l'exécution.
# [PÉDAGOGIE] ============================================================================

"""Flow M30 : ingest → feature → predict → store, idempotent par upsert."""

from __future__ import annotations

import os
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pandas as pd
from prefect import flow, get_run_logger, task
from prefect.cache_policies import NO_CACHE
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

from indusense.config import settings
from indusense.data.loaders import (
    build_dataset,
    load_incidents,
    load_pressure,
    load_temperature,
)
from indusense.features.temporal import add_temporal_features
from indusense.models.tabular import load_model, predict_proba, select_features

# [PÉDAGOGIE] SECRET — l'URL de la base contient le mot de passe : elle est lue dans
# [PÉDAGOGIE]          l'environnement PAR `store`, jamais passée en paramètre Prefect (les
# [PÉDAGOGIE]          paramètres sont journalisés) ni affichée dans les logs.
DB_URL_ENV = "INDUSENSE_DB_URL"

# [PÉDAGOGIE] SCHÉMA — la clé primaire est la clé NATURELLE (machine, prediction_ts) : c'est
# [PÉDAGOGIE]          elle qui permet à l'upsert de reconnaître une ligne déjà écrite.
# [PÉDAGOGIE]          Noms de types acceptés par PostgreSQL ET par SQLite.
# [PÉDAGOGIE]          prediction_ts = heure MÉTIER sans fuseau (comme les loaders) ;
# [PÉDAGOGIE]          created_at    = instant d'AUDIT avec fuseau (UTC).
CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS predictions (
    machine       VARCHAR(16)              NOT NULL,
    prediction_ts TIMESTAMP                NOT NULL,
    proba_panne   DOUBLE PRECISION         NOT NULL,
    decision      VARCHAR(8)               NOT NULL,
    created_at    TIMESTAMP WITH TIME ZONE NOT NULL,
    PRIMARY KEY (machine, prediction_ts)
)"""

# [PÉDAGOGIE] UPSERT — « insère, OU mets à jour si la clé existe déjà » :
# [PÉDAGOGIE]          • clé nouvelle → INSERT (nouvelle ligne)
# [PÉDAGOGIE]          • clé déjà vue → UPDATE de proba_panne et decision (pas de doublon)
# [PÉDAGOGIE]          created_at n'est PAS mis à jour : il garde l'instant de la 1re écriture.
# [PÉDAGOGIE]          EXCLUDED = la ligne qu'on tentait d'insérer (même syntaxe PG et SQLite).
UPSERT = """
INSERT INTO predictions (machine, prediction_ts, proba_panne, decision, created_at)
VALUES (:machine, :prediction_ts, :proba_panne, :decision, :created_at)
ON CONFLICT (machine, prediction_ts) DO UPDATE SET
    proba_panne = EXCLUDED.proba_panne,
    decision    = EXCLUDED.decision"""


# [PÉDAGOGIE] OBSERVABILITÉ — un taux de panne n'a de sens qu'avec sa POPULATION : on journalise
# [PÉDAGOGIE]          effectif, nombre de pannes et taux, préfixés par le nom de la population
# [PÉDAGOGIE]          (joined = après jointure ; gold = après features). Aucune ligne source
# [PÉDAGOGIE]          n'est publiée (les incidents contiennent des colonnes opérateur).
def _log_population(log, prefix: str, df: pd.DataFrame) -> None:
    """Journalise taille et taux de panne d'une population nommée."""
    n_panne = int(df[settings.target_col].sum())
    log.info(
        "%s_rows=%d %s_panne_count=%d %s_panne_rate=%.8f",
        prefix,
        len(df),
        prefix,
        n_panne,
        prefix,
        n_panne / len(df),
    )


# [PÉDAGOGIE] TASK 1 — INGEST : lecture des 3 sources hétérogènes, normalisation des
# [PÉDAGOGIE]          identifiants, jointure merge_asof(by="machine", ±90 min) et cible `panne`
# [PÉDAGOGIE]          (24 h avant un incident). Tout est fait par build_dataset (lib testée).
# [PÉDAGOGIE]          Pas de retry : fichier absent ou mal formé = erreur DÉTERMINISTE.
# [PÉDAGOGIE]          NO_CACHE : chaque run relit réellement les fichiers.
@task(cache_policy=NO_CACHE)
def ingest(data_dir: Path) -> pd.DataFrame:
    """Charge et joint les sources brutes : une ligne par (machine, timestamp)."""
    log = get_run_logger()
    joined = build_dataset(
        load_temperature(data_dir / "capteurs_temperature.csv"),
        load_pressure(data_dir / "capteurs_pression.tsv"),
        load_incidents(data_dir / "releves_incidents.csv"),
        window_hours=settings.incident_window_hours,
    )
    _log_population(log, "joined", joined)
    return joined


# [PÉDAGOGIE] TASK 2 — FEATURE : transformation PURE (aucun effet de bord). Lags et moyennes
# [PÉDAGOGIE]          glissantes PAR MACHINE, avec shift(1) AVANT rolling (pas de fuite, M23),
# [PÉDAGOGIE]          puis retrait des lignes incomplètes (débuts de série) → population gold.
# [PÉDAGOGIE]          Même enchaînement que `indusense build-gold`.
@task(cache_policy=NO_CACHE)
def feature(joined: pd.DataFrame) -> pd.DataFrame:
    """Ajoute les features temporelles sans fuite et retire les lignes incomplètes."""
    log = get_run_logger()
    gold = add_temporal_features(joined).dropna().reset_index(drop=True)
    _log_population(log, "gold", gold)
    return gold


# [PÉDAGOGIE] TASK 3 — PREDICT : on garde la DERNIÈRE observation de chaque machine (même règle
# [PÉDAGOGIE]          que `indusense predict`) → UNE prédiction par machine. Le modèle donne
# [PÉDAGOGIE]          proba_panne ; le seuil (celui de l'API, settings.decision_threshold)
# [PÉDAGOGIE]          la transforme en decision « alerte » / « ok ».
# [PÉDAGOGIE]          Pas de retry : modèle introuvable = erreur déterministe.
@task(cache_policy=NO_CACHE)
def predict(gold: pd.DataFrame, model_path: Path, threshold: float) -> pd.DataFrame:
    """Calcule proba_panne et decision pour la dernière observation de chaque machine."""
    log = get_run_logger()
    last = gold.groupby("machine").tail(1)
    proba = predict_proba(load_model(model_path), select_features(last, settings.target_col))
    preds = pd.DataFrame(
        {
            "machine": last["machine"].to_numpy(),
            "prediction_ts": last["timestamp"].to_numpy(),
            "proba_panne": proba,
            "decision": np.where(proba >= threshold, "alerte", "ok"),
        }
    )
    log.info(
        "predict : %d machines scorées | seuil=%s | alertes=%d",
        len(preds),
        threshold,
        int((preds["decision"] == "alerte").sum()),
    )
    return preds


# [PÉDAGOGIE] RETRY CIBLÉ — Prefect appelle cette fonction après un échec de `store` pour
# [PÉDAGOGIE]          décider s'il faut réessayer. On ne réessaie QUE l'OperationalError de
# [PÉDAGOGIE]          SQLAlchemy (base injoignable, verrou… = TRANSITOIRE). Toute autre erreur
# [PÉDAGOGIE]          (URL absente, SQL invalide… = DÉTERMINISTE) échoue tout de suite :
# [PÉDAGOGIE]          réessayer ne ferait que retarder le diagnostic.
def _is_transient(task, task_run, state) -> bool:
    """Condition de retry : vrai uniquement si l'échec vient d'une base injoignable."""
    try:
        state.result()
    except OperationalError:
        return True
    except Exception:
        return False
    return False


# [PÉDAGOGIE] BORD DU PILOTE — chaque base attend un type différent pour l'horodatage :
# [PÉDAGOGIE]          • SQLite refuse un pandas.Timestamp brut → texte ISO 8601 (heure conservée)
# [PÉDAGOGIE]          • PostgreSQL (psycopg) attend un datetime Python
def _ts_for_driver(value, is_sqlite: bool):
    """Adapte un horodatage pandas au type attendu par le pilote de la base."""
    ts = pd.Timestamp(value)
    return ts.isoformat() if is_sqlite else ts.to_pydatetime()


# [PÉDAGOGIE] TASK 4 — STORE : la SEULE task à effet de bord (écriture en base) → la seule à
# [PÉDAGOGIE]          réessayer : 3 fois, délais croissants 5 s / 15 s / 45 s (backoff), et
# [PÉDAGOGIE]          seulement si _is_transient le permet.
# [PÉDAGOGIE]          Idempotence : l'UPSERT sur (machine, prediction_ts) garantit qu'une relance
# [PÉDAGOGIE]          met à jour au lieu de dupliquer → count(*) stable.
# [PÉDAGOGIE]          Transaction unique (engine.begin) : tout est écrit, ou rien.
@task(
    retries=3,
    retry_delay_seconds=[5, 15, 45],
    retry_condition_fn=_is_transient,
    cache_policy=NO_CACHE,
)
def store(preds: pd.DataFrame) -> tuple[int, int]:
    """Écrit les prédictions par UPSERT et renvoie count(*) avant / après."""
    log = get_run_logger()
    db_url = os.environ.get(DB_URL_ENV)
    if not db_url:
        raise RuntimeError(f"{DB_URL_ENV} absente : définir l'URL de la base cible.")
    engine = create_engine(db_url)
    is_sqlite = engine.dialect.name == "sqlite"
    created_at = datetime.now(UTC)
    rows = [
        {
            "machine": r.machine,
            "prediction_ts": _ts_for_driver(r.prediction_ts, is_sqlite),
            "proba_panne": float(r.proba_panne),
            "decision": r.decision,
            "created_at": created_at.isoformat() if is_sqlite else created_at,
        }
        for r in preds.itertuples(index=False)
    ]
    with engine.begin() as con:
        con.execute(text(CREATE_TABLE))
        before = con.execute(text("SELECT count(*) FROM predictions")).scalar_one()
        con.execute(text(UPSERT), rows)
        after = con.execute(text("SELECT count(*) FROM predictions")).scalar_one()
    engine.dispose()
    # [PÉDAGOGIE] On journalise le TYPE de base (sqlite / postgresql), jamais l'URL.
    log.info(
        "store : %d prédictions | base=%s | lignes %d -> %d (nouvelles : %d)",
        len(rows),
        engine.dialect.name,
        before,
        after,
        after - before,
    )
    return before, after


# [PÉDAGOGIE] FLOW — orchestre les 4 tasks dans l'ordre du design. `data_dir` est un paramètre
# [PÉDAGOGIE]        du run (retrouvable dans ses journaux) ; par défaut INDUSENSE_DATA_DIR,
# [PÉDAGOGIE]        sinon data/raw. Le verdict final rend l'idempotence lisible d'un coup d'œil.
@flow(name="indusense-predict")
def predict_flow(data_dir: str | None = None) -> int:
    """Exécute ingest → feature → predict → store ; renvoie le nombre de lignes en base."""
    log = get_run_logger()
    source = Path(data_dir) if data_dir else settings.data_dir
    joined = ingest(source)
    gold = feature(joined)
    preds = predict(gold, settings.model_dir / "rf.joblib", settings.decision_threshold)
    before, after = store(preds)
    if after == before:
        verdict = "IDEMPOTENT (0 nouvelle ligne)"
    else:
        verdict = f"{after - before} nouvelle(s) ligne(s)"
    log.info("FLOW terminé : %d lignes en base -> %s", after, verdict)
    return after


if __name__ == "__main__":
    predict_flow()
