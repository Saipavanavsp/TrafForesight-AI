import random
import networkx as nx

class HMOptimizer:
    def __init__(self, G_C, source, target, w_d=1.0, w_c=2.0, w_i=1.5, w_t=3.0, 
                 ants=15, iterations=30, alpha=1.0, beta=2.0, evaporation=0.1, q_learning_rate=0.1, q_discount=0.9):
        self.G_C = G_C
        self.source = source
        self.target = target
        
        self.w_d = w_d
        self.w_c = w_c
        self.w_i = w_i
        self.w_t = w_t
        
        self.ants = ants
        self.iterations = iterations
        self.alpha = alpha
        self.beta = beta
        self.evaporation = evaporation
        
        self.q_learning_rate = q_learning_rate
        self.gamma = q_discount
        
        self.init_pheromones()
        
    def init_pheromones(self):
        for u, v, k, data in self.G_C.edges(keys=True, data=True):
            data['pheromone'] = 1.0
            
    def compute_edge_cost(self, data):
        d_ij = data.get('w_distance', 10.0)
        C_ij = data.get('C_GAT', 0.1)
        I_ij = data.get('I_SAGE', 0.5)
        T_ij = data.get('T_LSTM', 10.0)
        
        cost = (self.w_d * d_ij) + (self.w_c * C_ij) - (self.w_i * I_ij) + (self.w_t * T_ij)
        return max(0.01, cost)
        
    def construct_ant_solution(self):
        current_node = self.source
        path = [current_node]
        path_cost = 0.0
        visited = set([current_node])
        
        max_steps = self.G_C.number_of_nodes()
        step = 0
        
        while current_node != self.target and step < max_steps:
            neighbors = list(self.G_C.successors(current_node)) if self.G_C.is_directed() else list(self.G_C.neighbors(current_node))
            unvisited_neighbors = [n for n in neighbors if n not in visited]
            
            if not unvisited_neighbors:
                return None, float('inf') 
                
            probabilities = []
            for n in unvisited_neighbors:
                # fetch min cost edge in case of parallel edges
                edge_data = min(dict(self.G_C[current_node][n]).values(), key=lambda e: self.compute_edge_cost(e))
                pheromone = edge_data['pheromone']
                cost = self.compute_edge_cost(edge_data)
                visibility = 1.0 / cost
                
                prob = (pheromone ** self.alpha) * (visibility ** self.beta)
                probabilities.append((n, prob, cost))
                
            total_prob = sum(p[1] for p in probabilities)
            if total_prob == 0:
                chosen = random.choice(probabilities)
            else:
                rand_val = random.uniform(0, total_prob)
                cumulative = 0.0
                for n, prob, cost in probabilities:
                    cumulative += prob
                    if cumulative >= rand_val:
                        chosen = (n, prob, cost)
                        break
                        
            next_node, _, next_cost = chosen
            path.append(next_node)
            visited.add(next_node)
            path_cost += next_cost
            current_node = next_node
            step += 1
            
        if current_node == self.target:
            return path, path_cost
        return None, float('inf')
        
    def optimize(self, baseline_path):
        print("Layer 3: HMO initialized. Minimizing unifying cost function via ACO + Q-Learning...")
        best_path = baseline_path
        best_cost = float('inf')
        
        for iteration in range(self.iterations):
            solutions = []
            for _ in range(self.ants):
                path, cost = self.construct_ant_solution()
                if path:
                    solutions.append((path, cost))
                    if cost < best_cost:
                        best_cost = cost
                        best_path = path
                        
            if iteration == 0 and baseline_path:
                # Seed the first iteration with baseline path 
                base_cost = 0.0
                for i in range(len(baseline_path)-1):
                    u, v = baseline_path[i], baseline_path[i+1]
                    k_opt = min(self.G_C[u][v].keys(), key=lambda k: self.compute_edge_cost(self.G_C[u][v][k]))
                    base_cost += self.compute_edge_cost(self.G_C[u][v][k_opt])
                solutions.append((baseline_path, base_cost))
                if base_cost < best_cost:
                    best_cost = base_cost
                    best_path = baseline_path
                        
            for u, v, k, data in self.G_C.edges(keys=True, data=True):
                data['pheromone'] *= (1 - self.evaporation)
                
            for path, cost in solutions:
                reward = 100.0 / cost 
                
                for i in range(len(path) - 1):
                    u = path[i]
                    v = path[i+1]
                    
                    edge_keys = list(self.G_C[u][v].keys())
                    k_opt = min(edge_keys, key=lambda k: self.compute_edge_cost(self.G_C[u][v][k]))
                    data = self.G_C[u][v][k_opt]
                    
                    old_phero = data['pheromone']
                    
                    max_future = 0
                    if i + 2 < len(path):
                        next_v = path[i+2]
                        n_keys = list(self.G_C[v][next_v].keys())
                        n_k_opt = min(n_keys, key=lambda k: self.compute_edge_cost(self.G_C[v][next_v][k]))
                        max_future = self.G_C[v][next_v][n_k_opt]['pheromone']
                        
                    new_phero = old_phero + self.q_learning_rate * (reward + self.gamma * max_future - old_phero)
                    data['pheromone'] = new_phero
                    
        return best_path, best_cost
