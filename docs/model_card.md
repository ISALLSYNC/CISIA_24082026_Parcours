# Model Card — InduSense (modèle apprenant)

Les statuts autorisés sont `[mesuré]`, `[à produire]`, `[non mesuré]`,
`[à confirmer]` et `[benchmark externe]`. Toute ligne `[mesuré]` doit comporter
`preuve=chemin/relatif` vers un fichier local réel.

## 1. Niveau métier

- Finalité et utilisateurs : [à confirmer] aider le **responsable maintenance et les techniciens** à **prioriser les inspections** des machines les plus à risque de panne (étiquette « panne » = incident dans les 24 h qui suivent la mesure). Usage prévu à valider avec le responsable maintenance.
- Décision assistée, hors périmètre et supervision humaine : [à confirmer] le modèle **suggère seulement** (`decision` = ok / alerte) ; un **technicien vérifie et décide** d'intervenir ou non. **Aucun arrêt automatique** de machine. Hors périmètre : décision sans humain, évaluation des personnes, usage sur des machines ou capteurs absents du Gold. Au vu des performances mesurées (niveau technique), le modèle ne doit **pas** servir à décider en l'état.
- Coût des erreurs : [non mesuré] aucun coût chiffré. Ordre de grandeur qualitatif : la **panne ratée** (faux négatif : arrêt de production, casse, risque sécurité) coûte **plus cher** que la **fausse alerte** (faux positif : une inspection inutile). Le seuil devrait donc privilégier le **rappel** ; or le rappel mesuré est 0 (voir niveau technique).

## 2. Niveau technique / maintenance

- Artefact et version : [mesuré] Random Forest scikit-learn `artifacts/models/rf.joblib` (200 arbres, graine 42), md5 `2779890061870d6a08d6efdf733da094`, 4 965 817 octets, versionné par DVC (remote `localstore`) ; version exposée par l'API : `0.1.0` (= version du package) ; registre MLflow `indusense-rf` v2. preuve=artifacts/models/rf.joblib.dvc
- Données, split temporel et empreinte : [mesuré] Gold `data/gold/gold_dataset.csv` (md5 `637be8d3825023160de0980761c9a9e8`, 1 896 lignes, taux de panne 10,55 %) ; évaluation en split **temporel par machine** (dernières 20 % des mesures de chaque machine en test : 1 516 train / 380 test) ; le modèle livré est ensuite réentraîné sur tout le Gold. preuve=artifacts/models/model_metadata.json
- Métriques et seuil : [mesuré] split temporel : PR-AUC 0,1036 · ROC-AUC 0,2475 · précision / rappel / F1 = 0 au seuil calibré sur le train (0,975) · taux de panne du test 13,16 %. Seuil **réellement appliqué par l'API** : 0,5 (`decision_threshold` de `config.py`), différent du seuil d'évaluation. preuve=metrics.json
- MLflow run_id : [mesuré] ff9c521c7e2c4afbbfd841bb900eb0d7 (run temporel, expérience `indusense-maintenance`, version 2 de `indusense-rf`, commit Git `74fe3a5`). preuve=preuves/24_mlflow_v2.txt
- Signature I/O : [mesuré] entrée : `machine_id` + au moins 7 relevés (`timestamp`, `temperature` entre -20 et 200, `pressure_bar` > 0 et ≤ 400) ; sortie : `machine_id`, `proba_panne` ∈ [0 ; 1], `decision` ∈ {ok, alerte}, `model_version`, `threshold` ; erreurs 401 / 422 / 503 prouvées par 12 tests. preuve=src/indusense/api/schemas.py
- Coût comparé CPU, RAM, GPU, durée, latence et taille : [non mesuré] aucune comparaison faite. Seuls relevés ponctuels : taille du modèle 4,97 Mo ; une requête `/predict-tabular` ≈ 127 ms sur un poste Windows (mesure unique, pas un benchmark).
- Limite mesurée sur le futur : [mesuré] en split temporel, ROC-AUC 0,2475 < 0,5 et PR-AUC 0,1036 < taux de panne 0,1316 : le modèle classe **moins bien que le hasard** sur les mesures futures ; le split stratifié (0,8531) était gonflé par la fuite. preuve=preuves/24_mlflow_v2.txt
- Limites, drift, réévaluation et responsable : [à produire] surveillance du drift (M31-M32) et critères de réévaluation à définir ; responsable du modèle à désigner. Recommandation : **ne pas utiliser pour décider** en l'état ; investiguer (features, dérive temporelle, données par machine) avant tout nouveau candidat.

## 3. Niveau conformité AI Act

- Finalité, personnes affectées et données utilisées : [à confirmer] maintenance prédictive d'équipements industriels. Personnes affectées **indirectement** : techniciens et opérateurs (charge d'inspection, sécurité en cas de panne ratée). Données d'entrée du modèle : mesures de capteurs machines (température, pression), identifiants machines, horodatages.
- Données personnelles : [mesuré] le fichier brut `data/raw/releves_incidents.csv` contient des données personnelles (colonnes `operator_name`, `operator_badge`, `comment`, `shift`), mais `load_incidents` n'en conserve que `machine` et `incident_ts` (date et heure de l'incident, pour construire la cible). Le Gold, les features, le modèle et l'API n'en contiennent **aucune**. preuve=src/indusense/data/loaders.py
- Risques, transparence, journalisation et supervision : [à confirmer] risque principal : **fausse confiance** dans un modèle qui fait moins bien que le hasard sur le futur (panne ratée). Transparence : chaque réponse de l'API renvoie `proba_panne`, `threshold` et `model_version`. Journalisation : `X-Request-ID` sur chaque réponse, mais non écrit dans les journaux du serveur (à produire, M33). Supervision : humaine, à chaque alerte. Accès à l'API par clé `X-API-Key` (clé de développement par défaut : à remplacer, M26).
- Classification réglementaire : [à confirmer] à confirmer avec le référent conformité

## 4. Benchmark externe distinct

- Référence Marine — ne décrit pas mon modèle : [benchmark externe] XGBoost ; cible panne à 24 h ; seuil proche de 0,41 ; PR-AUC proche de 0,62 ; prévalence 16,6 %.
- Coût Marine — ne décrit pas mon modèle : [benchmark externe] frugal 202,6 s / 0,158 gCO2e ; lourd 612,8 s / 0,352 gCO2e.
