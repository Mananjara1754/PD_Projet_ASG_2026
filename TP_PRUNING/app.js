/**
 * AC-3 Algorithm Visualizer
 * Master PPC - Projet ASG 2026
 */

document.addEventListener('DOMContentLoaded', () => {
    // --- Configuration & Data ---
    const data = {
        variables: ['X', 'Y', 'Z'],
        domains: {
            'X': [1, 2],
            'Y': [1, 2],
            'Z': [1, 2]
        },
        constraints: [
            { id: 'c1', from: 'X', to: 'Y', check: (x, y) => x < y, label: 'X < Y' },
            { id: 'c2', from: 'Y', to: 'X', check: (y, x) => x < y, label: 'X < Y' },
            { id: 'c3', from: 'Y', to: 'Z', check: (y, z) => y === z, label: 'Y = Z' },
            { id: 'c4', from: 'Z', to: 'Y', check: (z, y) => y === z, label: 'Y = Z' }
        ]
    };

    let steps = [];
    let currentStepIndex = 0;
    let cy = null;

    // --- AC-3 Logic with Step Recording ---
    function runAC3() {
        steps = [];
        const domains = JSON.parse(JSON.stringify(data.domains));
        const queue = [...data.constraints.map(c => ({ from: c.from, to: c.to, constraint: c }))];

        // Initial State
        steps.push({
            type: 'initial',
            domains: JSON.parse(JSON.stringify(domains)),
            queue: [...queue],
            log: "État Initial : Domaines au maximum, file remplie.",
            activeArc: null,
            removed: {}
        });

        const q = [...queue];

        while (q.length > 0) {
            const arc = q.shift();
            const Xi = arc.from;
            const Xj = arc.to;

            steps.push({
                type: 'processing',
                domains: JSON.parse(JSON.stringify(domains)),
                queue: [arc, ...q],
                activeArc: arc,
                log: `Traitement de l'arc (${Xi}, ${Xj})...`,
                removed: {}
            });

            const revised = revise(Xi, Xj, domains, arc.constraint);

            if (revised.modified) {
                if (domains[Xi].length === 0) {
                    steps.push({
                        type: 'failure',
                        domains: JSON.parse(JSON.stringify(domains)),
                        queue: [...q],
                        activeArc: arc,
                        log: `ÉCHEC : Le domaine de ${Xi} est vide !`,
                        removed: { [Xi]: revised.removedValues }
                    });
                    return;
                }

                // Add neighbors back to queue
                const neighbors = data.constraints.filter(c => c.to === Xi && c.from !== Xj);
                const addedArcs = [];
                neighbors.forEach(c => {
                    const newArc = { from: c.from, to: c.to, constraint: c };
                    // Avoid duplicates in UI for clarity, or just push
                    q.push(newArc);
                    addedArcs.push(newArc);
                });

                steps.push({
                    type: 'modified',
                    domains: JSON.parse(JSON.stringify(domains)),
                    queue: [...q],
                    activeArc: arc,
                    log: `Réduction de D(${Xi}) : suppression de {${revised.removedValues.join(', ')}}. Réinsertion de ${addedArcs.length} arcs.`,
                    removed: { [Xi]: revised.removedValues },
                    addedArcs: addedArcs
                });
            } else {
                steps.push({
                    type: 'no_change',
                    domains: JSON.parse(JSON.stringify(domains)),
                    queue: [...q],
                    activeArc: arc,
                    log: `Aucune modification pour D(${Xi}).`,
                    removed: {}
                });
            }
        }

        steps.push({
            type: 'final',
            domains: JSON.parse(JSON.stringify(domains)),
            queue: [],
            activeArc: null,
            log: "État Final : Le graphe est stabilisé (Arc-Consistant).",
            removed: {}
        });
    }

    function revise(Xi, Xj, domains, constraint) {
        let modified = false;
        const removedValues = [];
        const domainXi = [...domains[Xi]];

        domains[Xi] = domainXi.filter(x => {
            const hasSupport = domains[Xj].some(y => constraint.check(x, y));
            if (!hasSupport) {
                modified = true;
                removedValues.push(x);
                return false;
            }
            return true;
        });

        return { modified, removedValues };
    }

    // --- Visualization & UI ---
    function initGraph() {
        const elements = [];
        data.variables.forEach(v => {
            elements.push({ data: { id: v, label: v } });
        });

        // Use unique edge IDs for directed arcs
        data.constraints.forEach(c => {
            elements.push({
                data: {
                    id: `${c.from}-${c.to}`,
                    source: c.from,
                    target: c.to,
                    label: c.label
                }
            });
        });

        cy = cytoscape({
            container: document.getElementById('cy'),
            elements: elements,
            style: [
                {
                    selector: 'node',
                    style: {
                        'background-color': '#6366f1',
                        'label': 'data(label)',
                        'color': '#fff',
                        'text-valign': 'center',
                        'text-halign': 'center',
                        'font-family': 'Outfit',
                        'width': 50,
                        'height': 50,
                        'font-size': '16px'
                    }
                },
                {
                    selector: 'edge',
                    style: {
                        'width': 2,
                        'line-color': '#4b5563',
                        'target-arrow-color': '#4b5563',
                        'target-arrow-shape': 'triangle',
                        'curve-style': 'bezier',
                        'label': 'data(label)',
                        'font-size': '10px',
                        'color': '#a0a0a0',
                        'text-margin-y': -10,
                        'edge-text-rotation': 'autorotate'
                    }
                },
                {
                    selector: '.active-arc',
                    style: {
                        'line-color': '#06b6d4',
                        'target-arrow-color': '#06b6d4',
                        'width': 4,
                        'shadow-blur': 10,
                        'shadow-color': '#06b6d4'
                    }
                },
                {
                    selector: '.modified-node',
                    style: {
                        'background-color': '#ef4444',
                        'transition-property': 'background-color',
                        'transition-duration': '0.5s'
                    }
                }
            ],
            layout: {
                name: 'grid',
                rows: 1
            },
            userZoomingEnabled: false,
            userPanningEnabled: false
        });
    }

    function renderStep(index) {
        const step = steps[index];
        if (!step) return;

        // Update Step Counter
        document.getElementById('step-counter').textContent = `Étape: ${index + 1} / ${steps.length}`;

        // Update Log
        const logsDiv = document.getElementById('logs');
        const entry = document.createElement('div');
        entry.className = 'log-entry' + (step.type === 'modified' ? ' highlight' : '');
        entry.innerHTML = `<strong>[Step ${index}]</strong> ${step.log}`;
        logsDiv.prepend(entry);

        // Update Queue UI
        const queueList = document.getElementById('queue-list');
        queueList.innerHTML = '';
        step.queue.forEach((arc, i) => {
            const item = document.createElement('div');
            item.className = 'queue-item' + (i === 0 && step.type === 'processing' ? ' active' : '');
            item.textContent = `${arc.from}→${arc.to}`;
            queueList.appendChild(item);
        });

        // Update Domain UI
        const domainList = document.getElementById('domain-list');
        domainList.innerHTML = '';
        Object.keys(step.domains).forEach(v => {
            const row = document.createElement('div');
            row.className = 'domain-row';
            
            const name = document.createElement('span');
            name.className = 'variable-name';
            name.textContent = `D(${v})`;

            const vals = document.createElement('div');
            vals.className = 'values';

            // Show current values
            step.domains[v].forEach(val => {
                const span = document.createElement('span');
                span.className = 'value';
                span.textContent = val;
                vals.appendChild(span);
            });

            // Show removed values from this step if any
            if (step.removed[v]) {
                step.removed[v].forEach(val => {
                    const span = document.createElement('span');
                    span.className = 'value removed';
                    span.textContent = val;
                    vals.appendChild(span);
                });
            }

            row.appendChild(name);
            row.appendChild(vals);
            domainList.appendChild(row);
        });

        // Update Graph Visuals
        cy.elements().removeClass('active-arc modified-node');
        if (step.activeArc) {
            const edgeId = `${step.activeArc.from}-${step.activeArc.to}`;
            cy.getElementById(edgeId).addClass('active-arc');
        }
        if (step.type === 'modified') {
            const nodeId = step.activeArc.from;
            cy.getElementById(nodeId).addClass('modified-node');
            setTimeout(() => cy.getElementById(nodeId).removeClass('modified-node'), 1000);
        }
    }

    // --- Controls ---
    document.getElementById('btn-next').onclick = () => {
        if (currentStepIndex < steps.length - 1) {
            currentStepIndex++;
            renderStep(currentStepIndex);
        }
    };

    document.getElementById('btn-prev').onclick = () => {
        if (currentStepIndex > 0) {
            currentStepIndex--;
            // We need to re-render from start or handle state reversal
            // For simplicity in this demo, we just re-render the specific step
            // Note: Journaling is additive, so this might look weird in logs
            renderStep(currentStepIndex);
        }
    };

    document.getElementById('btn-reset').onclick = () => {
        currentStepIndex = 0;
        document.getElementById('logs').innerHTML = '';
        renderStep(0);
    };

    let playInterval = null;
    document.getElementById('btn-play').onclick = () => {
        const btn = document.getElementById('btn-play');
        if (playInterval) {
            clearInterval(playInterval);
            playInterval = null;
            btn.textContent = '▶';
        } else {
            btn.textContent = '⏸';
            playInterval = setInterval(() => {
                if (currentStepIndex < steps.length - 1) {
                    currentStepIndex++;
                    renderStep(currentStepIndex);
                } else {
                    clearInterval(playInterval);
                    playInterval = null;
                    btn.textContent = '▶';
                }
            }, 1500);
        }
    };

    // --- Start ---
    initGraph();
    runAC3();
    renderStep(0);
});
