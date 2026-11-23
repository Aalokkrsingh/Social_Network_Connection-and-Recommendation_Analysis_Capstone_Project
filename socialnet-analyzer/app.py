"""
Streamlit UI for SocialNet Analyzer.
Run:  streamlit run app.py
"""
import csv, io, os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import streamlit as st

from socialnet import analysis, benchmark, traversal
from socialnet.generators import random_network, scale_free_network
from socialnet.graph import Graph
from socialnet.io_utils import load_edge_list

SAMPLE = os.path.join(os.path.dirname(__file__), "data", "sample_network.csv")
st.set_page_config(page_title="SocialNet Analyzer", layout="wide")


# ---------------- data loading ----------------
@st.cache_resource
def load_sample():
    return load_edge_list(SAMPLE)


@st.cache_resource
def make_generated(kind, n, seed):
    return random_network(n, 6, seed) if kind == "Random" else scale_free_network(n, 3, seed)


def parse_upload(file):
    g = Graph()
    text = file.getvalue().decode("utf-8")
    for row in csv.reader(io.StringIO(text)):
        if len(row) >= 2 and row[0].strip().lower() != "user_a":
            g.add_connection(row[0].strip(), row[1].strip())
    return g


# ---------------- drawing ----------------
def draw(g, path=None, highlight=None, start=None):
    G = nx.Graph()
    G.add_nodes_from(g.users())
    for u, friends in g.adj.items():
        for v in friends:
            G.add_edge(u, v)
    pos = nx.spring_layout(G, seed=7, k=0.9 / max(len(G) ** 0.5, 1))
    palette = plt.get_cmap("tab20")
    color = {}
    for i, comp in enumerate(analysis.connected_components(g)):
        for u in comp:
            color[u] = palette(i % 20)
    node_colors = [color[u] for u in G]
    sizes = [260] * len(G)
    fig, ax = plt.subplots(figsize=(9, 6))
    nx.draw_networkx_edges(G, pos, ax=ax, alpha=0.35, width=1)
    if path:
        pe = list(zip(path, path[1:]))
        nx.draw_networkx_edges(G, pos, edgelist=pe, ax=ax, edge_color="red", width=3.5)
    if highlight:
        node_colors = ["#ff9f1c" if u in highlight else c for u, c in zip(G, node_colors)]
    if path:
        node_colors = ["#e63946" if u in path else c for u, c in zip(G, node_colors)]
    if start is not None:
        node_colors = ["#d00000" if u == start else c for u, c in zip(G, node_colors)]
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=sizes, ax=ax,
                           edgecolors="white", linewidths=1)
    if len(G) <= 60:
        nx.draw_networkx_labels(G, pos, font_size=8, ax=ax)
    ax.axis("off")
    fig.tight_layout()
    return fig


# ---------------- sidebar ----------------
st.title("SocialNet Analyzer")
st.caption("Social network analysis with BFS, DFS, mutual connections, shortest paths and recommendations")

with st.sidebar:
    st.header("Network")
    source = st.radio("Data source", ["Sample network", "Upload CSV", "Generate"])
    if source == "Sample network":
        g = load_sample()
    elif source == "Upload CSV":
        up = st.file_uploader("CSV with columns user_a,user_b", type="csv")
        g = parse_upload(up) if up else load_sample()
        if not up:
            st.info("No file yet, showing the sample network.")
    else:
        kind = st.selectbox("Type", ["Scale-free", "Random"])
        n = st.slider("Users", 20, 300, 60, step=10)
        seed = st.number_input("Seed", 0, 999, 42)
        g = make_generated(kind, n, seed)
    st.metric("Users", g.num_users)
    st.metric("Connections", g.num_connections)

users = sorted(g.users(), key=str)
tabs = st.tabs(["Network", "Explore (BFS / DFS)", "Mutual & Path", "Recommend", "Statistics", "Benchmark"])

# ---------------- tab 1: network ----------------
with tabs[0]:
    st.pyplot(draw(g))
    st.caption("Each colour is one community (connected component). Users in different colours cannot reach each other.")

# ---------------- tab 2: explore ----------------
with tabs[1]:
    c1, c2, c3 = st.columns(3)
    start = c1.selectbox("Start user", users, key="start")
    algo = c2.radio("Algorithm", ["BFS", "DFS"], horizontal=True)
    depth = c3.slider("Max depth (BFS only, 0 = unlimited)", 0, 10, 0)
    if algo == "BFS":
        order, dist, _ = traversal.bfs(g, start, max_depth=depth or None)
        df = pd.DataFrame({"Step": range(1, len(order) + 1), "User": order,
                           "Hops from start": [dist[u] for u in order]})
        st.write("BFS visits users **level by level** (queue).")
    else:
        order = traversal.dfs_iterative(g, start)
        df = pd.DataFrame({"Step": range(1, len(order) + 1), "User": order})
        st.write("DFS follows **one branch as deep as possible** before backtracking (stack).")
    left, right = st.columns([3, 2])
    left.pyplot(draw(g, highlight=set(order), start=start))
    right.dataframe(df, hide_index=True, height=420)
    st.caption(f"Reached {len(order)} of {g.num_users} users. Orange = visited, dark red = start.")

