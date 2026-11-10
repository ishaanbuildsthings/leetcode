"""Tests the small hand-written folders (combinatorics, next-permutation, trees, reroot, bitset) against brute force.

    python3 test_misc.py          # Python and C++
    python3 test_misc.py --py     # Python only
"""
import importlib.util
import itertools
import math
import os
import random
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
from find_compiler import cxx, sanitize_flags  # noqa: E402

failures = []
WORK = tempfile.mkdtemp()
USE_CPP = "--py" not in sys.argv


def load(rel):
    spec = importlib.util.spec_from_file_location("t_" + rel.replace("/", "_").replace(".", "_"), os.path.join(ROOT, rel))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def same(name, got, want):
    if got != want:
        failures.append(f"FAIL  {name}: got {got!r}, expected {want!r}")
    return got == want


def raises(name, fn):
    try:
        fn()
    except (ValueError, IndexError):
        return
    failures.append(f"FAIL  {name}: should have raised")


def run_cpp(name, rel, body, stdin, want):
    """Compile body as main() next to the template at rel, feed it stdin, compare its stdout lines to want."""
    if not USE_CPP:
        return
    tag = name.replace("/", "_").replace(".", "_")
    src, exe = os.path.join(WORK, tag + ".cpp"), os.path.join(WORK, tag)
    open(src, "w").write(f'#include "{os.path.join(ROOT, rel)}"\nint main() {{\n{body}\n}}\n')
    built = subprocess.run([cxx(), "-std=c++17", "-O1", "-w", *sanitize_flags(), "-o", exe, src], capture_output=True, text=True)
    if built.returncode:
        failures.append(f"FAIL  {name} [cpp]: compile error\n{built.stderr[:1500]}")
        return
    got = subprocess.run([exe], input=stdin, capture_output=True, text=True, timeout=120)
    if got.returncode:
        failures.append(f"FAIL  {name} [cpp]: exit {got.returncode}\n{got.stderr[:800]}")
        return
    lines = got.stdout.split("\n")[:-1]
    for k, (a, b) in enumerate(zip(lines, want)):
        if a != b:
            failures.append(f"FAIL  {name} [cpp] line {k}: got {a}, expected {b}")
            return
    same(f"{name} [cpp] line count", len(lines), len(want))


# ---- combinatorics ----

def identical_ways(items, buckets, allow_empty):
    if buckets == 0:
        return int(items == 0)
    if allow_empty:
        return math.comb(items + buckets - 1, buckets - 1)
    return math.comb(items - 1, buckets - 1) if items >= 1 else 0


def test_modcalc():
    M = load("combinatorics/ModCalc.py")
    N = 40
    stdin, want = [], []
    for p in (2, 3, 5, 7, 13, 41, 43, 998244353):
        mc = M.ModCalc(N, p)
        stdin.append(f"{p}")
        for n in range(-2, N + 1):
            for k in range(-2, N + 2):
                c = math.comb(n, k) % p if 0 <= k <= n else 0
                perm = math.perm(n, k) % p if 0 <= k <= n else 0
                same(f"ModCalc.py C({n},{k}) mod {p}", mc.nChooseKWithMod(n, k), c)
                same(f"ModCalc.py P({n},{k}) mod {p}", mc.nPermuteKWithMod(n, k), perm)
                stdin.append(f"{n} {k}")
                want.append(f"{c} {perm}")
        stdin.append("x x")
        for a in range(N + 1):
            for b in range(N + 1 - a):
                same(f"ModCalc.py interleave({a},{b}) mod {p}", mc.interleaveTwoSequencesWithMod(a, b), math.comb(a + b, a) % p)
        for items in range(12):
            for buckets in range(12):
                for allow in (True, False):
                    same(f"ModCalc.py stars({items},{buckets},{allow}) mod {p}",
                         mc.waysToPutIdenticalItemsIntoDistinctBucketsWithMod(items, buckets, allow),
                         identical_ways(items, buckets, allow) % p)
        for x in range(N + 1):
            same(f"ModCalc.py {x}! mod {p}", mc.getFactorialWithMod(x), math.factorial(x) % p)
    body = f"""
    string a, b;
    while (cin >> a) {{
        long long p = stoll(a);
        ModCalc mc({N}, p);
        while (cin >> a >> b && a != "x") {{
            int n = stoi(a), k = stoi(b);
            cout << mc.nChooseKWithMod(n, k) << ' ' << mc.nPermuteKWithMod(n, k) << '\\n';
        }}
    }}"""
    run_cpp("combinatorics/ModCalc", "combinatorics/ModCalc.cpp", body, "\n".join(stdin) + "\n", want)


