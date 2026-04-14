import torch
import torch.nn as nn
from torch_geometric.nn import GATv2Conv, SAGEConv

# Temporal - LSTM for forecasting traffic time
class TemporalLSTM(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers=2):
        super(TemporalLSTM, self).__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, 1)
        
    def forward(self, x):
        out, _ = self.lstm(x)
        return self.fc(out[:, -1, :]) 

# Spatial - GAT for traffic propagation
class SpatialGAT(nn.Module):
    def __init__(self, in_channels, out_channels, heads=4):
        super(SpatialGAT, self).__init__()
        self.gat = GATv2Conv(in_channels, out_channels // heads, heads=heads)
        
    def forward(self, x, edge_index):
        return self.gat(x, edge_index)

# Infrastructure - GraphSAGE for importance scoring
class InfraSAGE(nn.Module):
    def __init__(self, in_channels, hidden_channels):
        super(InfraSAGE, self).__init__()
        self.sage = SAGEConv(in_channels, hidden_channels)
        self.fc = nn.Linear(hidden_channels, 1)
        
    def forward(self, x, edge_index):
        out = self.sage(x, edge_index)
        return torch.sigmoid(self.fc(out)) 

def generate_ai_costs(G_C):
    print("Layer 2: AI Predictive Intelligence initializing...")
    print(" -> Simulating historical temporal dependencies (LSTM)")
    print(" -> Modeling spatial traffic propagation (GAT)")
    print(" -> Calculating infrastructure importance (GraphSAGE)")
    
    # We simulate the AI generated features and map them to NetworkX edges
    for u, v, k, data in G_C.edges(keys=True, data=True):
        data['C_GAT'] = torch.rand(1).item() * 0.5 
        
        highway = data.get('highway', 'residential')
        if type(highway) == list:
            highway = highway[0]
            
        base_I = 0.3
        if highway in ['motorway', 'trunk', 'primary']: 
            base_I = 0.9
        elif highway in ['secondary', 'tertiary']: 
            base_I = 0.6
        data['I_SAGE'] = base_I + (torch.rand(1).item() * 0.1) 
        
        length = data.get('length', 10.0)
        speed_kmh = data.get('maxspeed', 50)
        if type(speed_kmh) == list: speed_kmh = speed_kmh[0]
        try:
            speed_kmh = float(speed_kmh)
        except:
            speed_kmh = 50.0
            
        speed_ms = speed_kmh * 1000 / 3600
        baseline_time = length / speed_ms
        
        lstm_prediction_factor = 1.0 + (data['C_GAT'] * 1.5) 
        data['T_LSTM'] = baseline_time * lstm_prediction_factor
        data['w_distance'] = length
        
    return G_C
