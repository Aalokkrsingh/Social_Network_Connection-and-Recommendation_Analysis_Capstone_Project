"""generators.py - make networks of any size for the performance experiments."""
import random
from .graph import Graph


def random_network(n, avg_degree=10, seed=42):
    """Random graph: every connection links two uniformly random users."""
    rng = random.Random(seed)
    g = Graph()
    for i in range(n):
        g.add_user(i)
    for _ in range(n * avg_degree // 2):
        g.add_connection(rng.randrange(n), rng.randrange(n))
    return g


def scale_free_network(n, m=5, seed=42):
    """
    Preferential attachment (Barabasi-Albert): new users prefer to connect to
    already-popular users, which creates a few 'celebrity hubs' like real
    social networks.
    """
    rng = random.Random(seed)
    g = Graph()
    targets = list(range(m))
    for t in targets:
        g.add_user(t)
    pool = []                                  # a user appears once per connection
    for new in range(m, n):
        for t in set(targets):
            g.add_connection(new, t)
        pool.extend(targets)
        pool.extend([new] * m)
        targets = [rng.choice(pool) for _ in range(m)]
    return g