def test_fibonacci():
    F = load("combinatorics/Fibonacci.py")
    fibs = [0, 1]
    while fibs[-1] + fibs[-2] < 2**63:
        fibs.append(fibs[-1] + fibs[-2])
    fibset = set(fibs)
    xs = sorted({y for f in fibs for y in (f - 1, f, f + 1) if -1 <= y < 2**63} | {6 * 10**18, 2**63 - 1, -5})
    want = [str(int(x in fibset)) for x in xs]
    for x in xs:
        same(f"Fibonacci.py isFib({x})", F.isFib(x), x in fibset)
    run_cpp("combinatorics/isFib", "combinatorics/Fibonacci.cpp",
            "long long x; while (cin >> x) cout << isFib(x) << '\\n';", " ".join(map(str, xs)), want)
    all_fibs = fibs[:]
    limits = [-1, 0, 1, 2, 10, 10**18, 2**63 - 1]
    want = []
    for n in limits:
        expected = [0, 1, *[f for f in all_fibs[2:] if f <= n]] if n >= 1 else ([0] if n == 0 else [])
        same(f"Fibonacci.py getFibList({n})", F.getFibList(n), expected)
        want.append(" ".join(map(str, expected)))
    body = """long long n; while (cin >> n) {
        auto v = getFibList(n);
        for (size_t i = 0; i < v.size(); i++) cout << (i ? " " : "") << v[i];
        cout << '\\n';
    }"""
    run_cpp("combinatorics/getFibList", "combinatorics/Fibonacci.cpp", body, " ".join(map(str, limits)), want)
    series = [0, 1]
    for _ in range(600):
        series.append(series[-1] + series[-2])
    stdin, want = [], []
    for x in range(1, 500):
        if x <= 93:
            same(f"Fibonacci.py getXthFib({x})", F.getXthFib(x), series[x - 1])
        for mod in (1, 2, 10**9 + 7, 4 * 10**18 + 37, 9 * 10**18 + 1, 2**63 - 25):
            same(f"Fibonacci.py getXthFibMod({x},{mod})", F.getXthFibMod(x, mod), series[x - 1] % mod)
            stdin.append(f"{x} {mod}")
            want.append(f"{series[x - 1] % mod}")
    run_cpp("combinatorics/getXthFibMod", "combinatorics/Fibonacci.cpp",
            "long long x, m; while (cin >> x >> m) cout << getXthFibMod(x, m) << '\\n';", "\n".join(stdin), want)
    raises("Fibonacci.py getXthFib(0)", lambda: F.getXthFib(0))
    raises("Fibonacci.py getXthFibMod(0)", lambda: F.getXthFibMod(0, 7))


# ---- next permutation ----

def all_arrays():
    for n in range(0, 7):
        for arr in itertools.product((1, 2, 3), repeat=n):
            yield list(arr)
    for n in range(1, 7):
        yield list(range(n, 0, -1))


def test_next_permutation():
    steps_py = load("next-permutation/NextPermutationSteps.py").nextPermutation
    next_py = load("next-permutation/NextPermutation.py").nextPermutation
    prev_py = load("next-permutation/PrevPermutation.py").prevPermutation
    next_ip = load("next-permutation/NextPermutation.inplace.py").nextPermutation
    prev_ip = load("next-permutation/PrevPermutation.inplace.py").prevPermutation
    in_next, want_next, want_prev, in_steps, want_steps = [], [], [], [], []
    show = lambda a: " ".join(map(str, a))
    for arr in all_arrays():
        perms = sorted(set(itertools.permutations(arr)))
        i = perms.index(tuple(arr))
        nx, pv = list(perms[(i + 1) % len(perms)]), list(perms[i - 1])
        same(f"NextPermutation.py {arr}", next_py(arr), nx)
        same(f"PrevPermutation.py {arr}", prev_py(arr), pv)
        a, b = arr[:], arr[:]
        next_ip(a)
        prev_ip(b)
        same(f"NextPermutation.inplace.py {arr}", a, nx)
        same(f"PrevPermutation.inplace.py {arr}", b, pv)
        in_next.append(f"{len(arr)} {show(arr)}")
        want_next.append(show(nx))
        want_prev.append(show(pv))
        for steps in (0, 1, 2, 3, len(perms) - 1, len(perms), len(perms) + 1, 2 * len(perms) + 5, 10**15):
            expected = list(perms[(i + steps) % len(perms)])
            same(f"NextPermutationSteps.py {arr} +{steps}", steps_py(arr, steps), expected)
            in_steps.append(f"{len(arr)} {show(arr)} {steps}")
            want_steps.append(show(expected))
    same("NextPermutationSteps.py string", steps_py("aab", 2), "baa")
    raises("NextPermutationSteps.py negative steps", lambda: steps_py([1, 2], -1))
    read = "int n; while (cin >> n) { vector<int> a(n); for (int& x : a) cin >> x; "
    out = "; for (int i = 0; i < n; i++) cout << (i ? \" \" : \"\") << r[i]; cout << '\\n'; }"
    for file, fn, want in (("NextPermutation", "nextPermutation", want_next), ("PrevPermutation", "prevPermutation", want_prev)):
        run_cpp(f"next-permutation/{file}", f"next-permutation/{file}.cpp", read + f"auto r = {fn}(a)" + out, "\n".join(in_next), want)
        run_cpp(f"next-permutation/{file}.inplace", f"next-permutation/{file}.inplace.cpp",
                read + f"auto r = a; {fn}(r)" + out, "\n".join(in_next), want)
    run_cpp("next-permutation/Steps", "next-permutation/NextPermutationSteps.cpp",
            read + "long long s; cin >> s; auto r = nextPermutation(a, s)" + out, "\n".join(in_steps), want_steps)


