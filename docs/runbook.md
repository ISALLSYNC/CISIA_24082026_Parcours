# Runbook M34 — InduSense

> Rédigé le 19/10/2026 à partir des incidents **réellement joués** jusqu'au retour **Normal**
> (preuves `preuves/34_incident_a_api_morte.txt` et `preuves/34_incident_b_pic_401.txt`).
> Règles : `monitoring/grafana/provisioning/alerting/rules.yml` · dashboard « InduSense — SLO (M34) ».
> Ne jamais copier de secret, de payload sensible ou de journal complet dans le runbook.

---

## Runbook 1 — « EXERCICE — API morte (up < 1) »

### Alerte

- **Nom** : EXERCICE — API morte (up < 1) · groupe `indusense-exercice`.
- **Signal / condition** : `up{job="indusense-api"} < 1` pendant **1 min** (`for: 1m`, évaluée toutes
  les 30 s) ; absence de série = alerte (cible perdue = surveillance aveugle).
- **Gravité et impact métier** : **critique** (SLO 1). Plus aucune prédiction : la maintenance travaille
  à l'aveugle ; chaque panne ratée coûte ≈ 5 000 €.

### Diagnostic borné

1. **L'API répond-elle ?** `Invoke-WebRequest http://127.0.0.1:8000/health` → *joué* : « Impossible de
   se connecter au serveur distant ».
2. **Le conteneur tourne-t-il ?** `docker compose ps -a api` → *joué* : `exited (137)`.
3. **Ce que voit Prometheus** : page Targets (`http://localhost:9090/targets`) → *joué* : `indusense-api`
   **down**, « lookup api … no such host » (le service a disparu du réseau Compose).

→ Si 1 et 2 sont KO : panne du service → action ci-dessous. Si le conteneur tourne mais `/health`
échoue : lire les **dernières lignes** du journal (`docker compose logs --tail 50 api`), sans les copier
ici, puis escalader.

### Action réversible

- **Action** : `docker compose up -d --wait api` (redémarre le service, attend `healthy`).
- **Retour arrière** : sans objet (redémarrage) ; si la nouvelle version est en cause, revenir à
  l'image précédente : `IMAGE_TAG=<tag précédent> docker compose up -d api`.
- **Preuve de résolution** : `/health` **200** et `/ready` **200** · alerte **Firing → Normal**.
  *Joué* : arrêt à T+5 s → **Pending** T+25 s → **Firing** T+85 s → redémarrage T+120 s → **Normal**
  T+150 s.
- **Escalade** : si le service retombe dans les 10 min, ou si `/ready` reste 503 (modèle absent) →
  responsable technique.

---

## Runbook 2 — « EXERCICE — Pic de 401 (> 0,1 / s) »

### Alerte

- **Nom** : EXERCICE — Pic de 401 (> 0,1 / s) · groupe `indusense-exercice`.
- **Signal / condition** : `sum(rate(http_requests_total{status="401"}[1m])) > 0,1` pendant **1 min**
  (codes **non regroupés** depuis le M33, sinon les 401 seraient noyés dans « 4xx »).
- **Gravité et impact métier** : **avertissement** (sécurité, M26). Un client mal configuré ne reçoit
  plus de prédictions, **ou** quelqu'un tente d'accéder sans clé.

### Diagnostic borné

1. **Ampleur** : taux de 401 sur le dashboard SLO → *joué* : **0,98 / s** (seuil 0,1).
2. **Nature** : y a-t-il aussi des 200 ou des 429 ? → *joué* : 200 = 0 / s, 429 = 0 / s → uniquement
   des refus d'authentification.
3. **Origine** : quel client ? (journal d'accès, adresse source — **sans** copier de clé ni de payload)
   → *joué* : client local sans en-tête `X-API-Key` (script d'exercice).

→ Client connu : configuration à corriger. Origine inconnue ou volume croissant : escalade sécurité.

### Action réversible

- **Action** : arrêter ou corriger la source (en réel : fournir la bonne clé au client, ou bloquer
  l'origine) ; **ne pas** désactiver l'authentification.
- **Retour arrière** : lever le blocage dès que le client est corrigé.
- **Preuve de résolution** : taux de 401 revenu à **0** · alerte **Firing → Normal**.
  *Joué* : envoi T+2 s → **Pending** T+42 s → **Firing** T+102 s → arrêt de la source → **Normal**
  T+193 s (≈ 104 réponses 401 comptées par Prometheus).
- **Escalade** : origine inconnue, ou pic qui reprend → référent sécurité ; envisager une rotation de la
  clé si une fuite est suspectée.

---

## Alertes de production (non jouées en incident)

| Règle | Première vérification | Remarque |
|---|---|---|
| PROD — Latence p95 > 300 ms (`for: 5m`) | charge en cours ? (taux de requêtes) · ressources du poste | Plus stricte que le SLO 2 (1 s) : **sonnera sous charge sur ce poste** (p95 mesurée 2,1 s) ; buckets plafonnés à 1 s |
| PROD — 5xx > 1 % (`for: 5m`) | `docker compose logs --tail 50 api` (sans copier) · `/ready` | Défaillance de l'API ; escalade technique si persistant |

## Ce que les exercices ont appris

- Une alerte passe toujours par **Pending** : `for:` évite d'alerter sur un incident qui se résout seul.
- Le délai réel dépasse `for:` : collecte (15 s) + évaluation (30 s) + fenêtre de `rate` (1 min).
- Arrêt de l'API avec le code **137** : Docker a dû la tuer au bout de 10 s (arrêt non gracieux) → à
  investiguer.
