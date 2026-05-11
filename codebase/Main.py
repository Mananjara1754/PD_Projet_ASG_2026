def generate_kmers(sequence: str, k: int) -> list[str]:
    """
    Découpe une séquence en sous-séquences de taille k (k-mers).
    Exemple: pour "ACTGA" avec k=3, on obtient ["ACT", "CTG", "TGA"].
    """
    kmers = []
    for i in range(len(sequence) - k + 1):
        kmers.append(sequence[i:i + k])
    return kmers

def extract_all_kmers(reads: list[str], k: int) -> list[str]:
    """
    Extrait tous les k-mers d'une liste de séquences de lecture (reads).
    """
    all_kmers = []
    for read in reads:
        all_kmers.extend(generate_kmers(read, k))
    return all_kmers

def build_de_bruijn_graph(kmers: list[str]) -> dict[str, list[str]]:
    """
    Construit un graphe de de Bruijn à partir d'une liste de k-mers.
    Chaque k-mer est un nœud. Une arête relie kmer1 à kmer2 si 
    le suffixe de kmer1 correspond au préfixe de kmer2.
    """
    graph = {}
    for kmer1 in kmers:
        graph[kmer1] = []
        for kmer2 in kmers:
            # On vérifie si le suffixe de kmer1 (tout sauf la 1ère lettre)
            # est égal au préfixe de kmer2 (tout sauf la dernière lettre)
            if kmer1[1:] == kmer2[:-1]:
                graph[kmer1].append(kmer2)
    return graph

def assemble_contig(graph: dict[str, list[str]], start_kmer: str) -> str:
    """
    Parcourt le graphe pour assembler la séquence finale (contig).
    On part d'un k-mer de départ et on ajoute la dernière lettre 
    du k-mer suivant à chaque étape.
    """
    current = start_kmer
    contig = current
    visited = set()
    
    # Tant que le k-mer actuel a des voisins (extensions possibles)
    while current in graph and len(graph[current]) > 0:
        # On prend simplement le premier voisin trouvé
        next_kmer = graph[current][0]
        
        # Sécurité pour éviter de tourner en rond (boucle infinie)
        if next_kmer in visited:
            break
            
        visited.add(next_kmer)
        
        # On ajoute uniquement le dernier nucléotide au contig
        contig += next_kmer[-1]
        current = next_kmer
        
    return contig

def main():
    reads = [
        "ACTGA",
        "TGATC",
        "ATCCG"
    ]
    
    # ATTENTION : Vos reads font 5 lettres. 
    # Avec k=13 comme dans l'ancien code, vous n'obteniez aucun k-mer (car 13 > 5).
    # J'ai corrigé en mettant k=3 pour que l'exemple fonctionne.
    k = 3
    
    print(f"--- Pipeline d'assemblage avec k={k} ---")
    
    # 1. Extraction
    kmers = extract_all_kmers(reads, k)
    print(f"1. K-mers extraits ({len(kmers)}) :", kmers)
    
    if len(kmers) == 0:
        print("Erreur : Aucun k-mer généré. Vérifiez la taille de k.")
        return
        
    # 2. Construction du graphe
    graph = build_de_bruijn_graph(kmers)
    print("\n2. Graphe construit. Aperçu :")
    for node, neighbors in graph.items():
        if neighbors:  # On n'affiche que les noeuds qui ont des voisins pour la clarté
            print(f"   {node} -> {neighbors}")
            
    # 3. Assemblage
    start_node = kmers[0]
    final_contig = assemble_contig(graph, start_node)
    print(f"\n3. Contig final assemblé : {final_contig}")

if __name__ == "__main__":
    main()