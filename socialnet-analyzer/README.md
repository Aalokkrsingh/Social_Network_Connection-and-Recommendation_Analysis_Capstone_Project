# SocialNet Analyzer

Social network analysis using graph algorithms. Users are vertices, friendships are edges.
Implements BFS, DFS, mutual connections, shortest connection path, friend recommendation, network
statistics, and a performance study on networks of up to 100,000 users.

## Quick start
```bash
pip install -r requirements.txt
python main.py info                      # network statistics
python main.py bfs Aalok                 # who is how many hops away
python main.py dfs Aalok                 # depth-first visit order
python main.py mutual Aalok Riya         # mutual connections
python main.py path Aalok Zoya           # shortest path (+ what DFS would give)
python main.py recommend Aalok           # people you may know
python main.py benchmark                 # performance experiments -> results/
python -m pytest -q                      # 11 unit tests
```
Use your own data with `--data edges.csv` (two columns: `user_a,user_b`).

## Structure
```
main.py                 command-line interface
socialnet/graph.py      Graph class (adjacency list: dict of sets)
socialnet/traversal.py  BFS, DFS (iterative + recursive), DFS path
socialnet/analysis.py   mutual, shortest path, bidirectional BFS, components,
                        recommendations, degree/density/clustering/path-length stats
socialnet/generators.py random and scale-free (preferential attachment) networks
socialnet/io_utils.py   CSV edge-list load/save
socialnet/benchmark.py  timing experiments and charts
data/sample_network.csv 20-user demo network (3 communities + 1 isolated pair)
tests/                  pytest suite
results/                benchmark.csv, benchmark.png
```

## Algorithms and complexity
| Task | Technique | Time |
|---|---|---|
| Explore network | BFS (queue) | O(V + E) |
| Explore deeply | DFS (stack) | O(V + E) |
| Mutual connections | set intersection | O(min(deg a, deg b)) |
| Shortest path | BFS + parent map | O(V + E) |
| Faster shortest path | bidirectional BFS | about O(b^(d/2)) |
| Communities | connected components | O(V + E) |
| Recommendations | friends-of-friends counting | O(sum of friends' degrees) |

## Key results (100,000 users, ~500,000 connections)
| Network | BFS | DFS | 20 path queries (BFS) | 20 path queries (bidirectional) | Avg hops BFS | Avg hops DFS |
|---|---:|---:|---:|---:|---:|---:|
| Random | 341 ms | 330 ms | 781 ms | 2.8 ms | 5.25 | 8,546 |
| Scale-free | 172 ms | 178 ms | 376 ms | 1.2 ms | 4.20 | 6,807 |

BFS and DFS cost the same, but only BFS returns shortest paths. A DFS path on a large network can be
thousands of hops long. See the accompanying report for full analysis. Timings vary by machine.
