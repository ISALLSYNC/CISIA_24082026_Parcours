# Préparer et contrôler une session Sprint 3

> **Mise à jour AELION du 28/09/2026 - version à utiliser.** Dans l'extranet Dendreo/AELION, ouvrez : **Concevoir et implémenter une solution d’IA > Public - Participants de l'ADF > Tous les Participants > ressources > Sprint 3**. Sous-dossiers : `01_PRESENTATIONS_PPTX` · `02_PRESENTATIONS_PDF` · `03_GUIDES_FICHES_ET_REVISION` · `04_FICHIERS_A_COMPLETER` · `05_DONNEES_ET_EXERCICES` · `06_Schéma_et_DAT` · `corrigé` · `fiches de révision autres sprints`.
>
> Les exercices sont distribués **en fichiers individuels**. Dans `05_DONNEES_ET_EXERCICES`, choisissez `M25_API`, `TP_PAYGUARD`, `TP_INDU_SENSE`, `VISION_METRICS`, `GAME_DAY` ou `PERFORMANCE_ET_DIVERS`. PayGuard et Vision sont déjà extraits : ne cherchez aucun ZIP. Les noms `data__...`, `scripts__...` et `tests__...` désignent les sous-dossiers à recréer ; retirez le suffixe `.txt` des fichiers de code et de configuration après téléchargement. Consultez `MODE_EMPLOI_FICHIERS_INDIVIDUELS.md` et `MANIFESTE_EXERCICES_INDIVIDUELS.json` pour les noms et empreintes.
>
> Le bundle Git GameDay complet n'est pas publié dans l'espace public ; attendez la remise par le formateur pour cette activité. Cette mise à jour remplace les anciens chemins de pack, les commandes d'extraction ZIP et les consignes de recherche de bundle dans les pages antérieures.


InduSense · Notice commune apprenant/formateur · Révision du 5 septembre 2026

## 1. Une version, un dossier, un environnement

**Obligatoire avant chaque atelier :** noter le jour, le module, la branche ou le commit demandé, le chemin du projet et la version de Python. Ne pas mélanger le starter, le parcours progressif, un ancien clone et le clone GameDay.

EXEMPLE — commandes de diagnostic à lancer dans le terminal du projet.

```text
git status --short
git branch --show-current
git rev-parse HEAD
uv run python --version
uv run python -c "import indusense; print(indusense.__file__)"
```

`__file__` comporte deux underscores avant ET après file. Cette commande sert à vérifier le module réellement importé. La branche de correction finale est une référence formateur ; ne pas la substituer aux jalons des apprenants avant l'introduction pédagogique des fonctionnalités.

Le contrat Python actuel est 3.13, strictement inférieur à 3.14. Utiliser le `uv.lock` livré : `uv sync --frozen --extra dev`. Ne pas mettre à jour les dépendances au hasard pour contourner une erreur. Préserver les fichiers déjà modifiés avant de changer de branche ; demander au formateur en cas de conflit.

**Diagnostic d'entrée (10 minutes) :** retrouver son dossier, expliquer un import, lire une ligne de CSV, lancer un test et identifier sa sortie. Si un point manque, traiter le prérequis avant le bonus. Le socle est obligatoire ; les défis et optimisations sont des bonus, pas une condition cachée de réussite.

@pagebreak

## 2. MLflow local : installer le bon extra et vérifier l'écriture

MLflow n'appartient pas à l'extra `dev` seul. Pour l'atelier MLflow, installer **les deux extras** et conserver cet environnement pour les commandes suivantes.

EXEMPLE — commandes depuis la racine du dépôt corrigé livré avec cette révision.

```text
uv sync --frozen --extra dev --extra mlops
uv run --no-sync python scripts/smoke_mlflow_local.py --output-dir reports/mlflow_preflight_01
```

Le dossier de preuve doit être nouveau ou vide. Le contrôle importe aussi les modules protobuf de MLflow, crée une base SQLite locale, enregistre un paramètre et une métrique puis les relit. Un simple `import mlflow` ne suffit pas. Un dossier non vide n'est jamais nettoyé automatiquement : utiliser un nouveau suffixe pour rejouer.

