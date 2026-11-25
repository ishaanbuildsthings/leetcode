"""Tests graphs/topoSort.{py,cpp}: random directed graphs (0- and 1-indexed ranges, isolated nodes, repeats,
self-loops, some built acyclic on purpose) are checked against a brute force cycle check (can any node reach itself);
when acyclic, the order must hold every node once with a before b for every edge a -> b. The C++ file, built with
sanitizers, has to print exactly what Python does.

    python3 test_topo_sort.py
"""
import os
import random
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)


def hasCycle(adj):
    for s in adj:
        seen, st = set(), [s]
        while st:
            x = st.pop()
            for y in adj[x]:
                if y == s:
                    return True
                if y not in seen:
                    seen.add(y)
                    st.append(y)
    return False


def main():
    ns = {}
    exec(open(os.path.join(SRC, "topoSort.py")).read(), ns)
    topoSort = ns["topoSort"]
    assert topoSort([(1, 3), (2, 3)], 3, oneIndexed=True) == [1, 2, 3]
    assert topoSort([(0, 1)], 3, oneIndexed=False) == [0, 2, 1]
    assert topoSort([(1, 2), (2, 3), (3, 1)], 3, oneIndexed=True) is None
    assert topoSort([], 0, oneIndexed=False) == []
    rnd = random.Random(7)
    cases, outs = [], []
    for _ in range(600):
        first = rnd.choice([0, 1])
        n = rnd.randint(0, 12)
        last = first + n - 1
        edges = []
        if n:
            rank = list(range(first, last + 1))
            rnd.shuffle(rank)
            acyclic = rnd.random() < 0.5
            for _ in range(rnd.randint(0, 3 * n)):
                a, b = rnd.randint(first, last), rnd.randint(first, last)
                if acyclic:
                    if a == b:
                        continue
                    if rank.index(a) > rank.index(b):
                        a, b = b, a
                edges.append((a, b))
        order = topoSort(edges, n, first == 1)
        adj = {x: [] for x in range(first, last + 1)}
        for a, b in edges:
            adj[a].append(b)
        cyc = hasCycle(adj)
        assert (order is None) == cyc, (edges, first, last)
        if order is not None:
            assert sorted(order) == list(adj), (edges, order)
            pos = {x: k for k, x in enumerate(order)}
            assert all(pos[a] < pos[b] for a, b in edges), (edges, order)
        cases.append((edges, first, n))
        outs.append("cycle" if order is None else " ".join(map(str, order)))
    print(f"python: {len(cases)} graphs agree with brute force")
    src = open(os.path.join(SRC, "topoSort.cpp")).read() + r'''
int main() {
    int t; cin >> t;
    while (t--) {
        int m, n, oneIndexed; cin >> m >> n >> oneIndexed;
        vector<pair<int, int>> edges(m);
        for (auto& [a, b] : edges) cin >> a >> b;
        vector<int> order = topoSort(edges, n, oneIndexed);
        if ((int)order.size() != n) { cout << "cycle\n"; continue; }
        for (size_t i = 0; i < order.size(); i++) cout << (i ? " " : "") << order[i];
        cout << "\n";
    }
}
'''
    open("/tmp/topoSort.cpp", "w").write(src)
    r = subprocess.run(["g++", "-std=c++17", "-Wall", "-fsanitize=address,undefined", "-o", "/tmp/topoSort", "/tmp/topoSort.cpp"],
                       capture_output=True, text=True)
    if r.returncode or "warning" in r.stderr:
        sys.exit("FAIL cpp compile\n" + r.stderr[:1500])
    inp = f"{len(cases)}\n" + "".join(f"{len(e)} {n} {f}\n" + "".join(f"{a} {b}\n" for a, b in e) for e, f, n in cases)
    got = subprocess.run(["/tmp/topoSort"], input=inp, capture_output=True, text=True, timeout=60).stdout.split("\n")[:-1]
    if got != outs:
        k = next(k for k in range(len(outs)) if k >= len(got) or got[k] != outs[k])
        sys.exit(f"FAIL cpp case {k}: {got[k] if k < len(got) else 'nothing'} vs python {outs[k]}")
    print("cpp: prints exactly what python does")


if __name__ == "__main__":
    main()
