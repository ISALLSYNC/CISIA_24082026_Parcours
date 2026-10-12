# [PÉDAGOGIE] ============================================================================
# [PÉDAGOGIE] FICHIER — src/indusense/flows/hello.py
# [PÉDAGOGIE] MODULE  — M29 — premier flow Prefect (« hello »)
# [PÉDAGOGIE] RÔLE    — Montrer le vocabulaire minimal : une TASK (étape unitaire, avec retries)
# [PÉDAGOGIE]           appelée par un FLOW (orchestration nommée et journalisée).
# [PÉDAGOGIE] THÉORIE — Prefect 3 : on appelle DIRECTEMENT la fonction décorée (pas de .run())
# [PÉDAGOGIE]           • @task(retries=…) : Prefect réessaie automatiquement si l'étape échoue
# [PÉDAGOGIE]           • get_run_logger() : messages rattachés au run (observabilité)
# [PÉDAGOGIE] LANCER  — uv run python -m indusense.flows.hello  (profil local 'ephemeral')
# [PÉDAGOGIE] LIMITE  — ping ne peut pas échouer : les retries ne se voient pas ici ; ils sont
# [PÉDAGOGIE]           montrés par scripts/demo_prefect_idempotence.py --flaky.
# [PÉDAGOGIE] GARDE   — Toutes les lignes marquées [PÉDAGOGIE] sont des commentaires : elles
# [PÉDAGOGIE]           guident la lecture sans changer l'exécution.
# [PÉDAGOGIE] ============================================================================

"""Flow « hello » du M29 : une task avec retries appelée par un flow nommé."""

from __future__ import annotations

from prefect import flow, get_run_logger, task


# [PÉDAGOGIE] TASK — étape unitaire ; réessayée 2 fois (après 1 s) en cas d'erreur.
@task(retries=2, retry_delay_seconds=1)
def ping(name: str) -> str:
    """Étape unitaire : renvoie ``pong:<name>``."""
    return f"pong:{name}"


# [PÉDAGOGIE] FLOW — orchestre la task ; son nom apparaît dans les journaux du run.
@flow(name="hello-indusense")
def hello_flow(name: str = "indusense") -> str:
    """Orchestration minimale : appelle ``ping`` et journalise son résultat."""
    logger = get_run_logger()
    result = ping(name)
    logger.info("Résultat de la task ping : %s", result)
    return result


if __name__ == "__main__":
    print(hello_flow())
