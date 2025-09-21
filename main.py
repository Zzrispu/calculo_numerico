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
    
    # Inicializando o Pygame
    pygame.init()
    WIDHT, HEIGHT = 800, 600
    win = pygame.display.set_mode((WIDHT, HEIGHT))
    pygame.display.set_caption("Simulação de Tráfego")
    font = pygame.font.SysFont("Arial", 16)

    nos = list(G.nodes)

    # Inicia os Veículos
    vehicles: List[Vehicle] = []
    for _ in range(20): # Quantidade de Veículso que tatará ser spawnado
        orig, dest = random.sample(nos, 2)
        
        try:
            path = nx.shortest_path(G, orig, dest, weight="travel_time")
            vehicles.append(Vehicle(path_nodes=path, G=G))
        except nx.NetworkXNoPath:
            print(f"No path between {orig} and {dest}")
    selected_vehicle = None

    clock = pygame.time.Clock()
    running = True

    # UI de texto
    info_text = ""

    def egde_distance(px: int, py: int, x1: int, y1: int, x2: int, y2: int):
        A = px - x1
        B = py - y1
        C = x2 - x1
        D = y2 - x2

        dot = A * C + B * D
        len_sq = C * C + D * D
        t = max(0, min(1, dot / len_sq)) if len_sq != 0 else 0

        xx = x1 + t * C
        yy = y1 + t * D
        return math.hypot(px - xx, py - yy)

    while running:
        dt = clock.tick(30) / 1000.0

        for event in pygame.event.get():
            # Quando o jogo fecha
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                clicked = False

                # Verifica clique em veículos
                for vehicle in vehicles:
                    pos = vehicle.current_edge()
                    if pos:
                        x = norm_x(pos[0])
                        y = norm_y(pos[1])
                        if math.hypot(mx - x, my - y) < 6:
                            info_text = f"ID: {vehicle.id} | Vel: {vehicle.speed:.1f} m/s | Index rota: {vehicle.edge_index}/{len(vehicle.path_nodes)}"
                            selected_vehicle = vehicle
                            clicked = True
                            break
                
                # Verificar clique me ruas (arestas)
                if not clicked:
                    selected_vehicle = None
                    for u, v, data in G.edges(data=True):
                        x1, y1 = norm_x(G.nodes[u]["x"]), norm_y(G.nodes[u]["y"])
                        x2, y2 = norm_x(G.nodes[v]["x"]), norm_y(G.nodes[v]["y"])
                        dist = egde_distance(mx, my, x1, y1, x2, y2)
                        if dist < 2: # tolerância de clique em pixels
                            name = data.get("name", "Sem nome")
                            vel = data.get("maxspeed", "N/A")
                            comp = data.get("length", 0)
                            info_text = f"Nome: {name} | Vel Máx: {vel} | Comp: {comp:.1f} m"
                            clicked = True
                            break
                
                if not clicked: 
                    info_text = ""
        
        win.fill((30, 30, 30))

        # Desenha as ruas
        for u, v in G.edges():
            x1, y1 = norm_x(G.nodes[u]["x"]), norm_y(G.nodes[u]["y"])
            x2, y2 = norm_x(G.nodes[v]["x"]), norm_y(G.nodes[v]["y"])
            pygame.draw.line(win, (200, 200, 200), (x1, y1), (x2, y2), 2)

        # Desenha e atualiza os veículos
        for vehicle in vehicles:
            vehicle.update(dt=dt)
            if vehicle.finished:
                vehicles.remove(vehicle)

            pos = vehicle.current_edge()
            if pos:
                x, y = norm_x(pos[0]), norm_y(pos[1])
                pygame.draw.circle(win, vehicle.color, (x, y), 4)

        # Desenha rota do veículo selecionado
        if selected_vehicle:
            route = selected_vehicle.path_nodes
            for i in range(len(route) - 1):
                u, v = route[i], route[i +1]
                x1, y1 = norm_x(G.nodes[u]["x"]), norm_y(G.nodes[u]["y"])
                x2, y2 = norm_x(G.nodes[v]["x"]), norm_y(G.nodes[v]["y"])
                pygame.draw.line(win, (0, 200, 0), (x1, y1), (x2, y2), 3)

        # Desenhar UI
        if info_text:
            text_suface = font.render(info_text, True, (255, 255, 255))
            win.blit(text_suface, (10, HEIGHT - 20))

        pygame.display.flip()
    pygame.quit()
    

if __name__ == "__main__":
    main()
