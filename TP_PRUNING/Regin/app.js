/**
 * Régin's Algorithm Visualizer for AllDifferent
 * Master PPC - Projet ASG 2026
 */

document.addEventListener('DOMContentLoaded', () => {
    // --- Data ---
    const initialDomains = {
        'x1': [1, 2],
        'x2': [1, 2],
        'x3': [2, 3],
        'x4': [2, 3, 4, 5]
    };

    const vars = Object.keys(initialDomains);
    const vals = [...new Set(Object.values(initialDomains).flat())].sort();

    let steps = [];
    let currentStepIndex = 0;
    let cy = null;

    // --- Algorithm Logic ---

    function runRegin() {
        steps = [];
        const domains = JSON.parse(JSON.stringify(initialDomains));

        // Step 1: Initial Bipartite Graph
        steps.push({
            type: 'initial',
            title: 'Graphe Biparti Initial',
            log: 'Construction du graphe variable-valeur à partir des domaines.',
            elements: getElements(domains),
            matching: []
        });

        // Step 2: Maximum Matching
        const matching = findMaxMatching(vars, domains);
        const isComplete = matching.length === vars.length;

        steps.push({
            type: 'matching',
            title: 'Couplage Maximum',
            log: isComplete ? 'Couplage complet trouvé !' : 'ÉCHEC : Pas de couplage complet.',
            elements: getElements(domains, matching),
            matching: matching
        });

        if (!isComplete) return;

        // Step 3: Residual Graph
        const residualEdges = getResidualEdges(vars, domains, matching);
        steps.push({
            type: 'residual',
            title: 'Graphe de Résidu',
            log: 'Orientation des arcs : Valeur → Variable pour le couplage, Variable → Valeur sinon.',
            elements: getElements(domains, matching, true),
            matching: matching
        });

        // Step 4: SCC Detection (Tarjan)
        const sccs = findSCCs(vars, vals, residualEdges);
        steps.push({
            type: 'scc',
            title: 'Composantes Fortement Connexes',
            log: `Détection des cycles via Tarjan. ${sccs.length} composantes identifiées.`,
            elements: getElements(domains, matching, true, sccs),
            matching: matching,
            sccs: sccs
        });

        // Step 5: Filtering
        const filteredDomains = performFiltering(vars, domains, matching, sccs, residualEdges);
        steps.push({
            type: 'final',
            title: 'Filtrage Final',
            log: 'Suppression des arcs qui ne sont ni dans le couplage, ni dans un cycle, ni sur un chemin vers une valeur libre.',
            elements: getElements(filteredDomains, matching, false),
            matching: matching,
            domains: filteredDomains
        });
    }

    function findMaxMatching(vars, domains) {
        const match = {}; // value -> variable
        const matching = [];

        function canMatch(v, visited) {
            for (const val of domains[v]) {
                if (!visited.has(val)) {
                    visited.add(val);
                    if (!match[val] || canMatch(match[val], visited)) {
                        match[val] = v;
                        return true;
                    }
                }
            }
            return false;
        }

        for (const v of vars) {
            canMatch(v, new Set());
        }

        for (const val in match) {
            matching.push({ var: match[val], val: parseInt(val) });
        }
        return matching;
    }

    function getResidualEdges(vars, domains, matching) {
        const edges = [];
        const matchMap = new Map();
        matching.forEach(m => matchMap.set(`${m.var}-${m.val}`, true));

        vars.forEach(v => {
            domains[v].forEach(val => {
                if (matchMap.has(`${v}-${val}`)) {
                    edges.push({ from: `val${val}`, to: v }); // v -> val in match, so val -> v in residual
                } else {
                    edges.push({ from: v, to: `val${val}` }); // v -> val not in match
                }
            });
        });
        return edges;
    }

    function findSCCs(vars, vals, edges) {
        const nodes = [...vars, ...vals.map(v => `val${v}`)];
        const adj = {};
        nodes.forEach(n => adj[n] = []);
        edges.forEach(e => adj[e.from].push(e.to));

        let index = 0;
        const stack = [];
        const onStack = {};
        const indices = {};
        const lowlink = {};
        const sccs = [];

        function strongconnect(v) {
            indices[v] = lowlink[v] = index++;
            stack.push(v);
            onStack[v] = true;

            (adj[v] || []).forEach(w => {
                if (indices[w] === undefined) {
                    strongconnect(w);
                    lowlink[v] = Math.min(lowlink[v], lowlink[w]);
                } else if (onStack[w]) {
                    lowlink[v] = Math.min(lowlink[v], indices[w]);
                }
            });

            if (lowlink[v] === indices[v]) {
                const scc = [];
                let w;
                do {
                    w = stack.pop();
                    onStack[w] = false;
                    scc.push(w);
                } while (w !== v);
                sccs.push(scc);
            }
        }

        nodes.forEach(n => {
            if (indices[n] === undefined) strongconnect(n);
        });

        return sccs;
    }

    function performFiltering(vars, domains, matching, sccs, edges) {
        const filtered = JSON.parse(JSON.stringify(domains));
        const matchMap = new Map();
        matching.forEach(m => matchMap.set(`${m.var}-${m.val}`, true));

        // Get free nodes (values not in matching)
        const matchedVals = new Set(matching.map(m => m.val));
        const freeVals = [1, 2, 3, 4, 5].filter(v => !matchedVals.has(v)).map(v => `val${v}`);
        
        // Find nodes reachable to/from free nodes in residual graph
        // Rule: an edge (x, v) is valid if:
        // 1. It is in the matching
        // 2. x and v are in the same SCC
        // 3. It belongs to an alternating path starting at a free node.
        
        const sccId = {};
        sccs.forEach((scc, i) => scc.forEach(n => sccId[n] = i));

        // Reachability for paths
        const adj = {};
        edges.forEach(e => {
            if (!adj[e.from]) adj[e.from] = [];
            adj[e.from].push(e.to);
        });

        const reachableFromFree = new Set();
        function dfs(v) {
            if (reachableFromFree.has(v)) return;
            reachableFromFree.add(v);
            (adj[v] || []).forEach(dfs);
        }
        freeVals.forEach(dfs);

        vars.forEach(v => {
            filtered[v] = domains[v].filter(val => {
                const inMatch = matchMap.has(`${v}-${val}`);
                const inSameSCC = sccId[v] === sccId[`val${val}`];
                const onPath = reachableFromFree.has(v) || reachableFromFree.has(`val${val}`);
                
                return inMatch || inSameSCC || onPath;
            });
        });

        return filtered;
    }

    function getElements(domains, matching = [], directed = false, sccs = []) {
        const elements = [];
        const nodeScc = {};
        sccs.forEach((scc, i) => scc.forEach(n => nodeScc[n] = i));

        vars.forEach((v, i) => {
            elements.push({ 
                data: { id: v, label: v, type: 'var', scc: nodeScc[v] },
                position: { x: 100, y: 100 + i * 80 }
            });
        });

        vals.forEach((val, i) => {
            elements.push({ 
                data: { id: `val${val}`, label: val, type: 'val', scc: nodeScc[`val${val}`] },
                position: { x: 400, y: 50 + i * 65 }
            });
        });

        const matchMap = new Set(matching.map(m => `${m.var}-val${m.val}`));

        vars.forEach(v => {
            domains[v].forEach(val => {
                const id = `${v}-val${val}`;
                const isMatched = matchMap.has(id);
                
                let source = v;
                let target = `val${val}`;
                if (directed && isMatched) {
                    source = `val${val}`;
                    target = v;
                }

                elements.push({
                    data: {
                        id: id,
                        source: source,
                        target: target,
                        matched: isMatched
                    }
                });
            });
        });

        return elements;
    }

    // --- Visualization ---
    function initCy() {
        cy = cytoscape({
            container: document.getElementById('cy'),
            style: [
                {
                    selector: 'node',
                    style: {
                        'label': 'data(label)',
                        'color': '#fff',
                        'text-valign': 'center',
                        'text-halign': 'center',
                        'width': 40,
                        'height': 40,
                        'font-family': 'Outfit'
                    }
                },
                {
                    selector: 'node[type="var"]',
                    style: { 'background-color': '#8b5cf6' }
                },
                {
                    selector: 'node[type="val"]',
                    style: { 'background-color': '#06b6d4' }
                },
                {
                    selector: 'edge',
                    style: {
                        'width': 1,
                        'line-color': '#4b5563',
                        'curve-style': 'bezier'
                    }
                },
                {
                    selector: 'edge[matched]',
                    style: {
                        'width': 4,
                        'line-color': '#10b981',
                        'z-index': 10
                    }
                },
                {
                    selector: 'node[scc]',
                    style: {
                        'border-width': 3,
                        'border-color': (node) => {
                            const colors = ['#f59e0b', '#ec4899', '#3b82f6', '#10b981', '#ef4444'];
                            return colors[node.data('scc') % colors.length];
                        }
                    }
                }
            ],
            userZoomingEnabled: false,
            userPanningEnabled: false
        });
    }

    function renderStep(index) {
        const step = steps[index];
        if (!cy || !step) return;

        document.getElementById('step-counter').textContent = `Étape: ${index + 1} / ${steps.length}`;
        document.getElementById('step-title').textContent = step.title;

        // Log
        const logs = document.getElementById('logs');
        const entry = document.createElement('div');
        entry.className = 'log-entry' + (step.type === 'final' ? ' important' : '');
        entry.innerHTML = `<strong>[${step.title}]</strong> ${step.log}`;
        logs.prepend(entry);

        // Graph
        cy.elements().remove();
        cy.add(step.elements);
        
        if (step.type === 'residual' || step.type === 'scc') {
            cy.style().selector('edge').style({
                'target-arrow-shape': 'triangle',
                'target-arrow-color': '#4b5563'
            }).update();
        } else {
            cy.style().selector('edge').style({
                'target-arrow-shape': 'none'
            }).update();
        }

        // Table
        if (step.type === 'final') {
            updateTable(step.domains);
        }
    }

    function updateTable(finalDomains) {
        const body = document.getElementById('domain-body');
        body.innerHTML = '';
        vars.forEach(v => {
            const tr = document.createElement('tr');
            
            const tdVar = document.createElement('td');
            tdVar.textContent = v;
            
            const tdBefore = document.createElement('td');
            initialDomains[v].forEach(val => {
                const span = document.createElement('span');
                span.className = 'val-chip';
                span.textContent = val;
                tdBefore.appendChild(span);
            });

            const tdAfter = document.createElement('td');
            initialDomains[v].forEach(val => {
                const isRemoved = !finalDomains[v].includes(val);
                const span = document.createElement('span');
                span.className = 'val-chip' + (isRemoved ? ' removed' : '');
                span.textContent = val;
                tdAfter.appendChild(span);
            });

            tr.appendChild(tdVar);
            tr.appendChild(tdBefore);
            tr.appendChild(tdAfter);
            body.appendChild(tr);
        });
    }

    // --- Events ---
    document.getElementById('btn-next').onclick = () => {
        if (currentStepIndex < steps.length - 1) {
            currentStepIndex++;
            renderStep(currentStepIndex);
        }
    };
    document.getElementById('btn-prev').onclick = () => {
        if (currentStepIndex > 0) {
            currentStepIndex--;
            renderStep(currentStepIndex);
        }
    };
    document.getElementById('btn-reset').onclick = () => {
        currentStepIndex = 0;
        document.getElementById('logs').innerHTML = '';
        renderStep(0);
    };

    initCy();
    runRegin();
    renderStep(0);
});
