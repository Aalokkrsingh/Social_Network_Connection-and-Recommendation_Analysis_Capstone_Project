"""
traversal.py - BFS and DFS.

Both visit every reachable user exactly once and look at every connection
twice, so both run in O(V + E) time and use O(V) extra memory.
The ONLY real difference is the container that holds "users still to visit":
    BFS -> queue (first in, first out)  -> explores level by level
    DFS -> stack (last in, first out)   -> explores one branch to the end
"""
from collections import deque


def bfs(graph, start, max_depth=None):
    """
    Breadth-First Search.
    Returns (order, dist, parent)
        order  : users in the order they were visited
        dist   : dist[u] = number of hops from `start` to u
        parent : parent[u] = the user who discovered u (used to rebuild paths)
    max_depth lets you stop early, e.g. max_depth=2 -> friends and friends-of-friends.
    """
    dist = {start: 0}
    parent = {start: None}
    order = []
    queue = deque([start])
    while queue:
        u = queue.popleft()                    # take the OLDEST waiting user
        order.append(u)
        if max_depth is not None and dist[u] == max_depth:
            continue
        for v in graph.neighbors(u):
            if v not in dist:                  # not discovered yet
                dist[v] = dist[u] + 1
                parent[v] = u
                queue.append(v)                # go to the back of the line
    return order, dist, parent


def dfs_iterative(graph, start):
    """Depth-First Search with an explicit stack. Returns visit order."""
    visited = set()
    order = []
    stack = [start]
    while stack:
        u = stack.pop()                        # take the NEWEST waiting user
        if u in visited:
            continue
        visited.add(u)
        order.append(u)
        for v in graph.neighbors(u):
            if v not in visited:
                stack.append(v)
    return order


def dfs_recursive(graph, start, visited=None, order=None):
    """Same as above but using the call stack. Fails on very deep graphs
    because Python limits recursion depth (about 1000 by default)."""
    if visited is None:
        visited, order = set(), []
    visited.add(start)
    order.append(start)
    for v in graph.neighbors(start):
        if v not in visited:
            dfs_recursive(graph, v, visited, order)
    return order


def dfs_path(graph, source, target):
    """A path found by DFS. It IS a valid path but usually NOT the shortest -
    this function exists to demonstrate why BFS is used for shortest paths."""
    parent = {source: None}
    stack = [source]
    while stack:
        u = stack.pop()
        if u == target:
            path = []
            while u is not None:
                path.append(u)
                u = parent[u]
            return path[::-1]
        for v in graph.neighbors(u):
            if v not in parent:
                parent[v] = u
                stack.append(v)
    return None
