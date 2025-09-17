class Vehicle:
  _id_counter = 0
  def __init__(self, path_nodes, init_edge=None):
    self.id = Vehicle._id_counter
    Vehicle._id_counter += 1

    self.path_nodes = path_nodes
    self.edge_index = 0
    self.pos_on_edge = 0.0    # distancia em metros desdo o começo da aresta atual
    self.speed = 0.0
    self.finished = False
    self.waiting = False
    self.stats = {
      "travel_time": 0.0,
      "distance_travelled": 0.0
      }
    
  def current_edge(self):
    if self.edge_index < len(self.path_nodes) -1:
      return (self.path_nodes[self.edge_index], self.path_nodes[self.edge_index + 1])
    return None
  
  def advance_edge(self):
    self.edge_index +=1
    self.pos_on_edge = 0.0
    if self.edge_index >= len(self.path_nodes) -1:
      self.finished = True