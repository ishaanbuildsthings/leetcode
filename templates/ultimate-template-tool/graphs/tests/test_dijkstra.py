"""Tests graphs/dijkstraDirected.* and dijkstraUndirected.*: random weighted graphs (0- and 1-indexed, isolated nodes,
repeated edges, self-loops, zero weights) are checked against relaxing every edge n times; prev must give a path whose
length is the distance, following it back must reach the source. The C++ files, built with sanitizers, must print what Python does.

    python3 test_dijkstra.py
"""
import os
import random
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)


def brute(edges, n, first, source, directed):
    size = first + n
    dist = [None] * size
    dist[source] = 0
    arcs = [(a, b, w) for a, b, w in edges] + ([] if directed else [(b, a, w) for a, b, w in edges])
    for _ in range(n):
        for a, b, w in arcs:
            if dist[a] is not None and (dist[b] is None or dist[a] + w < dist[b]):
                dist[b] = dist[a] + w
    return dist


def main():
    for kind in ("Directed", "Undirected"):
        ns = {}
        exec(open(os.path.join(SRC, f"dijkstra{kind}.py")).read(), ns)
        fn = ns[f"dijkstra{kind}"]
        dist, prev = fn([(1, 2, 4), (1, 3, 1), (3, 2, 2), (2, 4, 5)], 4, oneIndexed=True, source=1)
        assert (dist, prev) == ([None, 0, 3, 1, 8], [None, None, 3, 1, 2]), (kind, dist, prev)
        rnd = random.Random(11)
        cases, outs = [], []
        for _ in range(400):
            first = rnd.choice([0, 1])
            n = rnd.randint(1, 10)
            edges = [(rnd.randint(first, first + n - 1), rnd.randint(first, first + n - 1), rnd.randint(0, 9)) for _ in range(rnd.randint(0, 3 * n))]
            source = rnd.randint(first, first + n - 1)
            dist, prev = fn(edges, n, first == 1, source)
            assert dist == brute(edges, n, first, source, kind == "Directed"), (kind, edges, n, first, source)
            arcs = set(edges) | (set() if kind == "Directed" else {(b, a, w) for a, b, w in edges})
            for t in range(first, first + n):
                if dist[t] is None:
                    assert prev[t] is None
                    continue
                path = [t]  # walk prev back to the source
                while path[-1] != source:
                    path.append(prev[path[-1]])
                    assert len(path) <= n, "prev loops"
                path.reverse()
                total = 0
                for x, y in zip(path, path[1:]):
                    total += min(w for a, b, w in arcs if a == x and b == y)
                assert total == dist[t], (kind, edges, source, t, path)
            cases.append((edges, n, first, source))
            outs.append(" ".join(map(str, (-1 if d is None else d for d in dist))) + "|" + " ".join(map(str, (-1 if p is None else p for p in prev))))
        src = open(os.path.join(SRC, f"dijkstra{kind}.cpp")).read() + f'''
int main() {{
    int t; cin >> t;
    while (t--) {{
        int m, n, oneIndexed, source; cin >> m >> n >> oneIndexed >> source;
        vector<array<ll, 3>> edges(m);
        for (auto& e : edges) cin >> e[0] >> e[1] >> e[2];
        auto [dist, prev] = dijkstra{kind}(edges, n, oneIndexed, source);
        for (size_t i = 0; i < dist.size(); i++) cout << (i ? " " : "") << dist[i];
        cout << "|";
        for (size_t i = 0; i < prev.size(); i++) cout << (i ? " " : "") << prev[i];
        cout << "\\n";
    }}
}}
'''
        exe = f"/tmp/dijkstra{kind}"
        open(exe + ".cpp", "w").write(src)
        r = subprocess.run(["g++", "-std=c++17", "-Wall", "-fsanitize=address,undefined", "-o", exe, exe + ".cpp"], capture_output=True, text=True)
        if r.returncode or "warning" in r.stderr:
            sys.exit(f"FAIL cpp {kind} compile\n" + r.stderr[:1500])
        inp = f"{len(cases)}\n" + "".join(f"{len(e)} {n} {f} {s}\n" + "".join(f"{a} {b} {w}\n" for a, b, w in e) for e, n, f, s in cases)
        got = subprocess.run([exe], input=inp, capture_output=True, text=True, timeout=60).stdout.split("\n")[:-1]
        # (prev can legitimately differ between equally short paths, so C++ is held to the same distances, and its prev
        # to the same choices only because both pop the heap in the same order)
        if got != outs:
            k = next(k for k in range(len(outs)) if k >= len(got) or got[k] != outs[k])
            sys.exit(f"FAIL cpp {kind} case {k}: {got[k] if k < len(got) else 'nothing'} vs python {outs[k]}")
        print(f"{kind}: 400 graphs agree with brute force; paths check out; C++ prints what Python does")


if __name__ == "__main__":
    main()
