import streamlit as st
import numpy as np

def lcs_overlap_alignment(seq1, seq2, match=1, mismatch=-1, gap=-1):
    n = len(seq1)
    m = len(seq2)
    score = np.zeros((n + 1, m + 1), dtype=int)
    
    # Semi-global alignment: no penalty for starting gap in seq2
    for i in range(1, n + 1):
        score[i][0] = 0
    for j in range(1, m + 1):
        score[0][j] = 0
        
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if seq1[i-1] == seq2[j-1]:
                score[i][j] = score[i-1][j-1] + match
            else:
                score[i][j] = max(score[i-1][j-1] + mismatch, score[i-1][j] + gap, score[i][j-1] + gap)
            
    best_score = -float('inf')
    best_j = 0
    for j in range(1, m + 1):
        if score[n][j] > best_score:
            best_score = score[n][j]
            best_j = j
            
    # Traceback
    align1 = []
    align2 = []
    i, j = n, best_j
    while i > 0 and j > 0:
        if seq1[i-1] == seq2[j-1] and score[i][j] == score[i-1][j-1] + match:
            align1.append(seq1[i-1])
            align2.append(seq2[j-1])
            i -= 1
            j -= 1
        elif score[i][j] == score[i-1][j] + gap:
            align1.append(seq1[i-1])
            align2.append('-')
            i -= 1
        else:
            align1.append('-')
            align2.append(seq2[j-1])
            j -= 1
            
    while i > 0:
        align1.append(seq1[i-1])
        align2.append('-')
        i -= 1
        
    return best_score, (n, best_j), "".join(align1[::-1]), "".join(align2[::-1])

def run():
    st.header("Lot 2 : Alignement par Programmation Dynamique")
    st.markdown("Variante de la programmation dynamique pour trouver la plus longue sous-séquence commune (chevauchement).")
    
    col1, col2 = st.columns(2)
    with col1:
        seq1 = st.text_area("Read 1 (Séquence de référence)", value="ATGCGTACGTTAG", height=100)
    with col2:
        seq2 = st.text_area("Read 2 (Séquence à aligner)", value="CGTACGTTAGTCC", height=100)
        
    st.subheader("Paramètres d'alignement")
    c1, c2, c3 = st.columns(3)
    match = c1.number_input("Score de Match", value=1)
    mismatch = c2.number_input("Pénalité de Mismatch", value=-1)
    gap = c3.number_input("Pénalité de Gap", value=-1)
    
    if st.button("Calculer l'alignement", type="primary"):
        seq1 = seq1.strip().upper()
        seq2 = seq2.strip().upper()
        
        if not seq1 or not seq2:
            st.error("Les deux reads doivent être non vides.")
            return
            
        score, pos, a1, a2 = lcs_overlap_alignment(seq1, seq2, match, mismatch, gap)
        
        st.success(f"**Score de l'alignement :** {score}")
        st.info(f"**Position du chevauchement :** Fin du read 1 à l'indice {pos[0]}, et le read 2 commence à s'aligner jusqu'à l'indice {pos[1]}")
        
        matches = "".join(['|' if a1[i] == a2[i] and a1[i] != '-' else ' ' for i in range(len(a1))])
        
        st.markdown("### Visualisation de l'alignement")
        st.code(f"{a1}\n{matches}\n{a2}", language="text")
