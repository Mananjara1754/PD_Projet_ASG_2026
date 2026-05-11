import streamlit as st
import numpy as np

def alignement_dynamique_chevauchement(seq1: str, seq2: str, match: int, mismatch: int, gap: int):
    """
    Algorithme de Programmation Dynamique pour le chevauchement.
    Retourne le score max, les positions (i, j) et les séquences alignées.
    """
    n, m = len(seq1), len(seq2)
    score = np.zeros((n + 1, m + 1), dtype=int)
    
    # Remplissage de la matrice avec les scores
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if seq1[i-1] == seq2[j-1]:
                score[i][j] = score[i-1][j-1] + match
            else:
                score[i][j] = max(score[i-1][j-1] + mismatch, 
                                  score[i-1][j] + gap, 
                                  score[i][j-1] + gap)
                                  
    # Recherche du meilleur score sur la dernière ligne (fin de seq1)
    best_score = -float('inf')
    best_j = 0
    for j in range(1, m + 1):
        if score[n][j] > best_score:
            best_score = score[n][j]
            best_j = j
            
    # Remontée pour reconstruire l'alignement optimal
    align1, align2 = [], []
    i, j = n, best_j
    while i > 0 and j > 0:
        if seq1[i-1] == seq2[j-1] and score[i][j] == score[i-1][j-1] + match:
            align1.append(seq1[i-1])
            align2.append(seq2[j-1])
            i -= 1; j -= 1
        elif score[i][j] == score[i-1][j] + gap:
            align1.append(seq1[i-1])
            align2.append('-')
            i -= 1
        else:
            align1.append('-')
            align2.append(seq2[j-1])
            j -= 1
            
    # S'il reste des caractères dans seq1
    while i > 0:
        align1.append(seq1[i-1])
        align2.append('-')
        i -= 1
        
    return best_score, (n, best_j), "".join(align1[::-1]), "".join(align2[::-1])

def render_page():
    st.header("Lot 2 : Alignement par Programmation Dynamique")
    st.write("Trouver la Plus Longue Sous-Séquence Commune de chevauchement entre deux reads.")
    
    c1, c2 = st.columns(2)
    seq1 = c1.text_area("Read 1", "ATGCGTACGTTAG")
    seq2 = c2.text_area("Read 2", "CGTACGTTAGTCC")
    
    col1, col2, col3 = st.columns(3)
    match = col1.number_input("Match", value=1)
    mismatch = col2.number_input("Mismatch", value=-1)
    gap = col3.number_input("Gap", value=-1)
    
    if st.button("Calculer l'alignement"):
        score, pos, a1, a2 = alignement_dynamique_chevauchement(seq1.strip().upper(), seq2.strip().upper(), match, mismatch, gap)
        st.success(f"**Score final :** {score} | **Position :** fin du read 1 ({pos[0]}), début du read 2 jusqu'à ({pos[1]})")
        
        # Astuce d'affichage pour relier les matches avec le caractère '|'
        matches = "".join(['|' if a1[i] == a2[i] and a1[i] != '-' else ' ' for i in range(len(a1))])
        st.code(f"{a1}\n{matches}\n{a2}", language="text")
