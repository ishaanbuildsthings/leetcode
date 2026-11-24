"""Checks for graphs/euler{Circuit,Path}{Directed,Undirected}.{py,cpp}: the header examples, then random small
multigraphs (self-loops, repeated edges, 0- and 1-indexed labels, optional start / end) against a backtracking search
for whether a valid walk exists, validating every walk returned. usage: python3 tests/test_euler.py [--py | --cpp]"""
import os
import random
import subprocess
import sys
import tempfile
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOL = os.path.dirname(ROOT)
NAMES = ["eulerCircuitDirected", "eulerPathDirected", "eulerCircuitUndirected", "eulerPathUndirected"]


def load_py():
    fns = {}
    for name in NAMES:
        ns = {}
        exec(open(os.path.join(ROOT, name + ".py")).read(), ns)
        fns[name] = ns[name]
    return fns


def edge_key(a, b, directed):
    return (a, b) if directed else (min(a, b), max(a, b))


def exists(edges, directed, circuit, start, end):
    """backtracking: is there a walk using every edge once, starting at start / ending at end when given?"""
    if circuit and start is not None:
        end = start
    left = Counter(edge_key(a, b, directed) for a, b in edges)
    total = len(edges)
    nodes = sorted({x for e in edges for x in e})
    firsts = [start] if start is not None else nodes

    def go(node, used, first):
        if used == total:
            if circuit and node != first:
                return False
            return end is None or node == end
        for (a, b), count in list(left.items()):
            if count == 0:
                continue
            for x, y in ([(a, b)] if directed else [(a, b), (b, a)]):
                if x != node:
                    continue
                left[(a, b)] -= 1
                ok = go(y, used + 1, first)
                left[(a, b)] += 1
                if ok:
                    return True
        return False

    return any(go(first, 0, first) for first in firsts)


def valid(walk, edges, directed, circuit, start, end):
    if len(walk) != len(edges) + 1:
        return False
    if start is not None and walk[0] != start:
        return False
    if end is not None and walk[-1] != end:
        return False
    if circuit and walk[0] != walk[-1]:
        return False
    steps = Counter(edge_key(walk[i], walk[i + 1], directed) for i in range(len(walk) - 1))
    return steps == Counter(edge_key(a, b, directed) for a, b in edges)


def expected_empty(circuit, start, end):
    """the documented result for no edges"""
    if circuit:
        return [] if start is None else [start]
    if start is not None and end is not None and start != end:
        return None
    if start is not None:
        return [start]
    return [] if end is None else [end]


def random_case(rng, name):
    directed = "Undirected" not in name
    circuit = "Circuit" in name
    low = rng.choice([0, 1])
    k = rng.randrange(1, 5)
    m = rng.choice([0, 1, 2, 3, 4, 5, 6, 7])
    edges = [(rng.randrange(low, low + k), rng.randrange(low, low + k)) for _ in range(m)]
    if rng.random() < 0.3 and edges:
        # bias toward graphs that do have a walk: close a random walk into a circuit or leave it as a path
        node = rng.randrange(low, low + k)
        edges = []
        for _ in range(m):
            nxt = rng.randrange(low, low + k)
            edges.append((node, nxt))
            node = nxt
        if rng.random() < 0.5:
            edges.append((node, edges[0][0]))
        rng.shuffle(edges)
        if not directed:
            edges = [(b, a) if rng.random() < 0.5 else (a, b) for a, b in edges]
    pick = lambda: None if rng.random() < 0.5 else rng.randrange(low, low + k + 1)
    start = pick()
    end = None if circuit else pick()
    return name, edges, start, end


def check(name, edges, start, end, got, lang):
    directed = "Undirected" not in name
    circuit = "Circuit" in name
    if not edges:
        want = expected_empty(circuit, start, end)
        if lang == "cpp" and want is None:
            want = []
        assert got == want, (lang, name, edges, start, end, got, want)
        return
    ok = exists(edges, directed, circuit, start, end)
    if lang == "cpp" and got == []:
        got = None
    if ok:
        assert got is not None and valid(got, edges, directed, circuit, start, end), (lang, name, edges, start, end, got)
    else:
        assert got is None, (lang, name, edges, start, end, got)


