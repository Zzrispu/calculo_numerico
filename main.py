import networkx as nx
import osmnx as ox
import pygame
import random
import math
from classes import Vehicle
from typing import List

location_point = (-2.427944, -54.714781)

def main():
    G = ox.graph.graph_from_point(
        location_point,
        dist=1800,
        network_type="drive_service",
        simplify=False
    )

    G = ox.simplification.simplify_graph(G)

    G_proj = ox.project_graph(G)
    G = ox.consolidate_intersections(
        G_proj,
        rebuild_graph=True,
        tolerance=15,
        dead_ends=False
    )

    edges = ox.convert.graph_to_gdfs(G, nodes=False)
    edges["highway"] = edges["highway"].astype(str)

    hwy_speeds = {
        "residential": 35,
        "secundary": 50,
        "tertiary": 60
    }

    G = ox.routing.add_edge_speeds(G, hwy_speeds=hwy_speeds)
    G = ox.routing.add_edge_travel_times(G)

    nodes, edges = ox.convert.graph_to_gdfs(G)
    x = nodes["x"].values
    y = nodes["y"].values
    min_x, max_x = x.min(), x.max()
    min_y, max_y = y.min(), y.max()

    def norm_x(coord):
        return int((coord - min_x) / (max_x - min_x) * WIDHT)

    def norm_y(coord):
        return HEIGHT - int((coord - min_y) / (max_y - min_y) * HEIGHT)
    
    pygame.init()
    WIDHT, HEIGHT = 800, 600
    win = pygame.display.set_mode((WIDHT, HEIGHT))

    nos = list(G.nodes)
    vehicles: List[Vehicle] = []
    for _ in range(10):
        orig, dest = random.sample(nos, 2)
        
        try:
            path = nx.shortest_path(G, orig, dest, weight="travel_time")
            vehicles.append(Vehicle(path_nodes=path, G=G))
        except nx.NetworkXNoPath:
            print(f"No path between {orig} and {dest}")

    clock = pygame.time.Clock()
    running = True

    while running:
        dt = clock.tick(30) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # 
        win.fill((30, 30, 30))

        # Desenha as ruas
        for u, v in G.edges():
            x1, y1 = norm_x(G.nodes[u]["x"]), norm_y(G.nodes[u]["y"])
            x2, y2 = norm_x(G.nodes[v]["x"]), norm_y(G.nodes[v]["y"])
            pygame.draw.line(win, (200, 200, 200), (x1, y1), (x2, y2), 1)

        # Desenha e atualiza os veículos
        for vehicle in vehicles:
            vehicle.update(dt=dt)
            if vehicle.finished:
                vehicles.remove(vehicle)

            pos = vehicle.current_edge()
            if pos:
                x, y = norm_x(pos[0]), norm_y(pos[1])
                pygame.draw.circle(win, vehicle.color, (x, y), 4)

        pygame.display.flip()
    pygame.quit()
    

if __name__ == "__main__":
    main()
