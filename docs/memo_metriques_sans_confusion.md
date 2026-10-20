# Métriques : lire la bonne formule

Sprint 3 InduSense · Révision du 5 septembre 2026 · Mémo apprenant

## 1. Régression : une valeur numérique à prédire

On note y la valeur réelle, p la prédiction et n le nombre d'observations évaluées. Dans ce mémo, l'erreur signée est **e = p - y** : positif signifie surestimation. Certaines sources inversent ce signe ; toujours annoncer la convention.

| Mesure | Formule en mots | Unité et interprétation |
|---|---|---|
| MBE, biais moyen | somme(p - y) / n | unité de y ; le signe indique le biais ; des erreurs opposées peuvent s'annuler |
| MAE, erreur absolue moyenne | somme(abs(p - y)) / n | unité de y ; distance moyenne, toujours positive ou nulle |
| MSE, erreur quadratique moyenne | somme((p - y)^2) / n | unité de y au carré ; accentue les grandes erreurs |
| RMSE | racine carrée de MSE | unité de y ; accentue aussi les grandes erreurs |
| MAPE en pourcentage | 100 × somme(abs((p - y) / y)) / n | pourcentage ; formule définie ici seulement si tous les y sont non nuls |

**Attention : MBE n'est pas MSE ; MAE n'est pas MAPE.** Une formule au carré correspond à MSE. Une formule divisant par la valeur réelle correspond à une erreur relative, pas à MAE.

EXEMPLE ILLUSTRATIF — deux capteurs, aucune mesure réelle d'InduSense.

| y | p | e = p - y | abs(e) | e^2 | abs(e/y) |
|---|---|---|---|---|---|
| 10 | 12 | 2 | 2 | 4 | 0,20 |
| 20 | 18 | -2 | 2 | 4 | 0,10 |

Résultats : MBE = 0,00 ; MAE = 2,00 ; MSE = 4,00 ; RMSE = 2,00 ; MAPE = 15,0 %. Un biais nul ne signifie donc pas une prédiction parfaite.

Dans scikit-learn, `mean_absolute_percentage_error` renvoie un **ratio** : 0,15 correspond à 15 %. Avec un y nul, l'implémentation utilise un petit dénominateur de protection ; elle peut produire un nombre énorme. Ne pas présenter cette valeur comme un pourcentage métier fiable. Choisir une autre métrique ou définir une règle métier explicite, puis publier le nombre de lignes concernées. Ne jamais supprimer silencieusement ces lignes.

Sources de définition : [MAE scikit-learn](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.mean_absolute_error.html), [MAPE scikit-learn](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.mean_absolute_percentage_error.html). MBE utilise la convention signée annoncée ci-dessus.

@pagebreak

## 2. Classification InduSense : la panne est la classe positive

| Cas | Réalité | Prédiction |
|---|---|---|
| TP, vrai positif | panne | panne |
| FP, faux positif | pas de panne | panne : fausse alerte |
| FN, faux négatif | panne | pas de panne : panne manquée |
| TN, vrai négatif | pas de panne | pas de panne |

- Accuracy = (TP + TN) / (TP + FP + FN + TN) : proportion totale de décisions correctes.
- Précision = TP / (TP + FP) : parmi les alertes, quelle proportion correspond à une panne ?
- Recall ou rappel = TP / (TP + FN) : parmi les pannes, quelle proportion est détectée ?
- Une division par zéro exige une convention documentée. Conserver les effectifs et le seuil de décision avec chaque résultat.
- Avec peu de pannes, prédire toujours « pas de panne » donne une bonne accuracy, mais un rappel nul. Choisir le seuil avec les coûts métier ; ne pas optimiser l'accuracy seule.

## 3. Chaque pourcentage a son propre dénominateur

Références de la recette GameDay scellée du 4 septembre, **pas promesse de volume pour un autre jeu** :

| Étape | Lignes | Pannes | Taux de panne |
|---|---|---|---|
| Gold starter, data/raw | 1 896 | 200 | 10,55 % |
| Jointure capteurs du jeu complet | 65 625 | 3 137 | 4,78 % |
| Gold complet standard | 64 625 | 3 109 | 4,81 % |
| Fenêtres drift | 64 535 | 3 103 | 4,81 % |

Le **résidu de jointure** vaut 1 175 / 66 800 = **1,76 % des mesures de température d'entrée non jointes**. Ce n'est ni le taux de panne, ni la perte due aux features temporelles. Le nettoyage et les features font ensuite passer 65 625 à 64 625 lignes pour le gold standard.

Pourquoi 1 000 lignes retirées du gold standard ? Sur ce jeu exact : 90 débuts de séries (15 machines × 6 antécédents), 130 lignes avec température déjà manquante, puis 780 lignes suivantes dont les features utilisent ces valeurs manquantes. Ces ensembles sont disjoints : 90 + 130 + 780 = 1 000. La règle générale est de compter l'union des lignes contenant une valeur manquante, pas de multiplier seulement machines × lag, ni de sommer les NA de chaque colonne.

Dans le laboratoire vision M33, AE/PatchCore sont des **scores synthétiques** fournis pour apprendre à les évaluer. Ils ne constituent pas la preuve d'un entraînement réel des modèles. Ne pas comparer ces scores à un modèle réel sans protocole et données compatibles.
