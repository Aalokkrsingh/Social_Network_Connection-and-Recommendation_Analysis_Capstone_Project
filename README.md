# SocialNet Analyzer

**Social Network Connection and Recommendation Analysis**

A social network analysis system in which users are vertices and friendships are edges. It implements
BFS and DFS to explore connections, finds mutual connections, computes the shortest connection path,
recommends new friends, and measures how the algorithms perform on networks of up to 100,000 users.
Includes a command-line interface and a Streamlit web UI.

## Features

- Graph stored as an adjacency list (dictionary of sets)
- Breadth-First Search (queue) and Depth-First Search (iterative and recursive)
- Mutual connections between two users (set intersection)
- Shortest connection path (BFS with parent tracking) and a faster bidirectional BFS
- Connected components (communities)
- "People you may know" recommendations ranked by mutual friends
- Network statistics: average degree, density, clustering coefficient, average path length
- Random and scale-free network generators, CSV import and export
- Benchmark of traversal and path-finding time versus network size
- 11 automated unit tests

## Screenshots

| Network view | BFS explorer |
|---|---|
| ![Network](screenshots/network.png) | ![Explore](screenshots/explore.png) |
| **Mutual connections and path** | **Recommendations** |
| ![Path](screenshots/path.png) | ![Recommend](screenshots/recommend.png) |

## Installation

Requires Python 3.9 or newer.

```bash
python -m venv .venv
# Windows:      .venv\Scripts\activate
# Mac / Linux:  source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

### Web UI
```bash
streamlit run app.py
```
Opens at http://localhost:8501 with tabs for Network, Explore (BFS / DFS), Mutual and Path,
Recommend, Statistics and Benchmark. The data source can be the sample network, your own CSV, or a
generated network.

### Command line
```bash
python main.py info                  # network statistics
python main.py bfs Aalok             # users by hops from Aalok
python main.py dfs Aalok             # DFS visit order
python main.py mutual Aalok Riya     # mutual connections
python main.py path Aalok Zoya       # shortest path (also shows the DFS path for comparison)
python main.py recommend Aalok       # friend suggestions
python main.py benchmark             # performance experiments, saved to results/
```
Use your own data with `--data edges.csv` (two columns: `user_a,user_b`).

### Tests
```bash
python -m pytest -q
```

## Project structure

```
main.py                  command-line interface
app.py                   Streamlit web UI
socialnet/graph.py       Graph class (adjacency list)
socialnet/traversal.py   BFS, DFS (iterative and recursive), DFS path
socialnet/analysis.py    mutual connections, shortest path, bidirectional BFS, components,
                         recommendations, network statistics
socialnet/generators.py  random and scale-free network generators
socialnet/io_utils.py    CSV edge-list load and save
socialnet/benchmark.py   timing experiments and charts
data/sample_network.csv  20-user demo network (3 communities and 1 isolated pair)
tests/                   pytest unit tests
results/                 benchmark.csv and benchmark.png
screenshots/             UI screenshots
```

## Algorithms and complexity

| Task | Technique | Time complexity |
|---|---|---|
| Explore network | BFS (queue) | O(V + E) |
| Explore deeply | DFS (stack) | O(V + E) |
| Mutual connections | Set intersection | O(min(deg a, deg b)) |
| Shortest path | BFS with parent map | O(V + E) |
| Faster shortest path | Bidirectional BFS | about O(b^(d/2)) |
| Communities | Connected components (BFS) | O(V + E) |
| Recommendations | Friends-of-friends counting | O(sum of friends' degrees) |

**Why an adjacency list of sets?** Social networks are sparse, so an adjacency list needs O(V + E) memory
while a matrix needs O(V^2). Sets give O(1) friendship lookup, no duplicates, and built-in intersection.

**Why BFS for shortest paths?** BFS visits users in order of distance, so the first time it reaches the
target it has used the fewest possible hops. DFS only finds some path, often a very long one.

## Results

Synthetic random network, average 10 friends per user, best of 5 runs (times in milliseconds):

| Users | BFS | DFS | 20 path queries (BFS) | 20 path queries (bidirectional) | Avg hops BFS | Avg hops DFS |
|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | 0.65 | 0.77 | 1.97 | 0.23 | 3.40 | 74.4 |
| 10,000 | 11.01 | 12.57 | 29.98 | 0.71 | 4.45 | 761.5 |
| 100,000 | 341.03 | 330.37 | 781.35 | 2.84 | 5.25 | 8,546.0 |

![Benchmark](results/benchmark.png)

Findings:

1. BFS and DFS both scale linearly with network size and take about the same time.
2. Only BFS returns shortest paths: about 5 hops on 100,000 users, versus thousands of hops for DFS.
3. Bidirectional BFS answers path queries roughly 275 times faster than standard BFS at 100,000 users.

Timings depend on the machine; run `python main.py benchmark` to reproduce them.

## Limitations and future work

- Experiments use synthetic data; a real dataset (for example Stanford SNAP) would be a good next step.
- Connections are unweighted and undirected.
- Recommendations use only mutual-friend counts; Jaccard similarity or Adamic-Adar would improve them.
- The full graph is held in memory.

## Author

Aalok Kumar Singh, BCA (AI & Data Science), K.R. Mangalam University
