# Contrôles complémentaires avant la prochaine session

Version locale du 5 septembre 2026. Ce document complète les supports, sans changer la progression des jalons ni déclarer opérationnel un service non testé.

## Installer les dépendances réellement verrouillées

```powershell
uv sync --frozen --extra dev --extra mlops
uv run --frozen pytest -q
```

Le nouveau verrou a été testé avec MLflow 3.16.0 et protobuf 6.33.6 ; les preuves MLflow 3.14.0 antérieures restent historiques. Le scan du verrou complet, incluant les extensions, passe de 69 à 2 alertes identifiées le 5 septembre. Il ne remplace pas un scan de l'image Docker réellement construite. Ni NumPy, ni pandas, ni scikit-learn n'ont été mis à jour dans ce correctif.

Les deux alertes restantes n'ont pas de version corrective indiquée par la base de vulnérabilités utilisée :

- **DiskCache, CVE-2025-69872** : un acteur pouvant écrire dans un cache peut préparer des objets pickle exécutés lors de leur relecture. DVC utilise cette bibliothèque. N'utiliser qu'un cache neuf et fiable, sous un répertoire privé au compte ou à la charge, avec droits exclusifs vérifiés, aucun parent lié et aucun cache partagé ou restauré d'un dépôt apprenant. `DVC_SITE_CACHE_DIR` permet de choisir ce répertoire ; une simple valeur de variable ne prouve pas la sécurité de ses permissions. Ces permissions n'ont pas été vérifiées sur tous les postes apprenants.
- **NLTK, CVE-2026-81726** : certaines API de persistance de modèles acceptent des chemins pouvant sortir des limites prévues. Le parcours numérique inspecté ne les appelle pas directement ; cela ne garantit pas que toute utilisation de NLTK soit sûre. Ne pas exposer ces API ni accepter des chemins ou artefacts NLP non fiables. Aucun statut « non affecté » global n'est revendiqué.

Ne pas ouvrir les services au réseau public ni supprimer les alertes du scanner pour obtenir artificiellement un résultat vert. Garder les modèles sérialisés, caches et sources de confiance. Les mesures de sécurité ci-dessus sont des préconditions à vérifier, pas des protections automatiquement appliquées par ce document.

## Reproduire les nombres sans confondre les jeux

Le starter `data/raw` est distinct de la base complète `data/drift_source`.

```text
Jointure complète : 66 800 températures - 1 175 non appariées = 65 625 lignes.
Résidu de jointure : 1 175 / 66 800 = environ 1,76 %.
Côté pression : 65 529 - 392 - 103 + 591 = 65 625 appariements.
Gold standard : 65 625 - (90 + 130 + 780) = 64 625 lignes.
Dérive enrichie : 65 625 - (180 + 130 + 780) = 64 535 lignes.
```

Les 392 lignes pression surnuméraires appartiennent à des clés dupliquées ; 103 clés ne sont jamais sélectionnées, et 591 appariements réutilisent une source déjà employée. Le taux de panne de la jointure est une autre quantité : 3 137 / 65 625, soit environ 4,78 %.

Le calcul de dérive ajoute `shift(1).rolling(24, min_periods=12).std()` aux fenêtres strictes 3 et 6 : il demande 12 valeurs disponibles parmi les 24 précédentes, pas 12 valeurs consécutives toutes présentes. Son démarrage retire 90 lignes supplémentaires sur ce jeu précis.

## Doublons contradictoires : convention de compatibilité, pas vérité physique

La pression complète contient 261 clés avec deux valeurs différentes. Aucun identifiant de séquence ne permet de prouver laquelle est la bonne. Le code conserve explicitement le tri historique `quicksort`, le fichier canonique ordonné et les versions verrouillées ; trois tests documentent le départage et la répétabilité. **Réordonner les lignes source n'est pas une opération neutre.**

Un tri stable des pressions changerait 240 valeurs jointes, puis certaines features et cibles synthétiques de dérive. Ne pas remplacer silencieusement la règle ni réutiliser les anciens artefacts comme s'ils provenaient de cette nouvelle règle. Une migration impose de choisir une convention d'ingestion, régénérer les datasets, revalider les modèles et conserver les anciennes preuves. Le conflit des mesures physiques reste ouvert ; cette version ne prétend pas l'avoir arbitré.

## Docker et Windows

Le moteur du poste formateur a échoué au démarrage le 5 septembre sur `dockerInference`, avant l'activation de WSL. Compose, Kubernetes, les cibles Prometheus et Grafana ne sont donc pas déclarés prêts. Aucune suppression de socket ni réinitialisation n'a été faite. Les anciens états « actifs » décrivent leurs dates historiques.

Pour MLflow sous Windows, privilégier un chemin court pour le projet et l'environnement virtuel. La recette en chemin très profond a échoué à charger un fichier de migration ; la même version et le même verrou en environnement court ont réussi. Ne pas contourner le problème en effaçant la base : sauvegarder avant toute migration d'une base existante. La recette de cette unité n'utilise que des bases neuves.

Les tests actuels couvrent Windows, PowerShell et Git Bash ; la compatibilité native Linux/macOS et les services conteneurisés restent à valider séparément.

## Références de sécurité

- [Avis officiel NLTK GHSA-8mgp-746c-j5xp](https://github.com/nltk/nltk/security/advisories/GHSA-8mgp-746c-j5xp).
- [Fiche CVE-2025-69872](https://www.cve.org/CVERecord?id=CVE-2025-69872).
- [Notes officielles Docker Desktop 4.89.0](https://docs.docker.com/desktop/release-notes/#4890) : correctif Windows pertinent pour un socket bloqué après un arrêt brutal, sans garantie qu'il suffise à réparer ce poste.
