"""
analysis.py - the questions we ask of the network.
"""
import random
from collections import Counter, deque

from .traversal import bfs


# ---------- 1. Mutual connections ----------
def mutual_connections(graph, a, b):
    """Friends that both a and b have = intersection of the two friend sets."""
    return graph.neighbors(a) & graph.neighbors(b)


# ---------- 2. Shortest connection path ----------
def shortest_path(graph, source, target):
    """
    Fewest-hops path using BFS. BFS reaches every user in order of distance,
    so the first time we reach `target` is guaranteed to be via a shortest path.
    Returns a list of users, or None if they are not connected.
    """
    if source == target:
        return [source]
    parent = {source: None}
    queue = deque([source])
    while queue:
        u = queue.popleft()
        for v in graph.neighbors(u):
            if v not in parent:
                parent[v] = u
                if v == target:                       # early exit
                    return _rebuild(parent, v)
                queue.append(v)
    return None


def _rebuild(parent, node):
    path = []
    while node is not None:                           # walk back to the source
        path.append(node)
        node = parent[node]
    return path[::-1]


def bidirectional_shortest_path(graph, source, target):
    """Optimisation: search from BOTH ends and stop when the searches meet.
    Two small searches of depth d/2 are much cheaper than one of depth d."""
    if source == target:
        return [source]
    pa, pb = {source: None}, {target: None}
    qa, qb = deque([source]), deque([target])
    while qa and qb:
        q, mine, other = (qa, pa, pb) if len(qa) <= len(qb) else (qb, pb, pa)
        for _ in range(len(q)):                       # expand one full level
            u = q.popleft()
            for v in graph.neighbors(u):
                if v not in mine:
                    mine[v] = u
                    if v in other:                    # the two searches met
                        return _rebuild(pa, v) + _rebuild(pb, v)[::-1][1:]
                    q.append(v)
    return None


# ---------- 3. Communities ----------
def connected_components(graph):
    """Groups of users who can reach each other. Biggest group first."""
    seen, groups = set(), []
    for u in graph.users():
        if u not in seen:
            order, _, _ = bfs(graph, u)
            seen.update(order)
            groups.append(order)
    return sorted(groups, key=len, reverse=True)


# ---------- 4. Recommendations ----------
def recommend_friends(graph, user, top_k=5):
    """
    'People you may know'. For every friend of `user`, look at THEIR friends;
    anyone who is not already a friend gets +1 per shared friend.
    Returns [(candidate, mutual_friend_count), ...] best first.
    """
    friends = graph.neighbors(user)
    score = Counter()
    for f in friends:
        for candidate in graph.neighbors(f):
            if candidate != user and candidate not in friends:
                score[candidate] += 1
    return score.most_common(top_k)


# ---------- 5. Network statistics ----------
def degree_stats(graph):
    degs = {u: graph.degree(u) for u in graph.users()}
    n, m = graph.num_users, graph.num_connections
    top = max(degs, key=degs.get)
    return {
        "users": n,
        "connections": m,
        "average_degree": round(2 * m / n, 2) if n else 0,
        "max_degree": degs[top],
        "most_connected": top,
        "density": round(2 * m / (n * (n - 1)), 4) if n > 1 else 0,
    }


def clustering_coefficient(graph, user):
    """Fraction of a user's friend pairs who are also friends with each other."""
    nb = list(graph.neighbors(user))
    k = len(nb)
    if k < 2:
        return 0.0
    links = sum(1 for i in range(k) for j in range(i + 1, k)
                if nb[j] in graph.neighbors(nb[i]))
    return links / (k * (k - 1) / 2)


def average_clustering(graph):
    users = graph.users()
    return sum(clustering_coefficient(graph, u) for u in users) / len(users)


def average_path_length(graph, samples=50, seed=0):
    """Estimated by running BFS from random users inside the biggest component."""
    rng = random.Random(seed)
    comp = connected_components(graph)[0]
    starts = rng.sample(comp, min(samples, len(comp)))
    total = count = 0
    for s in starts:
        _, dist, _ = bfs(graph, s)
        total += sum(dist.values())
        count += len(dist) - 1
    return total / count if count else 0.0


def degrees_of_separation(graph, user):
    """How many users are exactly 1, 2, 3 ... hops away."""
    _, dist, _ = bfs(graph, user)
    return dict(sorted(Counter(dist.values()).items()))
