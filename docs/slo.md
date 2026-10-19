# SLO InduSense — M33

> Rédigé le 19/10/2026. Objectifs **choisis par moi**, question par question ; mise en forme, requêtes
> PromQL et valeurs mesurées par Claude Code (preuves `preuves/33_p1` à `33_p3`).
> Valeurs chiffrées des SLO 4 et 5 : proposées par Claude Code, **validées par moi**.
> Fenêtre de tous les SLO : **30 jours glissants**.

| # | Indicateur | Population | Objectif | Source PromQL (SLI) | Budget d'erreur | Mesuré le 19/10 |
|---|---|---|---|---|---|---|
| 1 | **Disponibilité** de l'API | cible `indusense-api` (process qui répond sur `/metrics`) | **≥ 99 %** | `avg_over_time(up{job="indusense-api"}[30d])` | 1 % ≈ **7 h 12 min** / 30 j | **0,993** ✅ (≈ 1 h d'historique ; le redémarrage pour reconstruire l'image compte) |
| 2 | **Latence** de prédiction | requêtes `POST /predict-tabular` | **p95 < 1 s** | `histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket{handler="/predict-tabular"}[5m])) by (le))` | **5 %** des requêtes au-delà d'1 s | sous charge : Locust **2,1 s** ❌ (PromQL affichait 1 : buckets) · hors charge : **NaN** = SLI **absent** (aucune requête en 5 min) |
| 3 | **Erreurs serveur** | toutes les requêtes de l'API | **< 1 %** en 5xx | `(sum(rate(http_requests_total{status=~"5.."}[30d])) or vector(0)) / sum(rate(http_requests_total[30d]))` | **1 requête sur 100** | **0** ✅ |
| 4 | **Dérive des données** | PSI `temperature` de la **fenêtre courante** contre la **référence du régime** (drift spec) | PSI **< 0,25** au moins **29 jours sur 30** | `max(indusense_drift_psi{feature="temperature", fenetre="<courante>", reference="<régime>"})` | **1 jour** de dérive forte / 30 j, traité selon la drift spec | janvier vs `haute` = **0,001** ✅ · F2 vs `normale` = 6,83 (dérive **volontaire** du TP) |
| 5 | **Fraîcheur de la collecte** | cible `indusense-drift` (exporteur de dérive) | **≥ 99 %** du temps collectée | `avg_over_time(up{job="indusense-drift"}[30d])` | 1 % ≈ 7 h 12 min / 30 j | **0,958** ❌ : exporteur lancé **après** la stack → premières collectes en échec (budget consommé) |

*Correction* : sans filtre `fenetre`, le `max` du SLO 4 mélangeait toutes les fenêtres publiées par
l'exporteur (11,03 contre `haute`, à cause de la fenêtre 2) ; en production, une seule fenêtre courante.

## Pourquoi chaque objectif est utile au métier

1. **Disponibilité 99 %** — la maintenance s'appuie sur l'API pour anticiper les pannes (5 000 € par
   panne ratée). 90 % autoriserait 3 jours « à l'aveugle » par mois ; 99,9 % exigerait plusieurs
   instances et une astreinte, irréaliste pour une API à un seul exemplaire.
2. **p95 < 1 s** — l'usage est la consultation de risques, pas du temps réel ; 1 s reste confortable.
   **Objectif à atteindre** : aujourd'hui violé sous charge (2,1 s) → décision d'optimiser l'API ou de
   dimensionner la machine.
3. **5xx < 1 %** — une 5xx est une défaillance **de l'API** (pas du client). Cohérent avec le SLO 1
   (5 % d'échecs = 95 % de disponibilité réelle) et avec l'alerte « 5xx > 1 % » du M34.
4. **PSI < 0,25** — protège la **qualité des entrées** du modèle : un capteur faux (fenêtre 2 : +8 °C)
   doit être vu et réétalonné. Comparer à la **référence du régime** (planning métier) évite les fausses
   alertes de campagne (janvier). Limite : le PSI ne voit pas le concept drift → KPI **rappel** de la
   drift spec en complément.
5. **Collecte 99 %** — si l'exporteur n'est plus collecté, le SLO 4 devient **aveugle** sans le dire :
   ce SLO surveille la surveillance.

## SLI absent ou SLI mauvais ?

| # | SLI **mauvais** (mesuré, hors objectif) | SLI **absent** (pas de mesure) | Comment le voir |
|---|---|---|---|
| 1 | `up = 0` : Prometheus joint la cible mais elle ne répond pas | série `up` absente (job mal configuré) | `absent(up{job="indusense-api"})` |
| 2 | p95 > 1 s | aucune requête dans la fenêtre → `rate` vide, « pas de données » | compter les requêtes : `sum(rate(http_requests_total{handler="/predict-tabular"}[5m]))` |
| 3 | ratio > 1 % | **aucune 5xx = série inexistante** → sans `or vector(0)`, le ratio est vide, pas 0 | `or vector(0)` dans la requête |
| 4 | PSI > 0,25 | exporteur arrêté → plus de série `indusense_drift_psi` | SLO 5 + `absent(indusense_drift_psi)` |
| 5 | `up = 0` | exporteur jamais déclaré → série absente | `absent(up{job="indusense-drift"})` |

🔑 Règle : « **pas de données** » n'est **jamais** « tout va bien ». Vu au M33 : le compteur
`indusense_predictions_total` n'a **aucune valeur** avant la 1re prédiction, et la requête des 5xx
renvoie « aucune donnée » tant qu'aucune 5xx n'a eu lieu.

## Limites et actions

- **Buckets de latence** : par défaut ≤ 0,1 / 0,5 / 1 s. Au-delà d'1 s, `histogram_quantile` plafonne
  à **1** : une alerte « p95 > 1 s » ne se déclencherait **jamais**, alors que la p95 réelle est de
  2,1 s. **Action** : ajouter des buckets au-delà d'1 s (ex. 2,5 s et 5 s) pour rendre le SLO 2
  mesurable.
- **Une seule instance, un seul poste** : la disponibilité mesurée par `up` ne couvre ni le réseau du
  client ni une panne du poste qui héberge Prometheus.
- **SLO 4** : l'exporteur publie des PSI **précalculés** par fenêtre du TP (protocole du dépôt fil
  rouge : F2 = 6,834) ; en production, il faudrait le calcul quotidien sur 7 jours de la drift spec.