# ---------------- tab 3: mutual & path ----------------
with tabs[2]:
    c1, c2 = st.columns(2)
    a = c1.selectbox("User A", users, key="a")
    b = c2.selectbox("User B", users, index=min(1, len(users) - 1), key="b")
    mutual = analysis.mutual_connections(g, a, b)
    st.subheader("Mutual connections")
    st.write(", ".join(sorted(map(str, mutual))) if mutual else "No mutual connections.")
    st.subheader("Connection path")
    sp = analysis.shortest_path(g, a, b)
    if sp is None:
        st.warning("These users are not connected (different communities).")
        st.pyplot(draw(g))
    else:
        dp = traversal.dfs_path(g, a, b)
        bp = analysis.bidirectional_shortest_path(g, a, b)
        m1, m2, m3 = st.columns(3)
        m1.metric("BFS shortest path", f"{len(sp) - 1} hops")
        m2.metric("Bidirectional BFS", f"{len(bp) - 1} hops")
        m3.metric("DFS path", f"{len(dp) - 1} hops")
        st.success(" → ".join(map(str, sp)))
        if len(dp) > len(sp):
            st.caption("DFS found a valid but longer path. This is why BFS is used for shortest paths.")
        st.pyplot(draw(g, path=sp))

# ---------------- tab 4: recommend ----------------
with tabs[3]:
    u = st.selectbox("Recommend friends for", users, key="rec")
    k = st.slider("How many suggestions", 1, 15, 5)
    recs = analysis.recommend_friends(g, u, k)
    if recs:
        st.dataframe(pd.DataFrame({
            "Suggested user": [r for r, _ in recs],
            "Mutual friends": [c for _, c in recs],
            "Through": [", ".join(sorted(map(str, analysis.mutual_connections(g, u, r)))) for r, _ in recs],
        }), hide_index=True)
        st.caption("Ranked by number of mutual friends (friends-of-friends who are not yet friends).")
    else:
        st.info("No suggestions: this user has no friends-of-friends outside their circle.")

# ---------------- tab 5: stats ----------------
with tabs[4]:
    s = analysis.degree_stats(g)
    comps = analysis.connected_components(g)
    r1 = st.columns(4)
    r1[0].metric("Average degree", s["average_degree"])
    r1[1].metric("Density", s["density"])
    r1[2].metric("Communities", len(comps))
    r1[3].metric("Most connected", f"{s['most_connected']} ({s['max_degree']})")
    r2 = st.columns(2)
    r2[0].metric("Average clustering", round(analysis.average_clustering(g), 3))
    r2[1].metric("Avg path length (hops)", round(analysis.average_path_length(g), 2))
    st.subheader("Degree distribution")
    degs = pd.Series([g.degree(x) for x in g.users()]).value_counts().sort_index()
    st.bar_chart(degs, x_label="Number of friends", y_label="Number of users")
    st.subheader("Communities")
    st.dataframe(pd.DataFrame({"Size": [len(c) for c in comps],
                               "Members": [", ".join(map(str, c[:12])) + (" ..." if len(c) > 12 else "") for c in comps]}),
                 hide_index=True)

# ---------------- tab 6: benchmark ----------------
with tabs[5]:
    st.write("Measures how running time grows with network size (best of 5 runs, so large sizes take a while).")
    c1, c2 = st.columns(2)
    kind_b = c1.selectbox("Network type", ["random", "scale_free"])
    sizes = c2.multiselect("Sizes", [1000, 2000, 5000, 10000, 20000, 50000],
                           default=[1000, 2000, 5000, 10000])
    if st.button("Run benchmark") and sizes:
        with st.spinner("Running..."):
            rows = benchmark.run(kind_b, sorted(sizes), verbose=False)
        df = pd.DataFrame(rows).set_index("users")
        st.dataframe(df)
        st.subheader("Traversal time (ms)")
        st.line_chart(df[["bfs_ms", "dfs_ms"]])
        st.subheader("20 shortest-path queries (ms)")
        st.line_chart(df[["path_bfs_ms", "path_bidir_ms"]])
        st.subheader("Average path length found (hops)")
        st.line_chart(df[["avg_hops_bfs", "avg_hops_dfs"]])
