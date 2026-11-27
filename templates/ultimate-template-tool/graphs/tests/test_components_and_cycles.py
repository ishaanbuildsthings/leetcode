"""Tests graphs/undirectedComponents.*, hasCycleUndirected.* and hasCycleDirected.* on random graphs (isolated nodes,
repeated edges, self-loops, forests, dense graphs), 0- and 1-indexed:
  - components against a plain breadth-first search
  - the undirected check against counting: a graph has a loop exactly when it has more edges than nodes - components
  - the directed check against "can some node get back to itself" by a search from each node
The C++ files, built with sanitizers, must print exactly what Python does.

    python3 test_components_and_cycles.py
"""
import os
import random
import subprocess
import sys
import tempfile
from collections import deque

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)


def load(name):
    ns = {}
    exec(open(os.path.join(SRC, name + ".py")).read(), ns)
    return ns[name]


undirectedComponents = load("undirectedComponents")
hasCycleUndirected = load("hasCycleUndirected")
hasCycleDirected = load("hasCycleDirected")


def bruteComponents(edges, numNodes, first):
    adj = {node: [] for node in range(first, first + numNodes)}
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    seen, comps = set(), []
    for start in range(first, first + numNodes):
        if start in seen:
            continue
        seen.add(start)
        group, queue = [], deque([start])
        while queue:
            node = queue.popleft()
            group.append(node)
            for nxt in adj[node]:
                if nxt not in seen:
                    seen.add(nxt)
                    queue.append(nxt)
        group.sort()
        members = set(group)
        comps.append((group, [[a, b] for a, b in edges if a in members]))
    return comps


def bruteUndirectedCycle(edges):
    if not edges:
        return False
    size = max(max(a, b) for a, b in edges) + 1
    return len(edges) > size - len(bruteComponents(edges, size, 0))


def bruteDirectedCycle(edges):
    adj = {}
    for a, b in edges:
        adj.setdefault(a, []).append(b)
    for start in adj:
        seen, stack = set(), list(adj[start])
        while stack:
            node = stack.pop()
            if node == start:
                return True
            if node not in seen:
                seen.add(node)
                stack.extend(adj.get(node, []))
    return False


def randomEdges(rnd, numNodes, first):
    kind = rnd.randrange(3)
    lab = lambda: rnd.randint(first, first + numNodes - 1)
    if kind == 0:  # anything
        return [(lab(), lab()) for _ in range(rnd.randint(0, 2 * numNodes))]
    if kind == 1:  # a forest: no undirected cycle unless we add one
        edges = [(first + i, first + rnd.randrange(i)) for i in range(1, numNodes) if rnd.random() < 0.8]
        if rnd.random() < 0.3 and numNodes > 1:
            edges.append((lab(), lab()))
        rnd.shuffle(edges)
        return edges
    # edges only from smaller to bigger label: no directed cycle unless we add one
    edges = []
    for _ in range(rnd.randint(0, 2 * numNodes)):
        a, b = sorted((lab(), lab()))
        if a != b:
            edges.append((a, b))
    if rnd.random() < 0.3 and edges:
        a, b = rnd.choice(edges)
        edges.append((b, a))
    rnd.shuffle(edges)
    return edges