**Versions à distinguer :** interpréteur Python 3.13 ; bibliothèques MLflow, mlflow-skinny et mlflow-tracing 3.14.0 ; protobuf 6.33.6. Le 3.14.0 de MLflow n'est pas une version de Python. En cas d'erreur d'import protobuf : vérifier le Python réellement utilisé et rejouer la synchronisation figée. Ne pas installer une version globale au hasard et ne pas supprimer le verrou.

EXEMPLE — démarrer le serveur local dans un terminal dédié, puis ouvrir son interface dans Chrome. Ces commandes utilisent une base distincte du test de contrôle.

```text
uv run --no-sync mlflow server --host 127.0.0.1 --port 5000 --backend-store-uri sqlite:///mlflow-local.db
```

Interface : [MLflow local](http://127.0.0.1:5000). Dans le terminal du programme qui entraîne, définir `MLFLOW_TRACKING_URI` à `http://127.0.0.1:5000` avant le lancement. PowerShell : `$env:MLFLOW_TRACKING_URI = 'http://127.0.0.1:5000'`. Bash/zsh : `export MLFLOW_TRACKING_URI=http://127.0.0.1:5000`.

Le serveur doit rester ouvert pendant les écritures. Vérifier qu'un run récent apparaît avec le paramètre et la métrique attendus. Un écran qui s'ouvre ne prouve pas la persistance. En cas de port occupé, choisir un port libre et adapter aussi l'URI client ; ne pas arrêter le service d'un autre atelier.

Un appel explicite à `mlflow.set_tracking_uri` dans le programme l'emporte sur la variable d'environnement. Vérifier l'URI effectivement utilisée. Le script de contrôle force volontairement SQLite et ignore l'URI serveur : pour tester le serveur HTTP, utiliser un client configuré vers ce serveur, pas ce smoke SQLite.

**RECETTE EXÉCUTÉE le 05/09/2026 :** Python 3.13.14 sous Windows ; health HTTP 200, page UI HTTP 200 et paramètre/métrique écrits puis relus via HTTP. Le serveur de test isolé a été arrêté après la preuve. Cette recette ne couvre ni les jobs MLflow sous Windows (non pris en charge par ce backend), ni l'envoi d'artefacts ou de modèles. Le script de recette a imposé une sortie UTF-8 pour éviter une erreur d'affichage Unicode dans l'ancien terminal Windows.

Source : [architecture du serveur MLflow](https://mlflow.org/docs/latest/self-hosting/architecture/tracking-server/). Ce contrôle couvre le tracking local, pas la totalité du registre ou le stockage distant d'artefacts.

@pagebreak

## 3. Docker : le budget doit correspondre à l'image mesurée

Le contrôle `scripts/check_image.py` prend un budget explicite **en MiB** et une plateforme explicite. 1 MiB = 1 048 576 octets. Il examine l'image du moteur Docker sélectionné sans l'exécuter. Vérifier `docker context show` avant la recette : un contexte distant n'est pas le moteur local. Le champ `Config.User` détecte une configuration root évidente ; il ne prouve pas l'utilisateur effectif de tout processus à l'exécution.

EXEMPLE NON MESURÉ — 700 est illustratif, à remplacer par le budget approuvé après mesure.

```text
docker build --platform linux/amd64 -t indusense:0.1.0 .
docker image inspect indusense:0.1.0
uv run --no-sync python scripts/check_image.py indusense:0.1.0 --max-mib 700 --platform linux/amd64
```

Relever l'identifiant d'image, Size en octets, OS/architecture, le budget et la marge justifiée. Utiliser le même contrat en CI. Avec buildx, charger l'image mono-plateforme localement (`--load`) avant de l'inspecter. Ne pas comparer la taille compressée d'un registre à la taille locale inspectée. Codes : 0 conforme ; 1 écart au contrat ; 2 commande ou données d'inspection invalides. Un échec de Docker n'est pas une image certifiée trop grosse.

Sans variante explicite, `linux/amd64` accepte les variantes déclarées de cette architecture ; pour l'exiger, fournir par exemple `linux/amd64/v3`. Toute sortie du contrôle est JSON ; `--json` est un indicateur de compatibilité. Archiver séparément `docker context show` et noter si un contexte ou un endpoint a été imposé, sans publier ses identifiants de connexion.

Source : [docker image inspect](https://docs.docker.com/reference/cli/docker/image/inspect/). Un budget de 200 ou 700 n'est jamais une vérité universelle. Le scan de vulnérabilités constitue un contrôle distinct à répéter à chaque release.

## 4. Prometheus/Grafana : vérifier le trajet avant le graphique

Avant le laboratoire J5 : lire `guide_manips_prometheus_grafana_J5.md`, puis nommer métrique, labels, unité et fenêtre. `up` vérifie le scrape, pas la qualité du modèle. `rate(compteur_total[5m])` exprime une vitesse par seconde. Un p95 de latence se lit avec son unité et sa fenêtre ; ce n'est pas une moyenne.

Le chemin est : CSV produit par le calcul → exporter qui relit le fichier → scrape Prometheus → requête → panneau Grafana. Le calcul ne pousse pas directement les CSV dans Grafana.

**Laisser l'exporter ouvert dans son propre terminal pendant les évaluations.** Dans le laboratoire concerné, il relit le CSV toutes les 15 secondes ; attendre également le scrape et le rafraîchissement du panneau. Une absence de données n'est pas une valeur zéro. Vérifier chemin du CSV, fraîcheur, cible UP, labels, fenêtre temporelle et datasource avant de modifier le panneau.

Ne pas mélanger les ports du laboratoire courant avec ceux de la démonstration isolée de cardinalité. Un identifiant de requête ou d'observation non borné va dans les logs/traces, pas dans les labels des métriques.

## 5. Données d'une autre cohorte : contrôler avant d'intégrer

Les jeux d'anciennes cohortes ne deviennent pas automatiquement les données du Sprint 3 actuel. **Le jeu machine livré actuellement n'inclut pas une table de maintenances.** Les incohérences signalées dans une ancienne table restent non reproductibles sans l'archive exacte. Ne pas fabriquer une correction de données absentes.

Avant d'adopter un jeu machines/incidents/maintenances : conserver l'archive et son empreinte approuvée ; vérifier les colonnes, les identifiants uniques, les références et l'égalité de machine entre maintenance et incident lié. Une maintenance sans incident nécessite une convention explicite. Le futur contrôle doit rapporter les compteurs et numéros de lignes, sans recopier les données nominatives.

Pour des images réelles, conserver des originaux immuables, l'identifiant d'échantillon, leur empreinte, dimensions natives, cohorte et split. Créer **deux branches indépendantes** depuis l'original : AE vers 128×128 ; PatchCore vers 224×224 dans le protocole de l'atelier concerné. Ne pas utiliser le 128×128 de l'AE pour recréer artificiellement un 224×224. Les tailles exactes restent dépendantes de l'implémentation du modèle.

Un manifeste ne peut vérifier que la cohérence de la lignée déclarée et les empreintes, pas deviner qu'une image a été réduite avant sa réception. L'identité de la cohorte exige une référence approuvée extérieure au manifeste. Le laboratoire M33 actuel est synthétique : pas de promesse de réparation ou d'entraînement d'un PatchCore réel.

@pagebreak

## 6. Utiliser une IA sans perdre la maîtrise

Pour chaque morceau de code proposé par une IA :

1. **Expliquer** les entrées, les sorties et chaque transformation avec ses mots.
2. **Prédire** le résultat sur un exemple minuscule avant de lancer.
3. **Modifier** un paramètre et annoncer l'effet attendu.
4. **Tester** un cas normal et un cas d'échec ; lire le message, pas uniquement sa couleur.
5. **Tracer** l'aide reçue, le choix retenu et la preuve dans le journal.

La qualité de l'explication et du test compte, pas le volume de code généré. Ne transmettre ni secret, ni fichier nominatif à un assistant. Le post-mortem sépare fait observé, hypothèse, correctif et preuve.

## 7. Checklist de passation

- Avant séance : version des supports et commit notés, commandes du module rejouées dans un environnement propre, archives et CSV nécessaires présents, ports et extras cohérents.
- Pendant : socle/bonus affichés, erreurs documentées, une seule modification à la fois, preuve avant/après, aide progressive sur demande.
- Après : journal, tests, provenance et blocages conservés ; aucun « tout vert » sans périmètre. La matrice de recette accompagnant la release distingue exécuté, hérité et non reproduit.
- GameDay : distribuer l'énoncé autonome. Les indices progressifs et la variante guidée restent dans le kit formateur.
