"""
benchmark.py - how do the algorithms behave as the network grows?
"""
import csv, os, random, time

from .generators import random_network, scale_free_network
from .traversal import bfs, dfs_iterative, dfs_path
from .analysis import shortest_path, bidirectional_shortest_path

SIZES = [1_000, 2_000, 5_000, 10_000, 20_000, 50_000, 100_000]
REPEATS = 5
QUERIES = 20
OUT = os.path.join(os.path.dirname(__file__), "..", "results")


def _best_ms(fn):
    best = float("inf")
    for _ in range(REPEATS):
        t = time.perf_counter()
        fn()
        best = min(best, time.perf_counter() - t)
    return best * 1000


def run(kind="random", sizes=SIZES, verbose=True):
    rows = []
    for n in sizes:
        g = random_network(n, 10) if kind == "random" else scale_free_network(n, 5)
        rng = random.Random(1)
        pairs = [(rng.randrange(n), rng.randrange(n)) for _ in range(QUERIES)]
        row = {
            "network": kind, "users": n, "connections": g.num_connections,
            "bfs_ms": _best_ms(lambda: bfs(g, 0)),
            "dfs_ms": _best_ms(lambda: dfs_iterative(g, 0)),
            "path_bfs_ms": _best_ms(lambda: [shortest_path(g, a, b) for a, b in pairs]),
            "path_bidir_ms": _best_ms(lambda: [bidirectional_shortest_path(g, a, b) for a, b in pairs]),
        }
        # quality check: how much longer are DFS paths than shortest paths?
        bfs_len = dfs_len = 0
        for a, b in pairs:
            p, d = shortest_path(g, a, b), dfs_path(g, a, b)
            if p and d:
                bfs_len += len(p) - 1
                dfs_len += len(d) - 1
        row["avg_hops_bfs"] = round(bfs_len / QUERIES, 2)
        row["avg_hops_dfs"] = round(dfs_len / QUERIES, 2)
        rows.append(row)
        if verbose:
            print({k: (round(v, 2) if isinstance(v, float) else v) for k, v in row.items()})
    return rows


def save(rows):
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "benchmark.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(1, 3, figsize=(16, 4.2))
    for kind, style in (("random", "-"), ("scale_free", "--")):
        r = [x for x in rows if x["network"] == kind]
        if not r:
            continue
        x = [i["users"] for i in r]
        ax[0].plot(x, [i["bfs_ms"] for i in r], "o" + style, label=f"BFS ({kind})")
        ax[0].plot(x, [i["dfs_ms"] for i in r], "s" + style, label=f"DFS ({kind})")
        ax[1].plot(x, [i["path_bfs_ms"] for i in r], "o" + style, label=f"BFS path ({kind})")
        ax[1].plot(x, [i["path_bidir_ms"] for i in r], "s" + style, label=f"Bidirectional ({kind})")
        ax[2].plot(x, [i["avg_hops_bfs"] for i in r], "o" + style, label=f"BFS ({kind})")
        ax[2].plot(x, [i["avg_hops_dfs"] for i in r], "s" + style, label=f"DFS ({kind})")
    ax[0].set(title="Full traversal time", xlabel="Users (V)", ylabel="ms")
    ax[1].set(title=f"{QUERIES} shortest-path queries", xlabel="Users (V)", ylabel="ms")
    ax[1].set_yscale("log")
    ax[2].set(title="Average path length found (hops)", xlabel="Users (V)", ylabel="hops")
    ax[2].set_yscale("log")
    for a in ax:
        a.grid(alpha=.3)
        a.legend(fontsize=7)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, "benchmark.png"), dpi=130)


def main():
    rows = run("random") + run("scale_free")
    save(rows)
    print("Saved results/benchmark.csv and results/benchmark.png")
