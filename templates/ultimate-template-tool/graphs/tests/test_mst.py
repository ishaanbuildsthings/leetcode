"""Tests graphs/minimumSpanningTrees.* on random weighted graphs (negative and tied weights, repeated edges, self-loops,
disconnected graphs, isolated labels):
  - the result is a forest made of the given edges that connects exactly what the graph connects
  - its total weight equals the best over every subset of edges (brute force, small graphs)
  - for every pair of nodes, the biggest edge on the tree path equals the smallest possible biggest edge over all
    paths in the graph (brute force: the cheapest threshold at which the two nodes connect)
The C++ file, built with sanitizers, must print the same tree as Python.

    python3 test_mst.py
"""
import itertools
import os
import random
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
ns = {}
exec(open(os.path.join(SRC, "minimumSpanningTrees.py")).read(), ns)
minimumSpanningTrees = ns["minimumSpanningTrees"]


def comps(size, edges):
    parent = list(range(size))

    def find(x):
        while parent[x] != x:
            x = parent[x]
        return x

    for a, b, *_ in edges:
        parent[find(a)] = find(b)
    return [find(x) for x in range(size)]


def treePathMax(tree, size, a, b):
    adj = [[] for _ in range(size)]
    for x, y, w in tree:
        adj[x].append((y, w))
        adj[y].append((x, w))
    stack, best = [(a, -1, None)], {}
    while stack:
        node, par, mx = stack.pop()
        best[node] = mx
        for nxt, w in adj[node]:
            if nxt != par:
                stack.append((nxt, node, w if mx is None else max(mx, w)))
    return best.get(b, "unreached")


def main():
    for bad in ([(-1, 0, 1)],):
        try:
            minimumSpanningTrees(bad)
        except ValueError:
            pass
        else:
            sys.exit("FAIL: negative label should raise")
    assert minimumSpanningTrees([]) == [] and minimumSpanningTrees([(2, 2, 5)]) == []
    assert minimumSpanningTrees([(1, 2, 5), (3, 4, 1)]) == [[[1, 2, 5]], [[3, 4, 1]]]

    rnd = random.Random(9)
    cases, outs = [], []
    for _ in range(1500):
        size = rnd.randint(1, 7)
        edges = [(rnd.randrange(size), rnd.randrange(size), rnd.randint(-5, 5)) for _ in range(rnd.randint(0, 10))]
        trees = minimumSpanningTrees(edges)
        tree = sorted((e for t in trees for e in t), key=lambda e: e[2])
        # one tree per piece with edges, each connected, cheapest first, ordered by smallest node
        smallestNodes = []
        for t in trees:
            assert t and [e[2] for e in t] == sorted(e[2] for e in t)
            nodesT = sorted({x for e in t for x in e[:2]})
            for x in nodesT[1:]:
                assert treePathMax(t, max(nodesT) + 1, nodesT[0], x) != "unreached", (edges, trees)
            smallestNodes.append(nodesT[0])
        assert smallestNodes == sorted(smallestNodes) and len(set(smallestNodes)) == len(smallestNodes)
        # made of the given edges, in order of weight, as a forest spanning each component
        pool = [list(e) for e in edges]
        for e in tree:
            assert e in pool, (e, edges)
            pool.remove(e)
        assert [e[2] for e in tree] == sorted(e[2] for e in tree)
        realSize = max([max(a, b) + 1 for a, b, _ in edges], default=0)
        graphComps = comps(realSize, edges)
        assert comps(realSize, tree) == graphComps or len(set(comps(realSize, tree))) == len(set(graphComps))
        assert len(tree) == realSize - len(set(graphComps)), (edges, tree)
        # total weight vs every subset of edges that is a spanning forest
        best = None
        for k in range(len(edges) + 1):
            if k != len(tree):
                continue
            for sub in itertools.combinations(edges, k):
                if len(set(comps(realSize, sub))) == len(set(graphComps)):
                    total = sum(w for _, _, w in sub)
                    best = total if best is None else min(best, total)
        assert sum(w for _, _, w in tree) == (best if best is not None else 0), (edges, tree)
        # bottleneck: smallest threshold at which a and b connect using edges of weight <= threshold
        for a in range(realSize):
            for b in range(realSize):
                if a == b or graphComps[a] != graphComps[b]:
                    continue
                need = min(t for t in sorted({w for _, _, w in edges})
                           if (lambda c: c[a] == c[b])(comps(realSize, [e for e in edges if e[2] <= t])))
                assert treePathMax(tree, realSize, a, b) == need, (edges, tree, a, b)
        cases.append(edges)
        outs.append(" | ".join(" ".join(f"{a},{b},{w}" for a, b, w in t) for t in trees))
    print(f"python: {len(cases)} graphs: minimum total weight and smallest biggest-edge paths check out")

    src = open(os.path.join(SRC, "minimumSpanningTrees.cpp")).read() + '''
int main() {
    int t; cin >> t;
    while (t--) {
        int m; cin >> m;
        vector<array<ll, 3>> edges(m);
        for (auto& e : edges) cin >> e[0] >> e[1] >> e[2];
        auto trees = minimumSpanningTrees(edges);
        for (int t = 0; t < (int)trees.size(); t++) {
            if (t) cout << " | ";
            for (int i = 0; i < (int)trees[t].size(); i++) cout << (i ? " " : "") << trees[t][i][0] << "," << trees[t][i][1] << "," << trees[t][i][2];
        }
        cout << "\\n";
    }
}
'''
    with tempfile.TemporaryDirectory() as tmp:
        exe = os.path.join(tmp, "mst")
        open(exe + ".cpp", "w").write(src)
        r = subprocess.run(["g++", "-std=c++17", "-Wall", "-fsanitize=address,undefined", "-o", exe, exe + ".cpp"],
                           capture_output=True, text=True)
        if r.returncode:
            sys.exit("FAIL cpp compile\n" + r.stderr[:2000])
        inp = f"{len(cases)}\n" + "".join(f"{len(e)}\n" + "".join(f"{a} {b} {w}\n" for a, b, w in e) for e in cases)
        r = subprocess.run([exe], input=inp, capture_output=True, text=True)
        got = r.stdout.splitlines()
        if r.returncode or got != outs:
            k = next((k for k in range(len(outs)) if k >= len(got) or got[k] != outs[k]), len(outs))
            sys.exit(f"FAIL cpp case {k}: {got[k] if k < len(got) else r.stderr[-800:]}\n  python: {outs[k]}")
    print("cpp: prints the same trees as python")


if __name__ == "__main__":
    main()
