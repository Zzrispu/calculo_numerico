import osmnx as ox

location_point = (-2.427944, -54.714781)

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

ox.io.save_graphml(G, filepath="./data/network.graphml")