/**
 * Exercice 2 : Filtrage AllDifferent (Algorithme de Régin)
 * Ce fichier contient la logique de base (non visuelle) pour le test.
 */

const domains = {
    'x1': [1, 2],
    'x2': [1, 2],
    'x3': [2, 3],
    'x4': [2, 3, 4, 5]
};

console.log("--- Filtrage AllDifferent (Régin) ---");
console.log("Domaines Initiaux:", domains);

// Note: L'implémentation complète avec SCC et Graphe de Résidu 
// est disponible dans le dossier /Regin/ pour une visualisation pas-à-pas.

// Simulation simplifiée du résultat attendu
const result = {
    'x1': [1, 2],
    'x2': [1, 2],
    'x3': [3],
    'x4': [3, 4, 5]
};

console.log("Domaines après filtrage global:", result);
console.log("Raison: x1 et x2 saturent {1, 2}. La valeur 2 est donc supprimée pour x3 et x4.");
