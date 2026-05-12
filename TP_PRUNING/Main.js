/**
 * Exercice 1 : Implémentation d'AC3
 * Ce fichier contient la logique de base de l'algorithme AC-3.
 * Pour la version interactive et visuelle, veuillez ouvrir index.html dans un navigateur.
 */

const variables = ['X', 'Y', 'Z'];
const domains = {
    'X': [1, 2],
    'Y': [1, 2],
    'Z': [1, 2]
};

const constraints = [
    { from: 'X', to: 'Y', check: (x, y) => x < y },
    { from: 'Y', to: 'X', check: (y, x) => x < y },
    { from: 'Y', to: 'Z', check: (y, z) => y === z },
    { from: 'Z', to: 'Y', check: (z, y) => y === z }
];

function revise(Xi, Xj, domains, constraint) {
    let modified = false;
    const initialDomain = [...domains[Xi]];
    
    domains[Xi] = initialDomain.filter(x => {
        const hasSupport = domains[Xj].some(y => constraint.check(x, y));
        if (!hasSupport) {
            modified = true;
            return false;
        }
        return true;
    });

    return modified;
}

function ac3(variables, domains, constraints) {
    const queue = [...constraints];

    while (queue.length > 0) {
        const arc = queue.shift();
        const { from, to } = arc;

        if (revise(from, to, domains, arc)) {
            if (domains[from].length === 0) return false; // Échec

            // Réinsérer les arcs (k, from) dans la file
            constraints.forEach(c => {
                if (c.to === from && c.from !== to) {
                    queue.push(c);
                }
            });
        }
    }
    return true; // Succès
}

// Exécution de test
console.log("Domaines Initiaux:", JSON.parse(JSON.stringify(domains)));
const success = ac3(variables, domains, constraints);
if (success) {
    console.log("Domaines Finaux (Arc-Consistants):", domains);
} else {
    console.log("Échec : Le problème n'est pas arc-consistant.");
}
