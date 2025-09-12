import networkx as nx
import osmnx as ox

location_point = (-2.427944, -54.714781)

def main():
    G = ox.graph.graph_from_point(
        location_point,
        dist=3700,
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
    # edges.groupby("highway")[["length", "speed_kph", "travel_time"]].mean().round(1)

    hwy_speeds = {
        "residential": 35,
        "secundary": 50,
        "tertiary": 60
    }

    G = ox.routing.add_edge_speeds(G, hwy_speeds=hwy_speeds)
    G = ox.routing.add_edge_travel_times(G)

    # orig = list(G.nodes)[321]
    # dest = list(G.nodes)[123]
    # route1 = ox.routing.shortest_path(G, orig=orig, dest=dest, weight="length")
    # route2 = ox.routing.shortest_path(G, orig=orig, dest=dest, weight="travel_time")

    # ec = ox.plot.get_edge_colors_by_attr(G, attr="length", cmap="plasma_r") # Destaca o comprimento das ruas
    # ec = ["gray" if k == 0 or u == v else "r" for u, v, k in G.edges(keys=True)] # Destaca as ruas sem conexão
    ec = ["blue" if data["oneway"] else "w" for u, v, key, data in G.edges(keys=True, data=True)] # Destaca as ruas de mão única

    ox.io.save_graphml(G, filepath=".data/network.graphml")

    # route1_length = int(sum(ox.routing.route_to_gdf(G, route1, weight="length")["length"]))
    # route2_length = int(sum(ox.routing.route_to_gdf(G, route2, weight="travel_time")["length"]))
    # route1_time = int(sum(ox.routing.route_to_gdf(G, route1, weight="length")["travel_time"]))
    # route2_time = int(sum(ox.routing.route_to_gdf(G, route2, weight="travel_time")["travel_time"]))
    # print(f"Rota 1 - Distância: {route1_length}m | Tempo: {route1_time}s")
    # print(f"Rota 2 - Distância: {route2_length}m | Tempo: {route2_time}s")

    fig, ax = ox.plot.plot_graph(
        G,
        # routes=[route1, route2],
        # route_colors=["r", "y"],
        node_color="w",
        node_edgecolor="k",
        node_size=5,
        edge_color=ec,
        edge_linewidth=1.5
    )


if __name__ == "__main__":
    main()
