import streamlit as st
import hashlib
from collections import Counter

class BloomFilter:
    def __init__(self, size, hash_count):
        self.size = size
        self.hash_count = hash_count
        self.bit_array = [0] * size

    def add(self, string):
        for seed in range(self.hash_count):
            result = int(hashlib.md5((string + str(seed)).encode()).hexdigest(), 16)
            index = result % self.size
            self.bit_array[index] = 1

    def __contains__(self, string):
        for seed in range(self.hash_count):
            result = int(hashlib.md5((string + str(seed)).encode()).hexdigest(), 16)
            index = result % self.size
            if self.bit_array[index] == 0:
                return False
        return True

def get_kmers(seq, k):
    return [seq[i:i+k] for i in range(len(seq) - k + 1)]

def run():
    st.header("Lot 3 : Moteur d'Assemblage Memory-Efficient (Minia 2)")
    st.markdown("Reconstruction des contigs par parcours implicite d'un Graphe de de Bruijn représenté par un Filtre de Bloom.")
    
    default_reads = ">Read1\nATGCGTAC\n>Read2\nCGTACGTA\n>Read3\nTACGTAGC\n>Read4\nACGTAGCA"
    reads_input = st.text_area("Reads (format brut ou FASTA)", value=default_reads, height=150)
    
    col1, col2 = st.columns(2)
    k = col1.slider("Taille des k-mers (k)", min_value=3, max_value=21, value=4)
    threshold = col2.number_input("Seuil de solidité (fréquence min)", min_value=1, value=1)
    
    col3, col4 = st.columns(2)
    m_size = col3.number_input("Taille du Filtre de Bloom (bits m)", min_value=100, value=1000)
    h_count = col4.number_input("Nombre de fonctions de hachage (k)", min_value=1, value=3)
    
    if st.button("Lancer l'assemblage De Novo", type="primary"):
        lines = reads_input.strip().splitlines()
        reads = [line.strip().upper() for line in lines if not line.startswith('>')]
        
        all_kmers = []
        for r in reads:
            all_kmers.extend(get_kmers(r, k))
            
        counts = Counter(all_kmers)
        solid_kmers = [kmer for kmer, v in counts.items() if v >= threshold]
        
        st.write(f"**K-mers extraits :** {len(all_kmers)}")
        st.write(f"**K-mers solides insérés :** {len(solid_kmers)}")
        
        if len(solid_kmers) == 0:
            st.error("Aucun k-mer solide trouvé.")
            return
            
        bf = BloomFilter(m_size, h_count)
        for solid_k in solid_kmers:
            bf.add(solid_k)
            
        # Assembly logic
        seed = solid_kmers[0]
        st.info(f"**Seed (k-mer de départ) :** {seed}")
        
        contig = seed
        current_kmer = seed
        nucleotides = ['A', 'C', 'G', 'T']
        
        max_len = 1000
        stopped_by_bifurcation = False
        
        with st.expander("Détails du parcours on-the-fly", expanded=True):
            for step in range(max_len):
                suffix = current_kmer[1:]
                valid_ext = []
                
                for n in nucleotides:
                    candidate = suffix + n
                    if candidate in bf:
                        valid_ext.append(candidate)
                        
                st.write(f"**Étape {step+1}** : K-mer actuel `{current_kmer}` -> Extensions valides : `{valid_ext}`")
                
                if len(valid_ext) == 0:
                    st.write("Aucune extension trouvée (Dead end).")
                    break
                elif len(valid_ext) > 1:
                    st.warning(f"Embranchement détecté (extensions: {valid_ext}). Le Filtre de Bloom peut engendrer des chemins fantômes (faux positifs) ou il s'agit d'une vraie répétition.")
                    stopped_by_bifurcation = True
                    break
                else:
                    current_kmer = valid_ext[0]
                    contig += current_kmer[-1]
                    
        st.success(f"**Contig assemblé :** {contig} (Longueur: {len(contig)})")
        if stopped_by_bifurcation:
            st.warning("L'assemblage s'est arrêté à cause d'une bifurcation. Les paramètres m et h du Filtre de Bloom pourraient être ajustés pour réduire les faux positifs.")
