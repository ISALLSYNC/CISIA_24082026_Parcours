# [PÉDAGOGIE] ============================================================================
# [PÉDAGOGIE] FICHIER — tests/test_cleaning.py
# [PÉDAGOGIE] MODULE  — M23 — extension « extraire une fonction propre » (fiche TD 23)
# [PÉDAGOGIE] RÔLE    — Prouver que l'imputation se fait machine par machine.
# [PÉDAGOGIE] THÉORIE — un test court, avec des valeurs choisies pour que l'erreur soit visible
# [PÉDAGOGIE]           • 10 et 30 : la médiane globale (20) diffère des médianes par machine
# [PÉDAGOGIE] GARDE   — Toutes les lignes marquées [PÉDAGOGIE] sont des commentaires : elles
# [PÉDAGOGIE]           guident la lecture sans changer l'exécution.
# [PÉDAGOGIE] ============================================================================

import pandas as pd

from indusense.features.cleaning import clean_sensor_data


# [PÉDAGOGIE] CONTRAT — entrées : aucun argument explicite ; preuve : chaque trou reçoit la
# [PÉDAGOGIE] médiane de SA machine, jamais la médiane globale 20.
def test_clean_sensor_data_imputes_by_machine():
    df = pd.DataFrame(
        {
            "machine": ["MACH-01", "MACH-01", "MACH-02", "MACH-02"],
            "temperature": [10.0, None, 30.0, None],
            "pressure_bar": [100.0, 102.0, 200.0, None],
        }
    )
    out = clean_sensor_data(df)

    # [PÉDAGOGIE] ORACLE — MACH-01 ne connaît que 10.0 → son trou vaut 10.0 (et non 20.0).
    assert out.loc[1, "temperature"] == 10.0
    # [PÉDAGOGIE] ORACLE — MACH-02 ne connaît que 30.0 → son trou vaut 30.0 (et non 20.0).
    assert out.loc[3, "temperature"] == 30.0
