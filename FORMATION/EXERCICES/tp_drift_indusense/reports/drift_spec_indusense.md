# Drift spec — InduSense v1

> Livrable M31-M32 (miroir `tp_drift_indusense`), rédigé le 19/10/2026.
> Décisions prises par moi, question par question ; mise en forme et chiffres repris de mes preuves
> (`preuves/31_01` à `31_03`, `32_01`, `32_02` du dépôt Parcours) par Claude Code.
> Modèle surveillé : `HistGradientBoostingClassifier`, 10 features capteurs, **seuil gelé 0,05**.

## 1. Références et régimes

- **Deux références**, une par régime de fonctionnement :
  - `normale` — fonctionnement ordinaire (32 177 relevés) ;
  - `haute` — campagnes de forte charge (11 156 relevés).
- **Choix de la référence** : selon le **régime annoncé par le métier** (planning de production).
  `normale` par défaut ; `haute` pendant une campagne annoncée. Sans information du métier, on compare
  à `normale` et toute alerte est vérifiée auprès du planning avant d'agir.
- *Preuve* : janvier (campagne) → PSI température **6,213** contre `normale`, **0,001** contre `haute`.
- Binning : **10 intervalles figés sur la référence**. Tout PSI est cité avec sa population, sa
  référence et son binning.

## 2. Fenêtre courante et fréquence

- **Fréquence** : calcul **quotidien**.
- **Fenêtre** : **glissante de 7 jours** (≈ 2 400 relevés pour 15 machines).
- **Taille minimale** : **2 000 relevés** ; en dessous, pas de verdict (« échantillon insuffisant »).
- *Pourquoi pas chaque heure* : ≈ 14 relevés par heure, trop peu pour 10 intervalles → PSI instable,
  fausses alertes.

## 3. Features surveillées et tests

| Feature | Test qui décide | Seuil | Confirmation |
|---|---|---|---|
| `temperature` | PSI | **> 0,25** : alerte · 0,10 – 0,25 : à surveiller | KS (p-value), information seulement |
| `pressure_bar` | PSI | idem | idem |
| Par machine | PSI machine par machine, si le PSI global > 0,25 | > 0,25 | Localise la machine (fenêtre 2, MACH-03 : **19,469**) |

- **Le PSI décide, KS confirme** : KS est « significatif » sur la pression (p = 4e-07) pour un PSI de
  0,025 — un écart statistique sans intérêt métier, dû aux grands effectifs.

## 4. KPI métier (dès que les labels arrivent)

- **KPI** : **rappel** au seuil gelé (part des pannes réelles détectées).
- **Plancher** : rappel **< 0,60 → alerte** · 0,60 – 0,70 → à surveiller (tendance) · ≥ 0,70 normal.
- *Repères* : validation 0,771 · janvier 0,728 (normal) · fenêtre 3 **0,053** (panne du modèle).
- *Pourquoi pas le taux de panne* : il reste ≈ 5 % dans toutes les fenêtres, même en fenêtre 3 ; il
  dit combien de pannes surviennent, pas si le modèle les voit. Suivi en complément seulement.
- Délai : dépend de l'arrivée des labels (incidents confirmés).

## 5. Réactions au franchissement

| Situation | Exemple | Réaction | Qui |
|---|---|---|---|
| PSI > 0,25, rappel normal | fenêtre 2 : capteur +8 °C | **Vérifier et réétalonner le capteur** ; ne pas réentraîner sur des valeurs fausses | Maintenance |
| PSI > 0,25 pendant une campagne annoncée | janvier vs `normale` | **Comparer à `haute`** : pas de dérive → pas d'alerte, campagne notée | Équipe data + planning |
| Rappel < 0,60 | fenêtre 3 : concept drift | **Analyser et réentraîner** sur données récentes labellisées ; contrôles manuels renforcés en attendant. Baisser le seuil **ne répare pas** (ROC-AUC 0,205, classement inversé) | Équipe data + maintenance |

- **Anti-spam (hystérésis)** : **une seule alerte** par feature, puis silence **jusqu'à ce que le PSI
  repasse sous 0,10** (réarmement) ; **rappel au bout de 7 jours** si rien n'est corrigé.
- Chaque alerte est tracée dans la table `drift_events` (date, feature, PSI) et le rapport JSON.

## 6. Limites connues

1. **Le PSI ne voit pas le concept drift** (fenêtre 3 : PSI 0,002, rappel 0,053). Seul le rappel le
   révèle, et il arrive **en retard**, avec les labels.
2. **Le choix de la référence dépend du planning métier** : une campagne non annoncée provoquerait
   une **fausse alerte**.

## Branchement visé dans le flow

`ingest → features → predict → drift_check → store/report → notify` — `drift_check` après `predict`
(rapport PSI/KS), `store/report` écrit le JSON et `drift_events`, `notify` n'alerte que si le seuil
**et** l'anti-spam le permettent.
