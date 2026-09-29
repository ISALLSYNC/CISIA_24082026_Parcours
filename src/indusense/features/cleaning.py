# [PÉDAGOGIE] ============================================================================
# [PÉDAGOGIE] FICHIER — src/indusense/features/cleaning.py
# [PÉDAGOGIE] MODULE  — M23 — extension « extraire une fonction propre » (fiche TD 23)
# [PÉDAGOGIE] RÔLE    — Nettoyer les mesures capteurs : retirer les doublons et combler les
# [PÉDAGOGIE]           valeurs manquantes machine par machine.
# [PÉDAGOGIE] THÉORIE — une transformation répétée dans un notebook devient une fonction
# [PÉDAGOGIE]           testée, rangée dans features/
# [PÉDAGOGIE]           • la médiane résiste mieux qu'une moyenne aux valeurs aberrantes
# [PÉDAGOGIE]           • groupby("machine") empêche une machine d'hériter des mesures d'une
# [PÉDAGOGIE]             autre
# [PÉDAGOGIE] À VOIR  — Sans groupby, la médiane de [10, 30] = 20 remplacerait le trou de
# [PÉDAGOGIE]           MACH-01 au lieu de sa propre valeur 10.
# [PÉDAGOGIE] PIÈGE   — Une machine sans aucune valeur connue garde ses NaN : il n'existe pas
# [PÉDAGOGIE]           de médiane à propager.
# [PÉDAGOGIE] GARDE   — Toutes les lignes marquées [PÉDAGOGIE] sont des commentaires : elles
# [PÉDAGOGIE]           guident la lecture sans changer l'exécution.
# [PÉDAGOGIE] ============================================================================

from __future__ import annotations

import pandas as pd


# [PÉDAGOGIE] BLOC `clean_sensor_data` — unité de responsabilité : isoler un nettoyage
# [PÉDAGOGIE] nommable, testable et réutilisable.
# [PÉDAGOGIE] CONTRAT — entrées : df avec une colonne `machine` et les colonnes capteurs ;
# [PÉDAGOGIE] sortie : copie sans doublons, trous comblés par la médiane de la machine.
def clean_sensor_data(
    df: pd.DataFrame,
    sensor_cols: tuple[str, ...] = ("temperature", "pressure_bar"),
) -> pd.DataFrame:
    """Drop duplicate rows and impute missing sensor values with the per-machine median."""
    # [PÉDAGOGIE] COPIE — .copy() évite de modifier le DataFrame de l'appelant.
    df = df.drop_duplicates().copy()
    for col in sensor_cols:
        # [PÉDAGOGIE] ISOLATION — transform calcule la médiane de CHAQUE machine et renvoie
        # [PÉDAGOGIE] une série alignée sur les lignes d'origine.
        df[col] = df.groupby("machine")[col].transform(lambda s: s.fillna(s.median()))
    return df
