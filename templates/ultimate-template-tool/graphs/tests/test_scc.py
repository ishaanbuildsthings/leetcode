"""Tests graphs/scc.{py,cpp}: random directed graphs (0- and 1-indexed ranges, isolated nodes, repeats, self-loops) are
checked against a brute force (reachability by search from every node): same components, ids in reverse topological
order, componentAdj = every crossing edge. The C++ file, built with sanitizers, has to print exactly what Python does.

    python3 test_scc.py
"""
import os
import random
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)


def reach(adj, s):
    seen, st = {s}, [s]
    while st:
        x = st.pop()
        for y in adj[x]:
            if y not in seen:
                seen.add(y)
                st.append(y)
    return seen


def main():
    ns = {}
    exec(open(os.path.join(SRC, "scc.py")).read(), ns)
    rnd = random.Random(5)
    ex = ns["buildScc"]([(1, 2), (2, 3), (3, 1), (4, 3)], 5, oneIndexed=True)
    assert (ex.numComponents, ex.nodeToComponentId, ex.componentNodes, ex.componentAdj) == (3, [-1, 0, 0, 0, 1, 2], [[1, 2, 3], [4], [5]], [[], [0], []])
    cases, outs = [], []
    for _ in range(400):
        first = rnd.choice([0, 1])
        n = rnd.randint(0, 12)
        last = first + n - 1
        edges = [(rnd.randint(first, last), rnd.randint(first, last)) for _ in range(rnd.randint(0, 3 * n))] if n else []
        s = ns["buildScc"](edges, n, first == 1)
        adj = {x: [] for x in range(first, last + 1)}
        for a, b in edges:
            adj[a].append(b)
        r = {x: reach(adj, x) for x in adj}
        for x in adj:
            for y in adj:
                same = y in r[x] and x in r[y]
                assert same == (s.nodeToComponentId[x] == s.nodeToComponentId[y]), (edges, first, last)
        assert all(s.nodeToComponentId[x] == -1 for x in range(first))
        assert s.numComponents == len(s.componentNodes) and sorted(sum(s.componentNodes, [])) == list(adj)
        want = [[] for _ in range(s.numComponents)]
        for a, b in edges:
            ca, cb = s.nodeToComponentId[a], s.nodeToComponentId[b]
            if ca != cb:
                assert ca > cb, "not reverse topological"
                want[ca].append(cb)
        assert [sorted(x) for x in s.componentAdj] == [sorted(x) for x in want]
        cases.append((edges, first, last))
        outs.append(f"{s.numComponents}|{' '.join(map(str, s.nodeToComponentId))}|" + ";".join(" ".join(map(str, c)) for c in s.componentNodes)
                    + "|" + ";".join(" ".join(map(str, c)) for c in s.componentAdj))
    print(f"python: {len(cases)} graphs agree with brute force")
    src = open(os.path.join(SRC, "scc.cpp")).read() + r'''
int main() {
    int t; cin >> t;
    while (t--) {
        int m, n, oneIndexed; cin >> m >> n >> oneIndexed;
        vector<pair<int, int>> edges(m);
        for (auto& [a, b] : edges) cin >> a >> b;
        Scc s = buildScc(edges, n, oneIndexed);
        cout << s.numComponents << "|";
        for (size_t i = 0; i < s.nodeToComponentId.size(); i++) cout << (i ? " " : "") << s.nodeToComponentId[i];
        auto lists = [](const vector<vector<int>>& v) {
            for (size_t i = 0; i < v.size(); i++) {
                if (i) cout << ";";
                for (size_t k = 0; k < v[i].size(); k++) cout << (k ? " " : "") << v[i][k];
            }
        };
        cout << "|"; lists(s.componentNodes); cout << "|"; lists(s.componentAdj); cout << "\n";
    }
}
'''
    open("/tmp/scc.cpp", "w").write(src)
    r = subprocess.run(["g++", "-std=c++17", "-Wall", "-fsanitize=address,undefined", "-o", "/tmp/scc", "/tmp/scc.cpp"], capture_output=True, text=True)
    if r.returncode or "warning" in r.stderr:
        sys.exit("FAIL cpp compile\n" + r.stderr[:1500])
    inp = f"{len(cases)}\n" + "".join(f"{len(e)} {l - f + 1} {f}\n" + "".join(f"{a} {b}\n" for a, b in e) for e, f, l in cases)
    got = subprocess.run(["/tmp/scc"], input=inp, capture_output=True, text=True, timeout=60).stdout.split("\n")[:-1]
    if got != outs:
        k = next(k for k in range(len(outs)) if k >= len(got) or got[k] != outs[k])
        sys.exit(f"FAIL cpp case {k}: {got[k] if k < len(got) else 'nothing'} vs python {outs[k]}")
    print("cpp: prints exactly what python does")


if __name__ == "__main__":
    main()