# ---- trees and reroot ----

def random_tree(rng, n, base):
    labels = list(range(base, base + n))
    rng.shuffle(labels)
    shape = rng.choice(("random", "path", "star"))
    edges = []
    for i in range(1, n):
        p = {"random": rng.randrange(i), "path": i - 1, "star": 0}[shape]
        edges.append([labels[p], labels[i]] if rng.random() < 0.5 else [labels[i], labels[p]])
    rng.shuffle(edges)
    return edges


def adjacency(edges, size):
    adj = [[] for _ in range(size)]
    for e in edges:
        w = e[2] if len(e) == 3 else 1
        adj[e[0]].append((e[1], w))
        adj[e[1]].append((e[0], w))
    return adj


def distances(adj, src):
    dist = {src: 0}
    stack = [src]
    while stack:
        u = stack.pop()
        for v, w in adj[u]:
            if v not in dist:
                dist[v] = dist[u] + w
                stack.append(v)
    return dist


def rooted(adj, root, size):
    children = [[] for _ in range(size)]
    seen = {root}
    stack = [root]
    while stack:
        u = stack.pop()
        for v, w in adj[u]:
            if v not in seen:
                seen.add(v)
                children[u].append((v, w))
                stack.append(v)
    return [sorted(c) for c in children]


def centroids(adj, nodes):
    n = len(nodes)
    worst = {}
    for u in nodes:
        biggest = 0
        for v, _ in adj[u]:
            seen = {u, v}
            stack = [v]
            while stack:
                x = stack.pop()
                for y, _ in adj[x]:
                    if y not in seen:
                        seen.add(y)
                        stack.append(y)
            biggest = max(biggest, len(seen) - 1)
        worst[u] = biggest
    best = min(worst.values())
    assert n >= 2 and best <= n // 2
    return sorted(u for u in nodes if worst[u] == best)


def edge_text(edges):
    return f"{len(edges)} " + " ".join(" ".join(map(str, e)) for e in edges)


