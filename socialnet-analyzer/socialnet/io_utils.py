"""io_utils.py - load/save a network from a simple CSV edge list (user_a,user_b)."""
import csv
from .graph import Graph


def load_edge_list(path):
    g = Graph()
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.reader(f):
            if len(row) >= 2 and row[0].strip().lower() != "user_a":
                g.add_connection(row[0].strip(), row[1].strip())
    return g


def save_edge_list(graph, path):
    seen = set()
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["user_a", "user_b"])
        for u, friends in graph.adj.items():
            for v in friends:
                if (v, u) not in seen:
                    seen.add((u, v))
                    w.writerow([u, v])
