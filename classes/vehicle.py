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

  def __str__(self):
    return self.id

  def __get_current_edge_data(self):
    if self.edge_index >= len(self.path_nodes) -1: return None
    u = self.path_nodes[self.edge_index]
    v = self.path_nodes[self.edge_index + 1]
    edge_data = self.G.get_edge_data( u, v, 0)
    return edge_data, u, v

  def __register_on_edge(self, edge_data):
    if edge_data is not None and "vehicles" not in edge_data:
      edge_data["vehicles"] = []
    edge_data["vehicles"].append(self)

  def __unregister_from_edge(self, edge_data):
    if edge_data is not None and "vehicles" in edge_data:
      if self in edge_data["vehicles"]:
        edge_data["vehicles"].remove(self)
    
  def current_edge(self):
    if self.edge_index >= len(self.path_nodes) -1:
      return None
    
    edge_data, u, v = self.__get_current_edge_data()
    lenth = edge_data['length']

    x1, y1 = self.G.nodes[u]['x'], self.G.nodes[u]['y']
    x2, y2 = self.G.nodes[v]['x'], self.G.nodes[v]['y']

    t = self.progress / lenth
    x = (1 - t) * x1 + t * x2
    y = (1 - t) * y1 + t * y2
    return x, y
  
  def update(self, dt):
    if self.edge_index >= len(self.path_nodes) - 1:
      self.finished = True
      return

    edge_data, u, v = self.__get_current_edge_data()
    lenth = edge_data['length']

    traffic_light = self.G.nodes[v].get("traffic_light")
    if traffic_light is not None and not traffic_light.isGreen:
      dist_to_tl = lenth - self.progress
      if dist_to_tl <= 10:
        self.progress = lenth - 10
        return

      if "vehicles" in edge_data:
        for other_vehicle in edge_data["vehicles"]:
          if other_vehicle is not self and other_vehicle.progress > self.progress:
            dist_to_vehicle = other_vehicle.progress - self.progress
            if dist_to_vehicle <= 5:
              self.progress = other_vehicle.progress - 5
              return

    self.progress += self.speed * dt
    if self.progress >= lenth:
      self.__unregister_from_edge(edge_data)
      self.progress = 0.0
      self.edge_index += 1

      next_edge = self.__get_current_edge_data()
      if next_edge is not None:
        self.__register_on_edge(next_edge[0])