def main():
    for name, f in (("undirectedComponents", undirectedComponents), ("hasCycleUndirected", hasCycleUndirected),
                    ("hasCycleDirected", hasCycleDirected)):
        for bad in ([(-1, 0)],) if name != "undirectedComponents" else ():
            try:
                f(bad)
            except ValueError:
                pass
            else:
                sys.exit(f"FAIL {name}: negative label should raise")
    for args in (([(1, 4)], 3, True), ([(0, 3)], 3, False), ([(0, 1)], 3, True)):
        try:
            undirectedComponents(*args)
        except ValueError:
            pass
        else:
            sys.exit(f"FAIL undirectedComponents{args}: should raise")
    assert hasCycleUndirected([]) is False and hasCycleDirected([]) is False
    assert hasCycleUndirected([(3, 3)]) is True and hasCycleDirected([(3, 3)]) is True
    assert undirectedComponents([], 0, False) == [] and undirectedComponents([], 2, True) == [([1], []), ([2], [])]

    rnd = random.Random(5)
    cases, outs = [], []
    counts = {True: 0, False: 0}
    for _ in range(3000):
        first = rnd.randint(0, 1)
        numNodes = rnd.randint(1, 10)
        edges = randomEdges(rnd, numNodes, first)
        comps = undirectedComponents(edges, numNodes, first == 1)
        assert [(list(n), [list(e) for e in es]) for n, es in comps] == bruteComponents(edges, numNodes, first), (edges, comps)
        u = hasCycleUndirected(edges)
        d = hasCycleDirected(edges)
        assert u == bruteUndirectedCycle(edges), edges
        assert d == bruteDirectedCycle(edges), edges
        counts[u] += 1
        counts[d] += 1
        cases.append((first, numNodes, edges))
        outs.append(" | ".join(",".join(map(str, n)) + ":" + ";".join(f"{a},{b}" for a, b in es) for n, es in comps))
        outs.append(f"{int(u)} {int(d)}")
    assert min(counts.values()) > 1000, counts  # plenty of both answers
    print(f"python: {len(cases)} graphs match the brute force ({counts[True]} cycle answers true, {counts[False]} false)")

    src = "\n".join(open(os.path.join(SRC, f + ".cpp")).read().split("using namespace std;", 1)[1]
                    for f in ("undirectedComponents", "hasCycleUndirected", "hasCycleDirected"))
    src = "#include <bits/stdc++.h>\nusing namespace std;\n" + src + '''
int main() {
    int t; cin >> t;
    while (t--) {
        int first, numNodes, m; cin >> first >> numNodes >> m;
        vector<pair<int, int>> edges(m);
        for (auto& [a, b] : edges) cin >> a >> b;
        auto comps = undirectedComponents(edges, numNodes, first == 1);
        for (int i = 0; i < (int)comps.size(); i++) {
            if (i) cout << " | ";
            for (int j = 0; j < (int)comps[i].nodes.size(); j++) cout << (j ? "," : "") << comps[i].nodes[j];
            cout << ":";
            for (int j = 0; j < (int)comps[i].edges.size(); j++)
                cout << (j ? ";" : "") << comps[i].edges[j].first << "," << comps[i].edges[j].second;
        }
        cout << "\\n" << hasCycleUndirected(edges) << " " << hasCycleDirected(edges) << "\\n";
    }
    bool threw = false;
    try { undirectedComponents({{1, 4}}, 3, true); } catch (const out_of_range&) { threw = true; }
    if (!threw) { cout << "no throw\\n"; return 1; }
}
'''
    with tempfile.TemporaryDirectory() as tmp:
        exe = os.path.join(tmp, "cc")
        open(exe + ".cpp", "w").write(src)
        r = subprocess.run(["g++", "-std=c++17", "-Wall", "-fsanitize=address,undefined", "-o", exe, exe + ".cpp"],
                           capture_output=True, text=True)
        if r.returncode:
            sys.exit("FAIL cpp compile\n" + r.stderr[:2000])
        inp = f"{len(cases)}\n" + "".join(f"{fi} {n} {len(e)}\n" + "".join(f"{a} {b}\n" for a, b in e) for fi, n, e in cases)
        r = subprocess.run([exe], input=inp, capture_output=True, text=True)
        got = r.stdout.splitlines()
        if r.returncode or got != outs:
            k = next((k for k in range(len(outs)) if k >= len(got) or got[k] != outs[k]), len(outs))
            sys.exit(f"FAIL cpp line {k}: {got[k] if k < len(got) else r.stdout[-300:] + r.stderr[-800:]}\n  python: {outs[k]}")
    print("cpp: prints exactly what python does")


if __name__ == "__main__":
    main()
