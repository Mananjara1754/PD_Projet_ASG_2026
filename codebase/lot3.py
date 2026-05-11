import streamlit as st
import hashlib
from collections import Counter
from Main import generate_kmers # Utilisation de la fonction du Main.py (la base)

class BloomFilter:
    """Filtre de Bloom pour simuler le Graphe sans l'instancier."""
    def __init__(self, size: int, hash_count: int):
        self.size = size
        self.hash_count = hash_count
        self.bit_array = [0] * size

    def add(self, string: str):
        """Ajoute un élément dans le filtre en utilisant md5."""
        for seed in range(self.hash_count):
            index = int(hashlib.md5((string + str(seed)).encode()).hexdigest(), 16) % self.size
            self.bit_array[index] = 1

    def __contains__(self, string: str) -> bool:
        """Vérifie si un élément est présent dans le filtre."""
        for seed in range(self.hash_count):
            index = int(hashlib.md5((string + str(seed)).encode()).hexdigest(), 16) % self.size
            if self.bit_array[index] == 0:
                return False
        return True

def render_page():
    st.header("Lot 3 : Moteur d'Assemblage (Filtre de Bloom)")
    st.markdown("Approche memory-efficient basée sur les fonctions d'extraction de `Main.py` mais utilisant un Filtre de Bloom à la place d'un dictionnaire de graphe.")
    
    reads_input = st.text_area("Reads (format brut, un par ligne)", ">Read1\nATGCGTAC\n>Read2\nCGTACGTA\n>Read3\nTACGTAGC", height=150)
    
    col1, col2 = st.columns(2)
    k = col1.slider("Taille des k-mers (k)", 3, 21, 4)
    threshold = col2.number_input("Fréquence minimum (solidité)", 1, value=1)
    
    col3, col4 = st.columns(2)
    m_size = col3.number_input("Taille du Filtre (bits)", 100, value=1000)
    h_count = col4.number_input("Nombre de hachages", 1, value=3)
    
    if st.button("Lancer l'Assemblage De Novo"):
        # Nettoyage de l'input
        reads = [line.strip().upper() for line in reads_input.splitlines() if not line.startswith('>')]
        
        all_kmers = []
        for r in reads:
            all_kmers.extend(generate_kmers(r, k))
            
        counts = Counter(all_kmers)
        solid_kmers = [kmer for kmer, v in counts.items() if v >= threshold]
        
        if not solid_kmers:
            st.error("Aucun k-mer solide.")
            return
            
        # Remplissage du filtre
        bf = BloomFilter(m_size, h_count)
        for solid_k in solid_kmers:
            bf.add(solid_k)
            
        # Logique de traversée "On-the-fly"
        seed = solid_kmers[0]
        contig = seed
        current_kmer = seed
        nucleotides = ['A', 'C', 'G', 'T']
        
        stopped_by_bifurcation = False
        
        with st.expander("Parcours On-the-fly (Détails)"):
            for step in range(1000):
                suffix = current_kmer[1:]
                
                # Test des 4 extensions possibles dans le filtre de Bloom
                valid_ext = [suffix + n for n in nucleotides if suffix + n in bf]
                
                st.write(f"K-mer actuel: `{current_kmer}` -> Extensions validées: `{valid_ext}`")
                
                if len(valid_ext) == 0:
                    break # Dead end
                elif len(valid_ext) > 1:
                    stopped_by_bifurcation = True
                    break # Embranchement, on arrête pour éviter de suivre une branche erronée
                else:
                    current_kmer = valid_ext[0]
                    contig += current_kmer[-1] # Ajout du dernier nucléotide au contig
                    
        st.success(f"**Contig assemblé :** {contig} (Longueur {len(contig)})")
        if stopped_by_bifurcation:
            st.warning("⚠️ L'assemblage s'est arrêté net suite à une bifurcation. Les bifurcations peuvent être causées par de vraies répétitions ou par des Faux Positifs inhérents au Filtre de Bloom.")
