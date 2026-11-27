"""Tests graphs/bridges.*, articulationPoints.* and bipartiteSplit.* on random undirected graphs (repeated edges,
self-loops, trees, cycles, disconnected pieces), against brute force:
  - an edge is a bridge exactly when its two ends are no longer connected after removing just that edge
  - a node is an articulation point exactly when, after removing it, its neighbors no longer all connect
  - a split exists exactly when some 2-coloring of the nodes (tried in every way) has no edge inside a side; the
    returned split must be such a coloring, with each component's smallest node on side1
The C++ files, built with sanitizers, must print exactly what Python does.

    python3 test_cuts_and_bipartite.py
"""
import itertools
import os
import random
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)


def load(name):
    ns = {}
    exec(open(os.path.join(SRC, name + ".py")).read(), ns)
    return ns[name]


bridges = load("bridges")
articulationPoints = load("articulationPoints")
bipartiteSplit = load("bipartiteSplit")


def connected(edges, a, b, skipNode=None):
    adj = {}
    for x, y in edges:
        if skipNode in (x, y):
            continue
        adj.setdefault(x, []).append(y)
        adj.setdefault(y, []).append(x)
    seen, stack = {a}, [a]
    while stack:
        node = stack.pop()
        if node == b:
            return True
        for nxt in adj.get(node, []):
            if nxt not in seen:
                seen.add(nxt)
                stack.append(nxt)
    return False


def randomEdges(rnd, size):
    kind = rnd.randrange(3)
    if kind == 0:
        return [(rnd.randrange(size), rnd.randrange(size)) for _ in range(rnd.randint(0, 2 * size))]
    if kind == 1:  # a tree plus a few extra edges
        edges = [(i, rnd.randrange(i)) for i in range(1, size)]
        edges += [(rnd.randrange(size), rnd.randrange(size)) for _ in range(rnd.randint(0, 2))]
    else:  # cycles chained together
        edges, node = [], 0
        while node + 2 < size:
            length = rnd.randint(2, min(5, size - node))
            for i in range(length):
                edges.append((node + i, node + (i + 1) % length))
            node += length - 1
    rnd.shuffle(edges)
    return [(b, a) if rnd.random() < 0.5 else (a, b) for a, b in edges]


def main():
    for f in (bridges, articulationPoints):
        try:
            f([(-1, 0)])
        except ValueError:
            pass
        else:
            sys.exit("FAIL: negative label should raise")
    try:
        bipartiteSplit([(1, 4)], 3, True)
    except ValueError:
        pass
    else:
        sys.exit("FAIL: bipartiteSplit out of range should raise")
    assert bridges([]) == [] and articulationPoints([]) == [] and bipartiteSplit([], 2, True) == ([1, 2], [])
    assert bipartiteSplit([(2, 2)], 2, True) is None

    rnd = random.Random(13)
    cases, outs = [], []
    stats = [0, 0]
    for _ in range(2500):
        size = rnd.randint(1, 9)
        edges = randomEdges(rnd, size)
        realSize = max([max(a, b) + 1 for a, b in edges], default=0)
        # bridges
        want = [list(e) for i, e in enumerate(edges) if e[0] != e[1] and not connected(edges[:i] + edges[i + 1:], e[0], e[1])]
        assert bridges(edges) == want, (edges, bridges(edges), want)
        # articulation points
        want = []
        for node in range(realSize):
            nbrs = sorted({y for x, y in edges if x == node and y != node} | {x for x, y in edges if y == node and x != node})
            if any(not connected(edges, nbrs[0], other, skipNode=node) for other in nbrs[1:]):
                want.append(node)
        assert articulationPoints(edges) == want, (edges, articulationPoints(edges), want)
        # bipartite (0-indexed and 1-indexed)
        first = rnd.randint(0, 1)
        shifted = [(a + first, b + first) for a, b in edges]
        numNodes = size
        split = bipartiteSplit(shifted, numNodes, first == 1)
        nodes = list(range(first, first + numNodes))
        possible = any(all(c[a - first] != c[b - first] for a, b in shifted) for c in itertools.product((0, 1), repeat=numNodes))
        assert (split is not None) == possible, (shifted, split)
        stats[possible] += 1
        if split:
            s1, s2 = split
            assert sorted(s1 + s2) == nodes and s1 == sorted(s1) and s2 == sorted(s2)
            side = {x: 0 for x in s1} | {x: 1 for x in s2}
            assert all(side[a] != side[b] for a, b in shifted)
            for start in nodes:  # each component's smallest node on side1
                if all(not connected(shifted, start, smaller) for smaller in range(first, start)):
                    assert side[start] == 0, (shifted, split, start)
        cases.append((edges, first, numNodes, shifted))
        outs.append(" ".join(f"{a},{b}" for a, b in bridges(edges)))
        outs.append(" ".join(map(str, articulationPoints(edges))))
        outs.append("x" if split is None else ",".join(map(str, split[0])) + "|" + ",".join(map(str, split[1])))
    assert min(stats) > 500, stats
    print(f"python: {len(cases)} graphs match the brute force ({stats[1]} bipartite, {stats[0]} not)")

    src = "\n".join(open(os.path.join(SRC, f + ".cpp")).read().split("using namespace std;", 1)[1]
                    for f in ("bridges", "articulationPoints", "bipartiteSplit"))
    src = "#include <bits/stdc++.h>\nusing namespace std;\n" + src + '''
int main() {
    int t; cin >> t;
    while (t--) {
        int m, first, numNodes; cin >> m >> first >> numNodes;
        vector<pair<int, int>> edges(m), shifted(m);
        for (auto& [a, b] : edges) cin >> a >> b;
        for (auto& [a, b] : shifted) cin >> a >> b;
        auto br = bridges(edges);
        for (int i = 0; i < (int)br.size(); i++) cout << (i ? " " : "") << br[i].first << "," << br[i].second;
        cout << "\\n";
        auto ap = articulationPoints(edges);
        for (int i = 0; i < (int)ap.size(); i++) cout << (i ? " " : "") << ap[i];
        cout << "\\n";
        auto split = bipartiteSplit(shifted, numNodes, first == 1);
        if (!split.possible) cout << "x";
        else {
            for (int i = 0; i < (int)split.side1.size(); i++) cout << (i ? "," : "") << split.side1[i];
            cout << "|";
            for (int i = 0; i < (int)split.side2.size(); i++) cout << (i ? "," : "") << split.side2[i];
        }
        cout << "\\n";
    }
}
'''
    with tempfile.TemporaryDirectory() as tmp:
        exe = os.path.join(tmp, "cuts")
        open(exe + ".cpp", "w").write(src)
        r = subprocess.run(["g++", "-std=c++17", "-Wall", "-fsanitize=address,undefined", "-o", exe, exe + ".cpp"],
                           capture_output=True, text=True)
        if r.returncode:
            sys.exit("FAIL cpp compile\n" + r.stderr[:2000])
        inp = f"{len(cases)}\n" + "".join(
            f"{len(e)} {fi} {n}\n" + "".join(f"{a} {b}\n" for a, b in e) + "".join(f"{a} {b}\n" for a, b in sh)
            for e, fi, n, sh in cases)
        r = subprocess.run([exe], input=inp, capture_output=True, text=True)
        got = r.stdout.splitlines()
        if r.returncode or got != outs:
            k = next((k for k in range(len(outs)) if k >= len(got) or got[k] != outs[k]), len(outs))
            sys.exit(f"FAIL cpp line {k}: {got[k] if k < len(got) else r.stderr[-800:]}\n  python: {outs[k]}")
    print("cpp: prints exactly what python does")


if __name__ == "__main__":
    main()
