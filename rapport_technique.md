# Rapport Technique - Pipeline d'Assemblage "De Novo" (Projet ASG-2026)

## 1. Choix des Scores de Similarité (Lot 2)
L'algorithme de programmation dynamique utilisé pour détecter le chevauchement (overlap) repose sur un score de Match de `+1`, et une pénalité de Mismatch et de Gap de `-1`. 
* **Justification** : Sachant que le taux d'erreur attendu des reads est de l'ordre de 1%, l'alignement doit être extrêmement restrictif pour éviter d'aligner des régions qui ne se correspondent pas réellement. En appliquant une pénalité égale ou supérieure au score de match pour les erreurs, on s'assure que le chevauchement global maximisera les longues suites de correspondances exactes.

## 2. Impact de la Taille de $k$ sur le Graphe (Lot 1 & 3)
La résolution du Graphe de de Bruijn dépend fortement de la taille des k-mers choisis ($k$) :
* **Si $k$ est trop petit** : La probabilité qu'un même k-mer apparaisse à plusieurs endroits différents dans le génome original est très élevée (répétitions). Le graphe sera extrêmement connecté avec de nombreuses branches ("tangles") et bifurcations. L'algorithme s'arrêtera prématurément, produisant de très petits contigs.
* **Si $k$ est trop grand** : La probabilité de chevauchement diminue. Surtout avec un taux d'erreur de 1%, un read erroné altèrera $k$ k-mers successifs. Si $k$ est proche de la longueur du read, on risque de perdre complètement la connectivité, créant de multiples graphes déconnectés ("dead ends") et l'impossibilité d'assembler la séquence.
* **Le compromis optimal** : $k$ doit être assez grand pour éviter les fausses répétitions, mais assez petit pour qu'il existe au moins une couverture complète en k-mers non erronés entre deux reads adjacents.

## 3. Analyse Critique de l'Approche Filtre de Bloom (Faux Positifs)
L'approche de Minia 2 utilise un Filtre de Bloom pour simuler le Graphe de de Bruijn. 
* **Le problème des faux positifs** : Le filtre, de par sa nature probabiliste, peut répondre "Oui" à un k-mer qui n'a jamais été inséré. Lors de la traversée "On-the-fly" à partir d'un k-mer, on teste les 4 extensions $A, C, G, T$. Un faux positif fera croire à la présence d'une extension qui n'existe pas.
* **Conséquences** :
  1. Si l'extension correcte est présente et qu'un faux positif est généré sur une autre, l'algorithme détecte une "fausse bifurcation". Le parcours s'arrête (ou se divise) alors qu'il ne s'agit pas d'une véritable répétition biologique, ce qui fragmente l'assemblage inutilement.
  2. Si aucune extension correcte n'existe (fin de contig), un faux positif fera s'engager l'algorithme dans un "chemin fantôme" fait d'erreurs, jusqu'à ce que le filtre ne valide plus les k-mers suivants.
* **Mitigation** : La qualité de l'assemblage dépend du dimensionnement du filtre (nombre de bits $m$ et fonctions de hachage $h$). Un grand $m$ par rapport au nombre de k-mers distincts réduit drastiquement les faux positifs, garantissant la fiabilité de l'assemblage memory-efficient.

## 4. Analyse de Complexité
Comparaison spatiale et temporelle de l'approche d'alignement $O(n^2)$ face à l'approche par graphe :

| Caractéristique | Approche Alignement (OLC / Graphe de Chevauchement) | Approche Graphe de de Bruijn (Filtre de Bloom) |
| :--- | :--- | :--- |
| **Complexité Temporelle** | $O(N^2 \times L^2)$ où $N$ est le nombre de reads et $L$ leur longueur. Il faut comparer chaque read avec tous les autres via une matrice de DP. | $O(N \times L)$ pour peupler le filtre, puis un temps linéaire proportionnel à la taille du contig $O(V)$ pour l'assemblage (avec $4 \times h$ hachages par k-mer). |
| **Complexité Spatiale** | $O(N \times L)$ pour stocker les reads, plus $O(L^2)$ pour la matrice DP active par paire. Le graphe de chevauchement prend $O(N^2)$ en espace pour les arêtes. | $O(m)$ bits pour le Filtre de Bloom. La mémoire est constante et indépendante du nombre de k-mers une fois le filtre dimensionné, contrairement à un dictionnaire standard nécessitant $O(K \times k)$. |

**Conclusion** : L'approche par alignement global ne "scale" pas face aux millions de fragments issus du NGS (Next Generation Sequencing). L'approche par Graphe de de Bruijn couplée à une structure de données probabiliste comme le Filtre de Bloom est la seule solution viable pour obtenir une complexité quasi-linéaire tout en maintenant une empreinte mémoire maîtrisée (Memory-Efficient).
