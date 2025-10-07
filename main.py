import networkx as nx
import osmnx as ox
import pygame
import random
import math
from classes.vehicle import Vehicle
from classes.trafficLight import TrafficLight
from typing import List

location_point = (-2.427944, -54.714781)
WIDTH, HEIGHT = 1000, 800

def main():
    G = ox.load_graphml(filepath='./data/network.graphml')

    nodes, edges = ox.convert.graph_to_gdfs(G)
    x = nodes["x"].values
    y = nodes["y"].values
    zoom = 1.0
    zoom_speed = 0.2
    offset_x = 0
    offset_y = 0
    min_x, max_x = x.min(), x.max()
    min_y, max_y = y.min(), y.max()

    dragging = False
    last_mouse_pos = None

    def norm_x(coord):
        normalized_x = (coord - min_x) / (max_x - min_x) * WIDTH
        return int((normalized_x - WIDTH / 2 + offset_x) * zoom + WIDTH / 2)
    # normalized_x - WIDTH / 2 | Centraliza o zoom no meio da tela

    def norm_y(coord):
        normalized_y = HEIGHT - (coord - min_y) / (max_y - min_y) * HEIGHT
        return int((normalized_y - HEIGHT / 2 + offset_y) * zoom + HEIGHT / 2)
    
    def edge_distance(px, py, x1, y1, x2, y2):
        A = px - x1
        B = py - y1
        C = x2 - x1
        D = y2 - y1

        dot = A * C + B * D
        len_sq = C * C + D * D
        t = max(0, min(1, dot / len_sq)) if len_sq != 0 else 0

        xx = x1 + t * C
        yy = y1 + t * D
        return math.hypot(px - xx, py - yy)

    def point_to_edge_distance(px: int, py: int, u:int, v:int, data: dict):
        if "geometry" in data and data["geometry"] is not None:
            coords_geo = list(data["geometry"].coords)
        else:
            coords_geo = [(G.nodes[u]["x"], G.nodes[u]["y"]), (G.nodes[v]["x"], G.nodes[v]["y"])]
        
        screen_coords = [(norm_x(cx), norm_y(cy)) for cx, cy in coords_geo]

        xs = [c[0] for c in screen_coords]
        ys = [c[1] for c in screen_coords]
        bbox_tol = 6
        if px < min(xs) - bbox_tol or px > max(xs) + bbox_tol or py < min(ys) - bbox_tol or py > max(ys) + bbox_tol:
            return float("inf")
        
        min_dist = float("inf")
        for i in range(len(screen_coords) - 1):
            x1, y1 = screen_coords[i]
            x2, y2 = screen_coords[i + 1]
            d = edge_distance(px, py, x1, y1, x2, y2)
            if d < min_dist:
                min_dist = d
        return min_dist
    
    def get_closest_node(mx: int, my: int):
        min_dist = float("inf")
        closest_node = None
        for node, data in G.nodes(data=True):
            x, y = norm_x(data["x"]), norm_y(data["y"])
            dist = math.hypot(mx - x, my - y)
            if dist < min_dist:
                min_dist = dist
                closest_node = node
        return closest_node, min_dist

    # Inicializando o Pygame
    pygame.init()
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Simulação de Tráfego")
    font = pygame.font.SysFont("Arial", 18)
    
    nos = list(G.nodes)

    # Inicia os Veículos
    vehicles: List[Vehicle] = []
    for _ in range(60): # Quantidade de Veículso que tatará ser spawnado
        orig, dest = random.sample(nos, 2)
        
        try:
            path = nx.shortest_path(G, orig, dest, weight="travel_time")
            vehicles.append(Vehicle(path_nodes=path, G=G))
        except nx.NetworkXNoPath:
            print(f"No path between {orig} and {dest}")

    # Inicia os Semáforos
    traffic_lights: List[TrafficLight] = []
    
    selected_vehicle = None
    selected_edge = None

    clock = pygame.time.Clock()
    running = True

    # UI de texto
    info_text = ""

    # GAME LOOP
    while running:
        dt = clock.tick(30) / 1000.0

        for event in pygame.event.get():
            # Quando o jogo fecha
            if event.type == pygame.QUIT:
                running = False
            
            # Detecta quando um botão do mouse é precionado
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                clicked = False

                # Detecta o click esquerdo do mouse
                if event.button == 1:
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
                        closest = None
                        min_dist = float('inf')

                        for u, v, k, data in G.edges(keys=True, data=True):
                            dist = point_to_edge_distance(mx, my, u, v, data)
                            if dist < min_dist:
                                min_dist = dist
                                closest = (u, v, k, data)

                        if closest and min_dist < 4: # tolerância de clique em pixels
                            u, v, k, data = closest
                            name = data.get("name", "Sem nome")

                            vel = data.get("maxspeed") or data.get("speed_kph") or data.get("speed") or "N/A"
                            if isinstance(vel, (list, tuple)):
                                vel = vel[0] if vel else "N/A"
                            elif isinstance(vel, str):
                                import re
                                m = re.search(r"\d+", vel)
                                vel = m.group(0) if m else vel

                            vehicles_ = data.get("vehicles", "")

                            comp = data.get("length", 0)
                            info_text = f"Nome: {name} | Vel Máx: {vel} | Comp: {comp:.1f} m | Qtd. Veículos: {len(vehicles_)}"
                            selected_vehicle = None
                            selected_edge = (u, v, k)
                            clicked = True
                            break

                # Detecta o click do meio do mouse (scroll)
                elif event.button == 2:
                    dragging = True
                    last_mouse_pos = event.pos

                # Detecta o click direito do mouse
                elif event.button == 3:
                    node, dist = get_closest_node(mx, my)

                    if node and G.nodes[node].get("traffic_light") is not None and dist < 6:
                        traffic_lights.remove(G.nodes[node]["traffic_light"])
                        G.nodes[node]["traffic_light"] = None
                        info_text = f"Semáforo removido no nó {node}"

                    elif node and dist < 6:
                        pos = (G.nodes[node]["x"], G.nodes[node]["y"])
                        traffic_light = TrafficLight(pos)
                        G.nodes[node]["traffic_light"] = traffic_light
                        traffic_lights.append(traffic_light)
                        info_text = f"Semáforo adicionado no nó {node}"

                    clicked = True
                
                if not clicked: 
                    info_text = ""
                    selected_vehicle = None
                    selected_edge = None
            
            # Detecta quando um botão do mouse é solto
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 2:
                    dragging = False

            # Detecta o scroll do mouse
            elif event.type == pygame.MOUSEWHEEL:
                if event.y > 0:
                    zoom = min(zoom + zoom_speed, 6) # zoom in maxímo
                elif event.y < 0:
                    zoom = max(zoom - (zoom_speed * 2), 1) # zoom out maxímo

            # Detecta o movimento do mouse
            elif event.type == pygame.MOUSEMOTION:
                if dragging:
                    mx, my = event.pos
                    lx, ly = last_mouse_pos
                    offset_x += (mx - lx) / zoom
                    offset_y += (my - ly) / zoom
                    last_mouse_pos = (mx, my)

        win.fill((30, 30, 30))

        # Desenha as ruas
        for u, v, k in G.edges(keys=True):
            x1, y1 = norm_x(G.nodes[u]["x"]), norm_y(G.nodes[u]["y"])
            x2, y2 = norm_x(G.nodes[v]["x"]), norm_y(G.nodes[v]["y"])

            color = (200, 200, 200)
            width = 2

            if selected_edge == (u, v, k):
                color = (200, 0, 200)
                width = 4
            
            pygame.draw.line(win, color, (x1, y1), (x2, y2), width=width)

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

        # Desenha e atualiza os semáforos
        for traffic_light in traffic_lights:
            traffic_light.update(dt)
            x, y = norm_x(traffic_light.coords[0]), norm_y(traffic_light.coords[1])
            color = (0, 255, 0) if traffic_light.isGreen else (255, 0, 0)
            pygame.draw.circle(win, color, (x, y), 5)

        # Desenhar UI
        if info_text:
            text_suface = font.render(info_text, True, (255, 255, 255))
            win.blit(text_suface, (10, HEIGHT - 20))

        pygame.display.flip()
    pygame.quit()
    

if __name__ == "__main__":
    main()