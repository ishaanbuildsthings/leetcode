"""Tests graphs/functionalGraph{,.oneIndexed}.*: random functional graphs (self-loops, long tails, branching trees,
many components, broom shapes) with edges in random order are checked method by method against walking the graph
step by step; the documented example must hold and bad input must raise. The C++ files, built with sanitizers, must
print exactly what Python does.

    python3 test_functional_graph.py
"""
import os
import random
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)


def load(file):
    ns = {}
    exec(open(os.path.join(SRC, file + ".py")).read(), ns)
    return ns["FunctionalGraph"]


def randomGraph(rnd, n, first):
    shape = rnd.randrange(4)
    nxt = {}
    nodes = list(range(first, first + n))
    if shape == 0:  # anything
        for a in nodes:
            nxt[a] = rnd.choice(nodes)
    elif shape == 1:  # one big cycle with branching trees
        k = rnd.randint(1, n)
        cyc = nodes[:k]
        for i, a in enumerate(cyc):
            nxt[a] = cyc[(i + 1) % k]
        for i in range(k, n):
            nxt[nodes[i]] = nodes[rnd.randrange(i)]
    elif shape == 2:  # broom: many starts into one long path into a self-loop
        pathLen = rnd.randint(1, n)
        for i in range(pathLen - 1):
            nxt[nodes[i]] = nodes[i + 1]
        nxt[nodes[pathLen - 1]] = nodes[pathLen - 1]
        for i in range(pathLen, n):
            nxt[nodes[i]] = nodes[0]
    else:  # all self-loops and 2-cycles
        for a in nodes:
            nxt[a] = rnd.choice([a, nodes[(a - first) ^ 1] if (a - first) ^ 1 < n else a])
    perm = nodes[:]
    rnd.shuffle(perm)  # relabel so cycles and tails aren't in label order
    relabel = dict(zip(nodes, perm))
    nxt = {relabel[a]: relabel[b] for a, b in nxt.items()}
    edges = [[a, b] for a, b in nxt.items()]
    rnd.shuffle(edges)
    return nxt, edges


def walk(nxt, a, k):
    for _ in range(k):
        a = nxt[a]
    return a


def check(F, nxt, edges, first, rnd):
    n = len(nxt)
    nodes = range(first, first + n)
    fg = F(edges)
    onCycle = set()
    for a in nodes:
        x = walk(nxt, a, n)  # surely on a cycle
        y = x
        while True:
            onCycle.add(y)
            y = nxt[y]
            if y == x:
                break
    # cycles: walking order, smallest first, sorted, exactly the cycle nodes
    cycles = fg.cycles()
    assert sorted(x for c in cycles for x in c) == sorted(onCycle), cycles
    assert cycles == sorted(cycles)
    for c in cycles:
        assert c[0] == min(c)
        assert all(nxt[c[i]] == c[(i + 1) % len(c)] for i in range(len(c)))
    cycleOfNode = {x: cid for cid, c in enumerate(cycles) for x in c}
    for a in nodes:
        steps, x = 0, a
        while x not in onCycle:
            x = nxt[x]
            steps += 1
        assert fg.numEdgesToCrossBeforeCycle(a) == steps
        assert fg.firstCycleNodeHit(a) == x
        assert fg.componentId(a) == cycleOfNode[x]
        for k in list(range(0, 2 * n + 2)) + [rnd.randint(0, 10**18) for _ in range(3)]:
            want = walk(nxt, a, k) if k <= 2 * n + 2 else walk(nxt, a, n + (k - n) % len(cycles[cycleOfNode[x]]))
            assert fg.kthNext(a, k) == want, (a, k)
    for a in nodes:
        seen = {}
        x, steps = a, 0
        while x not in seen:
            seen[x] = steps
            x = nxt[x]
            steps += 1
        for b in nodes:
            assert fg.stepsFromTo(a, b) == seen.get(b), (a, b)
    # components: cycle, then walks from every node with no incoming edges, each stopping at the first node listed
    comps = fg.components()
    assert len(comps) == len(cycles)
    hasIncoming = {b for b in nxt.values()}
    starts = [a for a in nodes if a not in hasIncoming]
    allStarts = []
    for cid, (cyc, tails) in enumerate(comps):
        assert cyc == cycles[cid]
        listed = set(cyc)
        for w in tails:
            assert len(w) >= 2 and w[0] not in hasIncoming
            assert all(nxt[w[i]] == w[i + 1] for i in range(len(w) - 1))
            assert all(x not in listed for x in w[:-1]) and w[-1] in listed
            listed.update(w)
            allStarts.append(w[0])
        assert listed == {a for a in nodes if fg.componentId(a) == cid}
        assert [w[0] for w in tails] == sorted(w[0] for w in tails)
    assert sorted(allStarts) == starts
    assert sum(len(c) + sum(len(w) for w in t) for c, t in comps) <= 2 * n
    return fg


