"""
graph.py - the data structure behind everything.

A social network is stored as an ADJACENCY LIST:
    { user : {set of that user's friends} }

Why a dict of sets?
  * dict  -> jump straight to a user in O(1)
  * set   -> "is X a friend of Y?" in O(1), no duplicate friends,
             and set intersection gives mutual friends cheaply.
Friendship is mutual, so the graph is UNDIRECTED: every edge is stored twice.
"""


class Graph:
    def __init__(self):
        self.adj = {}

    # ---- building ----
    def add_user(self, user):
        self.adj.setdefault(user, set())

    def add_connection(self, a, b):
        if a == b:                      # a user cannot befriend themselves
            return
        self.add_user(a)
        self.add_user(b)
        self.adj[a].add(b)              # a -> b
        self.adj[b].add(a)              # b -> a  (undirected)

    def remove_connection(self, a, b):
        if a in self.adj:
            self.adj[a].discard(b)
        if b in self.adj:
            self.adj[b].discard(a)

    # ---- querying ----
    def neighbors(self, user):
        return self.adj[user]

    def has_user(self, user):
        return user in self.adj

    def degree(self, user):
        return len(self.adj[user])

    def users(self):
        return list(self.adj)

    @property
    def num_users(self):
        return len(self.adj)

    @property
    def num_connections(self):
        # every edge is stored twice, so divide by 2
        return sum(len(f) for f in self.adj.values()) // 2

    def __repr__(self):
        return f"Graph(users={self.num_users}, connections={self.num_connections})"
