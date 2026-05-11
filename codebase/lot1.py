import streamlit as st
import matplotlib.pyplot as plt
from collections import Counter
from Main import generate_kmers # Utilisation de la fonction de la base

def parse_fastq(file_content: bytes) -> list[tuple[str, str, str]]:
    """Parse un fichier FASTQ en liste de (ID, Sequence, Qualité)."""
    lines = file_content.decode("utf-8").splitlines()
    reads = []
    for i in range(0, len(lines), 4):
        if i + 3 < len(lines):
            reads.append((lines[i], lines[i+1], lines[i+3]))
    return reads

def convert_to_fasta(reads: list[tuple[str, str, str]]) -> str:
    """Convertit la liste de reads en chaîne formatée FASTA."""
    fasta = []
    for header, seq, _ in reads:
        header_name = header[1:] if header.startswith('@') else header
        fasta.append(f">{header_name}\n{seq}")
    return "\n".join(fasta)

def render_page():
    st.header("Lot 1 : Ingestion et Qualité")
    st.markdown("Cette page permet de lire des séquences, de les convertir et d'analyser la qualité via l'histogramme des k-mers.")
    
    uploaded_file = st.file_uploader("Uploader un fichier FASTQ", type=["fastq", "fq"])
    k = st.slider("Taille des k-mers (k)", min_value=3, max_value=51, value=5, step=2)
    
    if uploaded_file is not None:
        file_content = uploaded_file.read()
        reads = parse_fastq(file_content)
        st.success(f"{len(reads)} reads chargés.")
        
        if st.checkbox("Voir l'aperçu FASTA"):
            fasta_str = convert_to_fasta(reads[:10])
            st.text_area("Aperçu FASTA (10 premiers)", fasta_str, height=200)
            
        with st.spinner("Analyse des k-mers en cours..."):
            all_kmers = []
            for _, seq, _ in reads:
                # Utilisation de generate_kmers venant de Main.py
                all_kmers.extend(generate_kmers(seq, k))
                
            kmer_counts = Counter(all_kmers)
            freqs = list(kmer_counts.values())
            freq_counts = Counter(freqs)
            
            x = sorted(list(freq_counts.keys()))
            y = [freq_counts[f] for f in x]
            
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.bar(x, y, color='royalblue', edgecolor='black', alpha=0.7)
            ax.set_xlabel("Fréquence d'apparition du k-mer")
            ax.set_ylabel("Nombre de k-mers uniques")
            ax.set_title("Histogramme des fréquences des k-mers")
            st.pyplot(fig)
            st.info("💡 Interprétation : Les k-mers avec une fréquence très faible (souvent 1) proviennent généralement d'erreurs de séquençage.")