def dump(fg, nodes, queries):
    out = [" ".join(",".join(map(str, c)) for c in fg.cycles())]
    out.append(" ".join(f"{fg.componentId(a)}/{fg.numEdgesToCrossBeforeCycle(a)}/{fg.firstCycleNodeHit(a)}" for a in nodes))
    out.append(" ".join(str(fg.kthNext(a, k)) for a, k in queries))
    out.append(" ".join(str(-1 if fg.stepsFromTo(a, b) is None else fg.stepsFromTo(a, b)) for a in nodes for b in nodes))
    out.append(" | ".join(",".join(map(str, c)) + ":" + ";".join(",".join(map(str, w)) for w in t) for c, t in fg.components()))
    return out


def main():
    for first in (0, 1):
        file = "functionalGraph" + (".oneIndexed" if first else "")
        F = load(file)
        s = lambda x: x + first

        fg = F([(s(0), s(1)), (s(1), s(2)), (s(2), s(3)), (s(3), s(1)), (s(4), s(2)), (s(5), s(4)), (s(6), s(0)), (s(7), s(7)), (s(8), s(7))])
        S = lambda xs: [s(x) for x in xs]
        assert fg.cycles() == [S([1, 2, 3]), S([7])]
        assert (fg.componentId(s(5)), fg.numEdgesToCrossBeforeCycle(s(5)), fg.firstCycleNodeHit(s(5))) == (0, 2, s(2))
        assert fg.kthNext(s(5), 4) == s(1) and fg.stepsFromTo(s(6), s(3)) == 4 and fg.stepsFromTo(s(4), s(0)) is None
        assert fg.components() == [(S([1, 2, 3]), [S([5, 4, 2]), S([6, 0, 1])]), (S([7]), [S([8, 7])])]

        for bad in ([(s(0), s(1)), (s(0), s(0))], [(s(0), s(2)), (s(1), s(0))], [(s(0) - 1, s(0)), (s(1), s(0))]):
            try:
                F(bad)
            except ValueError:
                pass
            else:
                sys.exit(f"FAIL {file}: {bad} should raise")
        for call in (lambda: fg.kthNext(s(0), -1), lambda: fg.componentId(s(9)), lambda: fg.stepsFromTo(s(0) - 1, s(0))):
            try:
                call()
            except ValueError:
                pass
            else:
                sys.exit(f"FAIL {file}: bad call should raise")

        rnd = random.Random(11)
        cases, outs = [], []
        for _ in range(600):
            n = rnd.randint(1, 12)
            nxt, edges = randomGraph(rnd, n, first)
            fg = check(F, nxt, edges, first, rnd)
            nodes = list(range(first, first + n))
            queries = [(rnd.choice(nodes), rnd.choice([rnd.randint(0, 30), rnd.randint(0, 10**18)])) for _ in range(20)]
            cases.append((edges, queries))
            outs += dump(fg, nodes, queries)
        print(f"{file}.py: matches walking the graph on {len(cases)} random graphs")

        src = open(os.path.join(SRC, file + ".cpp")).read() + f'''
int main() {{
    int t; cin >> t;
    while (t--) {{
        int n; cin >> n;
        vector<array<int, 2>> edges(n);
        for (auto& e : edges) cin >> e[0] >> e[1];
        int q; cin >> q;
        vector<pair<int, long long>> queries(q);
        for (auto& [a, k] : queries) cin >> a >> k;
        FunctionalGraph fg(edges);
        string line;
        for (auto& c : fg.cycles()) {{
            if (&c != &fg.cycles()[0]) cout << " ";
            for (int i = 0; i < (int)c.size(); i++) cout << (i ? "," : "") << c[i];
        }}
        cout << "\\n";
        for (int a = {first}; a < n + {first}; a++)
            cout << (a > {first} ? " " : "") << fg.componentId(a) << "/" << fg.numEdgesToCrossBeforeCycle(a) << "/" << fg.firstCycleNodeHit(a);
        cout << "\\n";
        for (int i = 0; i < q; i++) cout << (i ? " " : "") << fg.kthNext(queries[i].first, queries[i].second);
        cout << "\\n";
        bool firstOut = true;
        for (int a = {first}; a < n + {first}; a++)
            for (int b = {first}; b < n + {first}; b++) {{
                cout << (firstOut ? "" : " ") << fg.stepsFromTo(a, b);
                firstOut = false;
            }}
        cout << "\\n";
        auto& comps = fg.components();
        for (int cid = 0; cid < (int)comps.size(); cid++) {{
            if (cid) cout << " | ";
            for (int i = 0; i < (int)comps[cid].cycle.size(); i++) cout << (i ? "," : "") << comps[cid].cycle[i];
            cout << ":";
            for (int w = 0; w < (int)comps[cid].tails.size(); w++) {{
                if (w) cout << ";";
                auto& walk = comps[cid].tails[w];
                for (int i = 0; i < (int)walk.size(); i++) cout << (i ? "," : "") << walk[i];
            }}
        }}
        cout << "\\n";
    }}
    bool threw = false;
    try {{ FunctionalGraph bad({{{{{first}, {first + 1}}}, {{{first}, {first}}}}}); }} catch (const invalid_argument&) {{ threw = true; }}
    if (!threw) {{ cout << "no throw\\n"; return 1; }}
    threw = false;
    try {{ FunctionalGraph ok({{{{{first}, {first}}}}}); ok.kthNext({first}, -1); }} catch (const invalid_argument&) {{ threw = true; }}
    if (!threw) {{ cout << "no throw on k\\n"; return 1; }}
}}
'''
        with tempfile.TemporaryDirectory() as tmp:
            exe = os.path.join(tmp, "fg")
            open(exe + ".cpp", "w").write(src)
            r = subprocess.run(["g++", "-std=c++17", "-Wall", "-fsanitize=address,undefined", "-o", exe, exe + ".cpp"],
                               capture_output=True, text=True)
            if r.returncode:
                sys.exit(f"FAIL cpp {file} compile\n" + r.stderr[:2000])
            inp = f"{len(cases)}\n" + "".join(
                f"{len(e)}\n" + "".join(f"{a} {b}\n" for a, b in e) + f"{len(q)}\n" + "".join(f"{a} {k}\n" for a, k in q)
                for e, q in cases)
            r = subprocess.run([exe], input=inp, capture_output=True, text=True)
            got = r.stdout.splitlines()
            if r.returncode or got != outs:
                k = next((k for k in range(len(outs)) if k >= len(got) or got[k] != outs[k]), len(outs))
                sys.exit(f"FAIL cpp {file} line {k}: {got[k] if k < len(got) else r.stdout[-300:] + r.stderr[-800:]}\n  python: {outs[k] if k < len(outs) else ''}")
        print(f"{file}.cpp: prints exactly what Python does")


if __name__ == "__main__":
    main()
