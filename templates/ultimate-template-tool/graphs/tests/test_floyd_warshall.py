"""Tests graphs/floydWarshall{Directed,Undirected}{,.oneIndexed}.*: random weighted graphs (isolated nodes, repeated
edges, self-loops, zero weights) are checked against relaxing every edge numNodes times from every source; the
documented examples must hold, negative weights and out-of-range labels must raise, and the unused row / column of
the 1-indexed versions must stay INF. The C++ files, built with sanitizers, must print what Python does.

    python3 test_floyd_warshall.py
"""
import os
import random
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
INF = float("inf")


def brute(numNodes, edges, first, directed):
    size = first + numNodes
    arcs = list(edges) + ([] if directed else [(b, a, w) for a, b, w in edges])
    out = [[INF] * size for _ in range(size)]
    for src in range(first, size):
        dist = out[src]
        dist[src] = 0
        for _ in range(numNodes):
            for a, b, w in arcs:
                if dist[a] + w < dist[b]:
                    dist[b] = dist[a] + w
    return out


def load(file, fn):
    ns = {}
    exec(open(os.path.join(SRC, file + ".py")).read(), ns)
    return ns[fn]


def main():
    for kind in ("Directed", "Undirected"):
        directed = kind == "Directed"
        for first in (0, 1):
            fn = f"floydWarshall{kind}"
            file = fn + (".oneIndexed" if first else "")
            f = load(file, fn)

            # the header's example
            if first:
                dist = f(4, [(1, 2, 4), (1, 3, 1), (3, 2, 2)])
                assert dist[1] == [INF, 0, 3, 1, INF], (file, dist)
                assert dist[2] == ([INF, INF, 0, INF, INF] if directed else [INF, 3, 0, 2, INF]), (file, dist)
                assert dist[0] == [INF] * 5, (file, dist)
            else:
                dist = f(4, [(0, 1, 4), (0, 2, 1), (2, 1, 2)])
                assert dist[0] == [0, 3, 1, INF], (file, dist)
                assert dist[1] == ([INF, 0, INF, INF] if directed else [3, 0, 2, INF]), (file, dist)

            # errors
            for bad in ([(first, first + 1, -1)], [(first, first + 3, 1)], [(first - 1, first, 1)]):
                try:
                    f(3, bad)
                except ValueError:
                    pass
                else:
                    sys.exit(f"FAIL {file}: {bad} should raise")

            rnd = random.Random(7)
            cases, outs = [], []
            for _ in range(400):
                numNodes = rnd.randint(1, 9)
                lab = lambda: rnd.randint(first, first + numNodes - 1)
                edges = [(lab(), lab(), rnd.randint(0, 9)) for _ in range(rnd.randint(0, 3 * numNodes))]
                got = f(numNodes, edges)
                want = brute(numNodes, edges, first, directed)
                assert got == want, (file, numNodes, edges, got, want)
                assert len(got) == first + numNodes and all(len(r) == first + numNodes for r in got), file
                cases.append((numNodes, edges))
                outs.append(" ".join("x" if d == INF else str(d) for row in got for d in row))
            # floats work in Python too
            assert f(2, [(first, first + 1, 0.5)])[first][first + 1] == 0.5

            # C++: same cases, same output
            src = open(os.path.join(SRC, file + ".cpp")).read() + f'''
int main() {{
    int t; cin >> t;
    while (t--) {{
        int numNodes, m; cin >> numNodes >> m;
        vector<array<ll, 3>> edges(m);
        for (auto& e : edges) cin >> e[0] >> e[1] >> e[2];
        auto dist = {fn}(numNodes, edges);
        bool firstOut = true;
        for (auto& row : dist) for (ll d : row) {{
            if (!firstOut) cout << " ";
            firstOut = false;
            if (d == INF) cout << "x"; else cout << d;
        }}
        cout << "\\n";
    }}
    bool threw = false;
    try {{ {fn}(3, {{{{{first}, {first + 1}, -1}}}}); }} catch (const invalid_argument&) {{ threw = true; }}
    if (!threw) {{ cout << "no throw on negative\\n"; return 1; }}
    threw = false;
    try {{ {fn}(3, {{{{{first}, {first + 3}, 1}}}}); }} catch (const out_of_range&) {{ threw = true; }}
    if (!threw) {{ cout << "no throw on out of range\\n"; return 1; }}
}}
'''
            with tempfile.TemporaryDirectory() as tmp:
                exe = os.path.join(tmp, "fw")
                open(exe + ".cpp", "w").write(src)
                r = subprocess.run(["g++", "-std=c++17", "-Wall", "-fsanitize=address,undefined", "-o", exe, exe + ".cpp"],
                                   capture_output=True, text=True)
                if r.returncode:
                    sys.exit(f"FAIL cpp {file} compile\n" + r.stderr[:1500])
                inp = f"{len(cases)}\n" + "".join(
                    f"{n} {len(e)}\n" + "".join(f"{a} {b} {w}\n" for a, b, w in e) for n, e in cases)
                r = subprocess.run([exe], input=inp, capture_output=True, text=True)
                got = r.stdout.splitlines()
                if r.returncode or got != outs:
                    k = next((k for k in range(len(outs)) if k >= len(got) or got[k] != outs[k]), len(outs))
                    sys.exit(f"FAIL cpp {file} case {k}: {got[k] if k < len(got) else r.stdout[-300:] + r.stderr[-800:]}")
            print(f"{file}: python + cpp agree with the brute force")


if __name__ == "__main__":
    main()