def test_trees_and_reroot():
    rng = random.Random(1)
    plain = load("trees/edgeListToTree.py").edgeListToTree
    weighted = load("trees/weightedEdgeListToTree.py").edgeListToTree
    find = load("trees/findCentroids.py").findCentroids
    sum_py = load("reroot/SumOfDistances.py").sumOfDistances
    far_py = load("reroot/FarthestNode.py").farthestNodes
    sumw_py = load("reroot/SumOfDistances.weighted.py").sumOfDistances
    farw_py = load("reroot/FarthestNode.weighted.py").farthestNodes
    same("edgeListToTree.py single node", plain([], 0), [[]])
    same("edgeListToTree.py single node, root 1", plain([], 1), [[], []])
    same("weightedEdgeListToTree.py single node", weighted([], 0), [[]])
    raises("findCentroids.py no edges", lambda: find([]))
    cases = {k: ([], []) for k in ("tree", "wtree", "cent", "sum", "far", "sumw", "farw")}

    def add(key, inp, out):
        cases[key][0].append(inp)
        cases[key][1].extend(out)

    for _ in range(1500):
        n, base = rng.randint(2, 14), rng.randint(0, 1)
        edges = random_tree(rng, n, base)
        wedges = [e + [rng.randint(-5, 9)] for e in edges]
        size, nodes = n + base, list(range(base, base + n))
        root = rng.choice(nodes)
        adj, wadj = adjacency(edges, size), adjacency(wedges, size)
        want = [[v for v, _ in c] for c in rooted(adj, root, size)]
        same(f"edgeListToTree.py {edges} root {root}", [sorted(c) for c in plain(edges, root)], want)
        wwant = rooted(wadj, root, size)
        same(f"weightedEdgeListToTree.py {wedges} root {root}", [sorted(c) for c in weighted(wedges, root)], wwant)
        cents = centroids(adj, nodes)
        same(f"findCentroids.py {edges}", find(edges), cents)
        add("tree", f"{edge_text(edges)} {root}", [" ".join(map(str, c)) for c in want])
        add("wtree", f"{edge_text(wedges)} {root}", [" ".join(f"{v}:{w}" for v, w in c) for c in wwant])
        add("cent", edge_text(edges), [" ".join(map(str, cents))])
        for name, es, a, sum_fn, far_fn, s_key, f_key in (("", edges, adj, sum_py, far_py, "sum", "far"),
                                                          (".weighted", wedges, wadj, sumw_py, farw_py, "sumw", "farw")):
            sums, far = [-1] * size, [(-1, -1)] * size
            for u in nodes:
                d = distances(a, u)
                sums[u] = sum(d.values())
                far[u] = max(((d[v], -v) for v in nodes if v != u))
                far[u] = (far[u][0], -far[u][1])
            same(f"SumOfDistances{name}.py {es}", list(sum_fn(es)), sums)
            same(f"FarthestNode{name}.py {es}", [tuple(x) for x in far_fn(es)], far)
            add(s_key, edge_text(es), [" ".join(map(str, sums))])
            add(f_key, edge_text(es), [" ".join(f"{x}:{y}" for x, y in far)])

    pair_edges = "int m; while (cin >> m) { vector<pair<int, int>> e(m); for (auto& [a, b] : e) cin >> a >> b; "
    tri_edges = "int m; while (cin >> m) { vector<array<int, 3>> e(m); for (auto& [a, b, w] : e) cin >> a >> b >> w; "
    vec_edges = "int m, W = WEIGHTS; while (cin >> m) { vector<vector<int>> e(m, vector<int>(2 + W)); for (auto& x : e) for (int& y : x) cin >> y; "
    print_lists = "int root; cin >> root; auto r = edgeListToTree(e, root); for (auto c : r) { sort(c.begin(), c.end()); for (size_t i = 0; i < c.size(); i++) "
    run_cpp("trees/edgeListToTree", "trees/edgeListToTree.cpp", pair_edges + print_lists + "cout << (i ? \" \" : \"\") << c[i]; cout << '\\n'; } }", "\n".join(cases["tree"][0]), cases["tree"][1])
    run_cpp("trees/weightedEdgeListToTree", "trees/weightedEdgeListToTree.cpp", tri_edges + print_lists + "cout << (i ? \" \" : \"\") << c[i].first << ':' << c[i].second; cout << '\\n'; } }", "\n".join(cases["wtree"][0]), cases["wtree"][1])
    run_cpp("trees/findCentroids", "trees/findCentroids.cpp", pair_edges + "auto r = findCentroids(e); for (size_t i = 0; i < r.size(); i++) cout << (i ? \" \" : \"\") << r[i]; cout << '\\n'; }", "\n".join(cases["cent"][0]), cases["cent"][1])
    sums = "auto r = sumOfDistances(e); for (size_t i = 0; i < r.size(); i++) cout << (i ? \" \" : \"\") << r[i]; cout << '\\n'; }"
    fars = "auto r = farthestNodes(e); for (size_t i = 0; i < r.size(); i++) cout << (i ? \" \" : \"\") << r[i].first << ':' << r[i].second; cout << '\\n'; }"
    for file, key, tail, weights in (("SumOfDistances", "sum", sums, 0), ("FarthestNode", "far", fars, 0),
                                     ("SumOfDistances.weighted", "sumw", sums, 1), ("FarthestNode.weighted", "farw", fars, 1)):
        run_cpp(f"reroot/{file}", f"reroot/{file}.cpp", vec_edges.replace("WEIGHTS", str(weights)) + tail, "\n".join(cases[key][0]), cases[key][1])


# ---- bitset ----

