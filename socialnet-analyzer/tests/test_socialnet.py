import os, random, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from socialnet.graph import Graph
from socialnet.traversal import bfs, dfs_iterative, dfs_recursive, dfs_path
from socialnet.analysis import *
from socialnet.generators import random_network, scale_free_network
from socialnet.io_utils import load_edge_list, save_edge_list


def small():
    g = Graph()
    for a, b in [(1, 2), (1, 3), (2, 4), (3, 4), (4, 5), (6, 7)]:
        g.add_connection(a, b)
    return g


def test_graph_is_undirected_and_ignores_self_loops():
    g = Graph(); g.add_connection("a", "b"); g.add_connection("a", "a")
    assert "a" in g.neighbors("b") and g.num_connections == 1


def test_bfs_distances_and_depth_limit():
    _, d, _ = bfs(small(), 1)
    assert d == {1: 0, 2: 1, 3: 1, 4: 2, 5: 3}
    assert 5 not in bfs(small(), 1, max_depth=2)[1]


def test_dfs_variants_agree_on_reachable_set():
    g = small()
    assert set(dfs_iterative(g, 1)) == set(dfs_recursive(g, 1)) == set(bfs(g, 1)[0])


def test_dfs_path_valid_but_not_shorter_than_bfs():
    g = random_network(300, 4)
    rng = random.Random(3)
    for _ in range(50):
        a, b = rng.randrange(300), rng.randrange(300)
        p, d = shortest_path(g, a, b), dfs_path(g, a, b)
        assert (p is None) == (d is None)
        if p:
            assert len(d) >= len(p)
            assert all(d[i + 1] in g.neighbors(d[i]) for i in range(len(d) - 1))


def test_mutual_and_shortest():
    g = small()
    assert mutual_connections(g, 2, 3) == {1, 4}
    assert len(shortest_path(g, 1, 5)) == 4
    assert shortest_path(g, 1, 7) is None and shortest_path(g, 1, 1) == [1]


def test_bidirectional_equals_bfs_length():
    g = random_network(500, 4)
    rng = random.Random(0)
    for _ in range(100):
        a, b = rng.randrange(500), rng.randrange(500)
        p, q = shortest_path(g, a, b), bidirectional_shortest_path(g, a, b)
        assert (p is None) == (q is None)
        if p:
            assert len(p) == len(q) and q[0] == a and q[-1] == b
            assert all(q[i + 1] in g.neighbors(q[i]) for i in range(len(q) - 1))


def test_components_and_recommend():
    g = small()
    assert [len(c) for c in connected_components(g)] == [5, 2]
    assert recommend_friends(g, 1) == [(4, 2)]


def test_clustering_triangle_is_one():
    g = Graph()
    for a, b in [(1, 2), (2, 3), (1, 3)]:
        g.add_connection(a, b)
    assert clustering_coefficient(g, 1) == 1.0


def test_generators():
    assert random_network(100, 6).num_users == 100
    g = scale_free_network(200, 3)
    assert g.num_users == 200 and max(g.degree(u) for u in g.users()) > 15


def test_csv_roundtrip(tmp_path):
    g = small(); p = tmp_path / "x.csv"
    save_edge_list(g, p)
    h = load_edge_list(p)
    assert h.num_connections == g.num_connections


def test_sample_dataset_loads():
    g = load_edge_list(os.path.join(os.path.dirname(__file__), "..", "data", "sample_network.csv"))
    assert g.num_users == 20 and len(connected_components(g)) == 2
