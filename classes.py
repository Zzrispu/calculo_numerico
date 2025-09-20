import random

class Vehicle:
  _id_counter = 0
  def __init__(self, path_nodes, G):
    self.id = Vehicle._id_counter
    Vehicle._id_counter += 1

    self.G = G
    self.path_nodes = path_nodes # rota (Lista de nós)
    self.edge_index = 0
    self.progress = 0.0    # distancia em metros desdo o começo da aresta atual
    self.speed = random.uniform(10.0, 25.0) # m/s
    self.finished = False
    self.color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
    
  def current_edge(self):
    if self.edge_index >= len(self.path_nodes) -1:
      return None
    
    u = self.path_nodes[self.edge_index]
    v = self.path_nodes[self.edge_index + 1]
    edge_data = self.G.get_edge_data( u, v, 0)
    lenth = edge_data['length']

    x1, y1 = self.G.nodes[u]['x'], self.G.nodes[u]['y']
    x2, y2 = self.G.nodes[v]['x'], self.G.nodes[v]['y']

    t = self.progress / lenth
    x = (1 - t) * x1 + t * x2
    y = (1 - t) * y1 + t * y2
    return x, y
  
  def update(self, dt):
    if self.edge_index >= len(self.path_nodes) -1:
      self.finished = True
      return
    
    u = self.path_nodes[self.edge_index]
    v = self.path_nodes[self.edge_index + 1]
    edge_data = self.G.get_edge_data( u, v, 0)
    lenth = edge_data['length']

    self.progress += self.speed * dt
    if self.progress >= lenth:
      self.progress = 0.0
      self.edge_index += 1