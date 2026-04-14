import osmnx as ox
import networkx as nx

def build_graph(place_name='Liverpool, UK'):
    print(f"Downloading street network for {place_name} using osmnx...")
    G = ox.graph_from_place(place_name, network_type='drive')
    # Add basic attributes for time calculations
    G = ox.add_edge_speeds(G)
    try:
        G = ox.add_edge_travel_times(G)
    except Exception as e:
        print("Could not add standard travel times, defaulting lengths.")
    return G

def get_baseline_path(G, source, target):
    print("Computing baseline Dijkstra path...")
    try:
        # Standard Dijkstra based on edge length
        path = nx.shortest_path(G, source, target, weight='length')
        # calculate length
        length = sum(min(dict(G[u][v]).values(), key=lambda x: x.get('length', float('inf'))).get('length', 0) for u, v in zip(path[:-1], path[1:]))
        return path, length
    except nx.NetworkXNoPath:
        print("No path found between source and target.")
        return None, float('inf')

def extract_corridor(G, path, epsilon=3):
    print(f"Extracting Corridor Graph G_C with epsilon={epsilon} hops...")
    corridor_nodes = set()
    for node in path:
        # Gets all nodes within 'epsilon' hops (ignoring edge weights)
        neighbors = nx.single_source_shortest_path_length(G, node, cutoff=epsilon)
        corridor_nodes.update(neighbors.keys())
        
    G_C = G.subgraph(corridor_nodes).copy()
    
    total_nodes = G.number_of_nodes()
    corridor_nodes_count = G_C.number_of_nodes()
    reduction = (1 - (corridor_nodes_count / total_nodes)) * 100
    
    print(f"Original Graph Nodes: {total_nodes}")
    print(f"Corridor Graph Nodes: {corridor_nodes_count}")
    print(f"Search Space Reduction: {reduction:.2f}%")
    
    return G_C