def test_bitset():
    rng = random.Random(2)
    stdin, want = [], []
    for _ in range(400):
        n = rng.choice((0, 1, 5, 63, 64, 65, 127, 128, 129, 200))
        bits = [0] * n
        stdin.append(f"new {n}")
        for _ in range(60):
            op = rng.choice(("set", "unset", "toggle", "rangeSet", "rangeUnset", "rangeToggle", "append", "pop", "shl", "shr", "query"))
            if op == "append":
                b = rng.randint(0, 1)
                bits.append(b)
                stdin.append(f"append {b}")
            elif op == "pop":
                if bits:
                    want.append(str(bits.pop()))
                    stdin.append("pop")
                    want.append("".join(map(str, bits)))
                continue
            elif op in ("shl", "shr"):
                k = rng.randint(0, len(bits) + 3)
                stdin.append(f"{op} {k}")
                if op == "shl":
                    bits = ([0] * k + bits)[:len(bits)]
                else:
                    bits = (bits[k:] + [0] * k)[:len(bits)]
            elif not bits:
                continue
            elif op in ("set", "unset", "toggle"):
                i = rng.randrange(len(bits))
                bits[i] = {"set": 1, "unset": 0, "toggle": 1 - bits[i]}[op]
                stdin.append(f"{op} {i}")
            elif op == "query":
                i = rng.randint(-1, len(bits) - 1)
                j = rng.randint(0, len(bits))
                nxt = next((x for x in range(i + 1, len(bits)) if bits[x]), -1)
                prv = next((x for x in range(j - 1, -1, -1) if bits[x]), -1)
                nz = next((x for x in range(i + 1, len(bits)) if not bits[x]), -1)
                pz = next((x for x in range(j - 1, -1, -1) if not bits[x]), -1)
                stdin.append(f"query {i} {j}")
                want.append(f"{nxt} {prv} {nz} {pz} {sum(bits)}")
                continue
            else:
                l = rng.randrange(len(bits))
                r = rng.randrange(l, len(bits))
                for x in range(l, r + 1):
                    bits[x] = {"rangeSet": 1, "rangeUnset": 0, "rangeToggle": 1 - bits[x]}[op]
                stdin.append(f"{op} {l} {r}")
                stdin.append(f"count {l} {r}")
                want.append(str(sum(bits[l : r + 1])))
            want.append("".join(map(str, bits)))
    body = """
    string op; DynamicBitset b;
    while (cin >> op) {
        int x, y;
        if (op == "new") { cin >> x; b = DynamicBitset(x); continue; }
        if (op == "count") { cin >> x >> y; cout << b.countOnesInRange(x, y) << '\\n'; continue; }
        if (op == "query") {
            cin >> x >> y;
            cout << b.nextOneAfter(x) << ' ' << b.prevOneBefore(y) << ' ' << b.nextZeroAfter(x) << ' ' << b.prevZeroBefore(y)
                 << ' ' << b.countOnes() << '\\n';
            continue;
        }
        if (op == "pop") { cout << b.popBit() << '\\n'; cout << b.toString() << '\\n'; continue; }
        cin >> x;
        if (op == "append") b.appendBit(x);
        else if (op == "shl") b <<= x;
        else if (op == "shr") b >>= x;
        else if (op == "set") b.set(x);
        else if (op == "unset") b.unset(x);
        else if (op == "toggle") b.toggle(x);
        else {
            cin >> y;
            if (op == "rangeSet") b.rangeSet(x, y);
            else if (op == "rangeUnset") b.rangeUnset(x, y);
            else b.rangeToggle(x, y);
        }
        if (op.rfind("range", 0) != 0) cout << b.toString() << '\\n';
        else { cout << b.countOnesInRange(x, y) << '\\n'; cin >> op >> x >> y; cout << b.toString() << '\\n'; }
    }"""
    # a range op is followed by its "count l r" line, so the C++ prints the count first, then the bits
    run_cpp("bitset/DynamicBitset", "bitset/DynamicBitset.cpp", body, "\n".join(stdin) + "\n", want)


if __name__ == "__main__":
    for test in (test_modcalc, test_fibonacci, test_next_permutation, test_trees_and_reroot, test_bitset):
        before = len(failures)
        test()
        print(f"{'FAIL' if len(failures) > before else 'PASS'}  {test.__name__}", flush=True)
    for line in failures[:20]:
        print(line)
    print(f"{len(failures)} failures" if failures else "all misc templates agree with the brute force")
    sys.exit(1 if failures else 0)
