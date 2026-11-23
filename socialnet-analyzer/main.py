"""
Command-line interface.

  python main.py info
  python main.py bfs Aalok
  python main.py dfs Aalok
  python main.py mutual Aalok Riya
  python main.py path Aalok Pooja
  python main.py recommend Aalok
  python main.py benchmark
Add --data your_edges.csv to use your own network (columns: user_a,user_b).
"""
import argparse, os, sys

from socialnet.io_utils import load_edge_list
from socialnet import traversal, analysis

DEFAULT = os.path.join(os.path.dirname(__file__), "data", "sample_network.csv")


def need(g, *users):
    for u in users:
        if not g.has_user(u):
            sys.exit(f"User '{u}' not found. Try one of: {', '.join(sorted(g.users())[:8])} ...")


def main():
    p = argparse.ArgumentParser(description="Social network analyzer")
    p.add_argument("command", choices=["info", "bfs", "dfs", "mutual", "path", "recommend", "benchmark"])
    p.add_argument("users", nargs="*")
    p.add_argument("--data", default=DEFAULT)
    a = p.parse_args()

    if a.command == "benchmark":
        from socialnet import benchmark
        return benchmark.main()

    g = load_edge_list(a.data)
    if a.command == "info":
        for k, v in analysis.degree_stats(g).items():
            print(f"{k:>15}: {v}")
        comps = analysis.connected_components(g)
        print(f"{'communities':>15}: {len(comps)} (sizes {[len(c) for c in comps]})")
        print(f"{'avg clustering':>15}: {analysis.average_clustering(g):.3f}")
        print(f"{'avg path length':>15}: {analysis.average_path_length(g):.2f} hops")
        return
    if a.command in ("bfs", "dfs", "recommend"):
        if len(a.users) != 1:
            sys.exit(f"'{a.command}' needs exactly one user")
        u = a.users[0]; need(g, u)
        if a.command == "bfs":
            order, dist, _ = traversal.bfs(g, u)
            for x in order:
                print(f"  {dist[x]} hop(s): {x}")
        elif a.command == "dfs":
            print(" -> ".join(traversal.dfs_iterative(g, u)))
        else:
            for name, mutual in analysis.recommend_friends(g, u):
                print(f"  {name}  ({mutual} mutual friend{'s' if mutual > 1 else ''})")
        return
    if len(a.users) != 2:
        sys.exit(f"'{a.command}' needs exactly two users")
    x, y = a.users; need(g, x, y)
    if a.command == "mutual":
        print(sorted(analysis.mutual_connections(g, x, y)) or "No mutual connections")
    else:
        path = analysis.shortest_path(g, x, y)
        print(" -> ".join(path) + f"   ({len(path) - 1} hops)" if path else "Not connected")
        dp = traversal.dfs_path(g, x, y)
        if dp:
            print(f"(a DFS path would be {len(dp) - 1} hops: {' -> '.join(dp)})")


if __name__ == "__main__":
    main()
