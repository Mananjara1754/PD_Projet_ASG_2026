import streamlit as st
import matplotlib.pyplot as plt
from collections import Counter

def parse_fastq(file_content):
    lines = file_content.decode("utf-8").splitlines()
    reads = []
    for i in range(0, len(lines), 4):
        if i + 3 < len(lines):
            header = lines[i]
            seq = lines[i+1]
            qual = lines[i+3]
            reads.append((header, seq, qual))
    return reads

def convert_to_fasta(reads):
    fasta_lines = []
    for header, seq, _ in reads:
        header_name = header[1:] if header.startswith('@') else header
        fasta_lines.append(f">{header_name}")
        fasta_lines.append(seq)
    return "\n".join(fasta_lines)

def get_kmers(seq, k):
    return [seq[i:i+k] for i in range(len(seq) - k + 1)]

def run():
    st.header("Lot 1 : Ingestion et Qualité")
    st.markdown("Prise en charge des fichiers FASTQ, conversion en FASTA et analyse de granularité des k-mers.")
    
    uploaded_file = st.file_uploader("Uploader un fichier FASTQ", type=["fastq", "fq"])
    k = st.slider("Taille des k-mers (k)", min_value=3, max_value=51, value=5, step=2)
    
    if uploaded_file is not None:
        file_content = uploaded_file.read()
        reads = parse_fastq(file_content)
        st.success(f"{len(reads)} reads chargés avec succès.")
        
        if st.checkbox("Convertir en FASTA et afficher un aperçu"):
            fasta_str = convert_to_fasta(reads[:10])
            st.text_area("Aperçu FASTA (10 premiers reads)", fasta_str, height=200)
            
        st.subheader("Analyse de qualité des k-mers")
        with st.spinner("Calcul des k-mers en cours..."):
            all_kmers = []
            for _, seq, _ in reads:
                all_kmers.extend(get_kmers(seq, k))
                
            kmer_counts = Counter(all_kmers)
            st.write(f"**Nombre total de k-mers distincts :** {len(kmer_counts)}")
            
            freqs = list(kmer_counts.values())
            freq_counts = Counter(freqs)
            
            x = sorted(list(freq_counts.keys()))
            y = [freq_counts[f] for f in x]
            
            fig, ax = plt.subplots(figsize=(10, 5))
            max_x = min(max(x), sorted(freqs)[int(len(freqs)*0.99)] + 5) if len(freqs)>0 else 50
            ax.bar(x, y, width=1.0, color='royalblue', edgecolor='black', alpha=0.7)
            ax.set_xlim(0, max_x)
            ax.set_xlabel("Fréquence d'apparition du k-mer")
            ax.set_ylabel("Nombre de k-mers distincts")
            ax.set_title(f"Spectre des k-mers (k={k})")
            ax.grid(axis='y', linestyle='--', alpha=0.7)
            
            st.pyplot(fig)
            st.info("L'histogramme permet d'identifier le taux d'erreur : les k-mers ayant une faible fréquence (généralement 1) sont majoritairement issus d'erreurs de séquençage.")