EXAMPLES = [
    ("eulerCircuitDirected", [(1, 2), (2, 3), (3, 1)], None, None, [1, 2, 3, 1]),
    ("eulerCircuitDirected", [(1, 2), (2, 3), (3, 1)], 2, None, [2, 3, 1, 2]),
    ("eulerCircuitDirected", [(1, 2), (2, 3)], None, None, None),
    ("eulerPathDirected", [(1, 2), (2, 3), (3, 1), (1, 4)], None, None, [1, 2, 3, 1, 4]),
    ("eulerPathDirected", [(1, 2), (2, 1)], 2, 2, [2, 1, 2]),
    ("eulerPathDirected", [(1, 2), (1, 3)], None, None, None),
    ("eulerCircuitUndirected", [(1, 2), (2, 3), (3, 1)], None, None, [1, 3, 2, 1]),
    ("eulerCircuitUndirected", [(1, 2), (2, 3), (3, 1)], 2, None, [2, 3, 1, 2]),
    ("eulerCircuitUndirected", [(1, 2), (2, 3)], None, None, None),
    ("eulerPathUndirected", [(1, 2), (2, 3), (3, 1), (1, 4)], None, None, [1, 3, 2, 1, 4]),
    ("eulerPathUndirected", [(1, 2), (2, 3)], 3, None, [3, 2, 1]),
    ("eulerPathUndirected", [(1, 2), (1, 3), (1, 4)], None, None, None),
]

CPP_DRIVER = """
int main() {
    int t; cin >> t;
    while (t--) {
        int kind, start, end, m; cin >> kind >> start >> end >> m;
        vector<pair<int, int>> edges(m);
        for (auto& [a, b] : edges) cin >> a >> b;
        vector<int> got;
        if (kind == 0) got = eulerCircuitDirected(edges, start);
        if (kind == 1) got = eulerPathDirected(edges, start, end);
        if (kind == 2) got = eulerCircuitUndirected(edges, start);
        if (kind == 3) got = eulerPathUndirected(edges, start, end);
        cout << got.size();
        for (int x : got) cout << ' ' << x;
        cout << '\\n';
    }
}
"""


def run_cpp(cases):
    sys.path.insert(0, TOOL)
    compiler = subprocess.run([sys.executable, os.path.join(TOOL, "find_compiler.py")], capture_output=True, text=True).stdout.strip() or "g++"
    with tempfile.TemporaryDirectory() as tmp:
        src = os.path.join(tmp, "t.cpp")
        with open(src, "w") as f:
            for name in NAMES:
                f.write(open(os.path.join(ROOT, name + ".cpp")).read() + "\n")
            f.write(CPP_DRIVER)
        exe = os.path.join(tmp, "t")
        subprocess.run([compiler, "-std=c++17", "-O2", "-Wall", "-Werror", src, "-o", exe], check=True)
        lines = [str(len(cases))]
        for name, edges, start, end in cases:
            s = -1 if start is None else start
            e = -1 if end is None else end
            lines.append(f"{NAMES.index(name)} {s} {e} {len(edges)} " + " ".join(f"{a} {b}" for a, b in edges))
        out = subprocess.run([exe], input="\n".join(lines) + "\n", capture_output=True, text=True, check=True).stdout
    results = []
    for line in out.strip().split("\n"):
        nums = list(map(int, line.split()))
        results.append(nums[1:])
    return results


def main():
    langs = ["py", "cpp"]
    if "--py" in sys.argv:
        langs = ["py"]
    if "--cpp" in sys.argv:
        langs = ["cpp"]
    rng = random.Random(1)
    cases = [random_case(rng, rng.choice(NAMES)) for _ in range(6000)]
    if "py" in langs:
        fns = load_py()
        for name, edges, start, end, want in EXAMPLES:
            kwargs = {} if start is None else {"start": start}
            if end is not None:
                kwargs["end"] = end
            got = fns[name](edges, **kwargs)
            assert got == want, ("py example", name, edges, start, end, got, want)
        for name, edges, start, end in cases:
            kwargs = {"start": start} if "Circuit" in name else {"start": start, "end": end}
            check(name, edges, start, end, fns[name](edges, **kwargs), "py")
        print(f"py: {len(EXAMPLES)} examples + {len(cases)} random cases ok")
    if "cpp" in langs:
        got = run_cpp([(n, e, s, t) for n, e, s, t, _ in EXAMPLES])
        for (name, edges, start, end, want), g in zip(EXAMPLES, got):
            assert g == (want or []), ("cpp example", name, edges, start, end, g, want)
        for case, g in zip(cases, run_cpp(cases)):
            check(*case, g, "cpp")
        print(f"cpp: {len(EXAMPLES)} examples + {len(cases)} random cases ok")


if __name__ == "__main__":
    main()
