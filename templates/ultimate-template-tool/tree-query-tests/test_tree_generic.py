"""Every commented example of the generic tree templates (generic-trees/), switched on, against a plain fold.

For each file the examples in its fill-in section are uncommented, random trees are built and a random script of the
file's ops is replayed on each. Every answer is compared with the same data folded one node (or edge) at a time along
the path, by Python stand-ins for the example (Mirror). The test also checks what the template hands to the leaf
functions: a node's own label, and an edge's two ends with the upper one first.

    python3 test_tree_generic.py                    # every file, both languages
    python3 test_tree_generic.py --py               # the Python files only (--cpp: the C++ files only)
    python3 test_tree_generic.py GenericLazyTree    # only the files whose name starts with this
"""
import hashlib
import os
import random
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import test_tree as TT  # noqa: E402
import test_tree_shape as TS  # noqa: E402
from find_compiler import cxx, sanitize_flags  # noqa: E402

DIR = os.path.join(os.path.dirname(HERE), "generic-trees")
A = ord("a")


def parse(name):
    """(kind, lazy, rev, level, ext) of a file name like GenericLazyTreeBoth.simple.norev.cpp."""
    parts = name.split(".")
    level = next((p for p in parts[1:-1] if p in ("simple", "complex")), "basic")
    return parts[0].split("Tree")[1], "Lazy" in parts[0], "norev" not in parts, level, parts[-1]


def fill(text, ext):
    """The file with every commented example switched on."""
    if ext == "py":
        cut = re.search(r"^class ", text, re.M).start()
        head = re.sub(r"^( +)# (?!This is NOT)(.*)$", r"\1\2", text[:cut], flags=re.M)
        return re.sub(r"^    pass\n", "", head, flags=re.M) + text[cut:]
    start = text.index("// WHAT YOU FILL IN")
    cut = min(i for i in (text.find("// A segment tree with no identity"), text.find("// A lazy segment tree with no")) if i > 0)
    return text[:start] + re.sub(r"^( +)// (?!This is NOT)(.*)$", r"\1\2", text[start:cut], flags=re.M) + text[cut:]


class Mirror:
    """Python stand-ins for one example: what a value is as data, how two join, a stretch read backwards, a tag applied;
    how the C++ driver prints the data; and how it reads a value and a tag from numbers."""

    def __init__(self, level, rev, lazy):
        self.level, self.rev, self.lazy = level, rev, lazy

    def val(self, rng):
        return rng.randrange(A, A + 26) if self.level == "complex" else rng.randint(-50, 50)

    def tag(self, rng):
        """A tag as the numbers sent to the driver."""
        if self.level != "complex":
            return [rng.randint(-9, 9)]
        return [int(rng.random() < 0.4), rng.randrange(A, A + 26), rng.randrange(26) if rng.random() < 0.6 else 0]

    def leaf(self, x):
        if self.level == "simple":
            return (x, x) if self.rev else x
        if self.level == "basic":
            return (x, x, x, 1) if self.rev else (x, x, 1) if self.lazy else (x, x)
        cnt = tuple(int(c == x - A) for c in range(26))
        return (cnt, x, x, 1) if self.rev else (cnt, 1)

    def combine(self, l, r):
        if self.level == "simple":
            return (l[0], r[1]) if self.rev else max(l, r)
        if self.level == "basic":
            if self.rev:
                return (l[0] + r[0], l[1], r[2], l[3] + r[3])
            return (l[0] + r[0], min(l[1], r[1])) + ((l[2] + r[2],) if self.lazy else ())
        cnt = tuple(x + y for x, y in zip(l[0], r[0]))
        return (cnt, l[1], r[2], l[3] + r[3]) if self.rev else (cnt, l[1] + r[1])

    def reverse(self, d):
        if self.level == "simple":
            return (d[1], d[0])
        if self.level == "basic":
            return (d[0], d[2], d[1], d[3])
        return (d[0], d[2], d[1], d[3])

    def apply(self, d, tag):
        if self.level == "simple":
            return (d[0] + tag[0], d[1] + tag[0]) if self.rev else d + tag[0]
        if self.level == "basic":
            t = tag[0]
            return (d[0] + t * d[3], d[1] + t, d[2] + t, d[3]) if self.rev else (d[0] + t * d[2], d[1] + t, d[2])
        assign, letter, shift = tag
        cnt, n = list(d[0]), d[-1]
        first, last = (d[1], d[2]) if self.rev else (A, A)
        if assign:
            cnt = [0] * 26
            cnt[letter - A] = n
            first = last = letter
        if shift:
            cnt = [cnt[(c - shift) % 26] for c in range(26)]
            first, last = A + (first - A + shift) % 26, A + (last - A + shift) % 26
        return (tuple(cnt), first, last, n) if self.rev else (tuple(cnt), n)

    def show(self, d):
        if self.level == "simple":
            return f"{d[0]} {d[1]}" if self.rev else str(d)
        if self.level == "basic":
            return " ".join(map(str, d))
        return " ".join(map(str, list(d[0]) + list(d[1:])))

    def cpp(self, t):
        """C++ helpers for target t ("node" / "edge"): show, toVal, toTag."""
        T = t.capitalize()
        if self.level == "simple":
            show = 'return to_string(d.first) + " " + to_string(d.second);' if self.rev else "return to_string(d);"
            tag = f"return ({T}Tag)a[0];"
        elif self.level == "basic":
            fields = ["tot", "first", "last", "len"] if self.rev else ["tot", "mn"] + (["len"] if self.lazy else [])
            show = "return " + ' + " " + '.join(f"to_string(d.{f})" for f in fields) + ";"
            tag = f"{T}Tag t; t.add = a[0]; return t;"
        else:
            ends = ' s += " " + to_string((int)d.first) + " " + to_string((int)d.last);' if self.rev else ""
            show = ('string s; for (int c = 0; c < 26; c++) s += (c ? " " : "") + to_string(d.cnt[c]);' + ends
                    + ' return s + " " + to_string(d.len);')
            tag = f"{T}Tag t; t.assign = a[0] != 0; t.letter = (char)a[1]; t.shift = (int)a[2]; return t;"
        out = [f"string show{T}(const {T}Data& d) {{ {show} }}", f"{T}Val to{T}Val(long long x) {{ return ({T}Val)x; }}"]
        if self.lazy:
            out.append(f"{T}Tag to{T}Tag(const long long* a) {{ {tag} }}")
        return out


# ---------------------------------------------------------------- trials

def plain_tree(edges, root, lo):
    """par, dep and children by label, for the brute force."""
    n = len(edges) + 1
    hi = lo + n - 1
    adj = {v: [] for v in range(lo, hi + 1)}
    for e in edges:
        adj[e[0]].append(e[1])
        adj[e[1]].append(e[0])
    par, dep, bfs = {root: -1}, {root: 0}, [root]
    for v in bfs:
        for u in adj[v]:
            if u not in par:
                par[u], dep[u] = v, dep[v] + 1
                bfs.append(u)
    return par, dep, bfs


def path_nodes(par, dep, a, b):
    up, down = [], []
    while a != b:
        if dep[a] >= dep[b]:
            up.append(a)
            a = par[a]
        else:
            down.append(b)
            b = par[b]
    return up + [a] + down[::-1]


def make_trials(name, count):
    """[(edges, root, lo, vals, [(op, args)])]: op is "!name" when the call must raise."""
    kind, lazy, rev, level, _ = parse(name)
    M = Mirror(level, rev, lazy)
    targets = {"Nodes": ["node"], "Edges": ["edge"], "Both": ["node", "edge"]}[kind]
    trials = []
    for t in range(count):
        rng = random.Random(int(hashlib.md5(f"{name.rsplit('.', 1)[0]}/{t}".encode()).hexdigest()[:8], 16))
        n = rng.choice((1, 2, 3, 5, 8, 13, 20, 30, 45, 60))
        if t % 3 == 2:  # chains nested in chains: a path crosses many pieces, each with two or more nodes
            edges, root, lo = TT.nested_tree(rng.choice((30, 45, 60)), rng)
        else:
            edges, root, lo = TS.make_tree(n, rng.choice(TS.SHAPES), rng)
        n = len(edges) + 1
        hi = lo + n - 1
        if "edge" in targets:  # every edge carries its weight (a nodes-only file takes edges with or without one)
            edges = [[e[0], e[1], M.val(rng)] for e in edges]
        vals = [M.val(rng) for _ in range(hi + 1)]
        par, dep, bfs = plain_tree(edges, root, lo)
        kids = {v: 0 for v in bfs}
        for v in bfs[1:]:
            kids[par[v]] += 1
        leaves = [v for v in bfs if kids[v] == 0]

        def node():
            return rng.randrange(lo, hi + 1)

        def ends():
            return [rng.choice(leaves) if rng.random() < 0.5 else node() for _ in range(2)]

        seq = []
        for _ in range(rng.randint(30, 60)):
            tg = rng.choice(targets)
            names = ["Get", "Assign", "PathQuery", "PathQuery", "SubtreeQuery"] + (["Update", "PathUpdate", "PathUpdate", "SubtreeUpdate"] if lazy else [])
            what = rng.choice(names)
            op = tg + what
            tag = M.tag(rng) if what.endswith("Update") else []
            if rng.random() < 0.03:  # a label that is not in the tree
                bad = rng.choice((lo - 1, hi + 1, hi + 7))
                args = [bad, node()][:2 if (what.startswith("Path") or (tg == "edge" and what in ("Get", "Assign", "Update"))) else 1]
                rng.shuffle(args)
                seq.append(("!" + op, args + ([M.val(rng)] if what == "Assign" else []) + tag))
                continue
            if what.startswith("Path"):
                a, b = ends()
                if rng.random() < 0.08:
                    b = a
                seq.append((("!" if tg == "edge" and what == "PathQuery" and a == b else "") + op, [a, b] + tag))
            elif what.startswith("Subtree"):
                v = node()
                seq.append((("!" if tg == "edge" and what == "SubtreeQuery" and kids[v] == 0 else "") + op, [v] + tag))
            elif tg == "node":
                seq.append((op, [node()] + ([M.val(rng)] if what == "Assign" else []) + tag))
            elif n > 1:
                v = rng.choice(bfs[1:])  # an edge: a node and its parent, in either order
                pair, must_raise = [v, par[v]], False
                if rng.random() < 0.06:  # two nodes with no edge between them
                    u = node()
                    if par[u] != v and par[v] != u:
                        pair, must_raise = [v, u], True
                rng.shuffle(pair)
                seq.append((("!" if must_raise else "") + op, pair + ([M.val(rng)] if what == "Assign" else []) + tag))
            if rng.random() < 0.05:
                seq.append(("lca", ends()))
        trials.append((edges, root, lo, vals, seq))
    return trials


def expected(name, trial, order):
    """What every answering call of the trial must print, given the template's own position order (for subtrees)."""
    kind, lazy, rev, level, _ = parse(name)
    M = Mirror(level, rev, lazy)
    edges, root, lo, vals, seq = trial
    par, dep, bfs = plain_tree(edges, root, lo)
    pos = {v: i for i, v in enumerate(order)}
    sz = {v: 1 for v in bfs}
    for v in reversed(bfs[1:]):
        sz[par[v]] += sz[v]
    nd = {v: M.leaf(vals[v]) for v in bfs}
    ed = {}
    for e in edges:
        if len(e) == 3:
            ed[e[0] if par[e[0]] == e[1] else e[1]] = M.leaf(e[2])

    def fold(items):
        res = items[0]
        for x in items[1:]:
            res = M.combine(res, x)
        return res

    out = []
    for op, args in seq:
        if op.startswith("!"):
            out.append("raised")
            continue
        if op == "lca":
            path = path_nodes(par, dep, *args)
            out.append(str(min(path, key=lambda v: dep[v])))
            continue
        held, what = (nd, op[4:]) if op.startswith("node") else (ed, op[4:])
        edge = op.startswith("edge")
        if what in ("Get", "Assign", "Update"):
            key = (args[0] if par[args[0]] == args[1] else args[1]) if edge else args[0]
            rest = args[2 if edge else 1:]
            if what == "Get":
                out.append(M.show(held[key]))
            elif what == "Assign":
                held[key] = M.leaf(rest[0])
            else:
                held[key] = M.apply(held[key], rest)
            continue
        if what.startswith("Path"):
            keys = path_nodes(par, dep, args[0], args[1])
            if edge:  # each edge by its lower end: the lca has none on this path
                top = min(keys, key=lambda v: dep[v])
                keys = [v for v in keys if v != top]
            rest = args[2:]
        else:
            l = pos[args[0]]
            keys = [order[i] for i in range(l + (1 if edge else 0), l + sz[args[0]])]
            rest = args[1:]
        if what.endswith("Query"):
            out.append(M.show(fold([held[k] for k in keys])))
        else:
            for k in keys:
                held[k] = M.apply(held[k], rest)
    return out


# ---------------------------------------------------------------- Python

def run_py(name, text, trials):
    """[(order, answers)] for every trial."""
    kind, lazy, rev, level, _ = parse(name)
    M = Mirror(level, rev, lazy)
    ns = {}
    exec(compile(fill(text, "py"), name, "exec"), ns)
    logs = {}
    for t in ("node", "edge"):  # (what the template hands to the leaf functions)
        if t + "Leaf" in ns:
            logs[t] = []
            ns[t + "Leaf"] = (lambda fn, log: lambda *a: (log.append(a), fn(*a))[1])(ns[t + "Leaf"], logs[t])
    out = []
    for edges, root, lo, vals, seq in trials:
        par, dep, bfs = plain_tree(edges, root, lo)
        for log in logs.values():
            log.clear()
        tree = ns["Tree"](edges, root) if kind == "Edges" else ns["Tree"](edges, root, vals)
        above = {(e[0] if par[e[0]] == e[1] else e[1]): e[2] for e in edges if len(e) == 3}
        if "node" in logs:
            assert sorted(logs["node"]) == sorted((vals[v], v) for v in bfs), "nodeLeaf was not handed each value with its node"
        if "edge" in logs:
            assert sorted(logs["edge"]) == sorted((above[v], par[v], v) for v in bfs[1:]), \
                "edgeLeaf was not handed each weight with its two ends (the upper one first)"
        got = []
        for op, args in seq:
            bad = op.startswith("!")
            fn = getattr(tree, op.lstrip("!"))
            try:
                res = fn(*args[:2], args[2]) if len(args) == 3 else fn(*args)
            except IndexError:
                got.append("raised" if bad else "raised (it should not have)")
                continue
            if bad:
                got.append("no error")
            elif op == "lca":
                got.append(str(res))
            elif op.endswith(("Get", "Query")):
                got.append(M.show(res))
            elif op.endswith("Assign"):
                want = (args[1], args[0]) if op == "nodeAssign" else \
                    (args[2],) + ((args[1], args[0]) if par[args[0]] == args[1] else (args[0], args[1]))
                assert logs[op[:4]][-1] == want, f"{op}{tuple(args)}: {op[:4]}Leaf was handed {logs[op[:4]][-1]}"
        out.append((list(tree.order), got))
    return out


# ---------------------------------------------------------------- C++

def cpp_driver(name, text):
    kind, lazy, rev, level, _ = parse(name)
    M = Mirror(level, rev, lazy)
    targets = {"Nodes": ["node"], "Edges": ["edge"], "Both": ["node", "edge"]}[kind]
    code = fill(text, "cpp")
    # every call of a leaf function is written down, to check what the template hands it
    code = code.replace("using ll = long long;\n", "using ll = long long;\nvector<array<long long, 3>> leafLog[2];\n", 1)
    sig = "NodeData nodeLeaf(const NodeVal& v, int node) {\n"
    if "node" in targets:
        assert code.count(sig) == 1
        code = code.replace(sig, sig + "    leafLog[0].push_back({(long long)v, node, -1});\n")
    sig = "EdgeData edgeLeaf(const EdgeVal& w, int a, int b) {\n"
    if "edge" in targets:
        assert code.count(sig) == 1
        code = code.replace(sig, sig + "    leafLog[1].push_back({(long long)w, a, b});\n")
    lines = [code, *[h for t in targets for h in M.cpp(t)], "int main() {",
             "  int cases; cin >> cases;",
             "  while (cases--) {",
             "    int n, lo, root; cin >> n >> lo >> root;",
             "    int hi = lo + n - 1;",
             "    vector<vector<long long>> edges(n - 1);",
             "    for (auto& e : edges) { int len; cin >> len; e.resize(len); for (auto& x : e) cin >> x; }",
             "    vector<long long> raw(hi + 1), par(hi + 1), above(hi + 1);",
             "    for (auto& x : raw) cin >> x;",
             "    for (auto& x : par) cin >> x;",
             "    for (auto& x : above) cin >> x;",
             "    leafLog[0].clear(), leafLog[1].clear();"]
    if "node" in targets:
        lines += ["    vector<NodeVal> vals(hi + 1);", "    for (int i = 0; i <= hi; i++) vals[i] = toNodeVal(raw[i]);",
                  "    Tree t(edges, root, vals);",
                  "    { vector<array<long long, 3>> want;",
                  "      for (int v = lo; v <= hi; v++) want.push_back({raw[v], v, -1});",
                  "      sort(want.begin(), want.end()); auto got = leafLog[0]; sort(got.begin(), got.end());",
                  '      if (got != want) { cerr << "nodeLeaf was not handed each value with its node\\n"; return 3; } }']
    else:
        lines += ["    Tree t(edges, root);"]
    if "edge" in targets:
        lines += ["    { vector<array<long long, 3>> want;",
                  "      for (int v = lo; v <= hi; v++) if (v != root) want.push_back({(long long)toEdgeVal(above[v]), par[v], v});",
                  "      sort(want.begin(), want.end()); auto got = leafLog[1]; sort(got.begin(), got.end());",
                  '      if (got != want) { cerr << "edgeLeaf was not handed each weight with its two ends\\n"; return 3; } }']
    lines += ['    cout << "order";', "    for (int i = 0; i < n; i++) cout << ' ' << t.order[i];", "    cout << '\\n';",
              "    int q; cin >> q;",
              "    while (q--) {",
              "      string op; cin >> op;",
              "      bool bad = op[0] == '!';",
              "      if (bad) op = op.substr(1);",
              "      long long a[8] = {0, 0, 0, 0, 0, 0, 0, 0};",
              "      int cnt; cin >> cnt; for (int i = 0; i < cnt; i++) cin >> a[i];",
              "      try {",
              '      if (op == "lca") { cout << t.lca(a[0], a[1]) << \'\\n\'; }']
    for tg in targets:
        T, edge = tg.capitalize(), tg == "edge"
        one = "a[0], a[1]" if edge else "a[0]"
        k = 2 if edge else 1  # (where an op's value or tag starts, after the node / the edge's two ends)
        lines.append(f'      else if (op == "{tg}Get") {{ auto r = t.{tg}Get({one}); if (!bad) cout << show{T}(r) << \'\\n\'; }}')
        check = ("int c = par[a[0]] == a[1] ? a[0] : a[1]; array<long long, 3> want = {(long long)toEdgeVal(a[2]), par[c], c};"
                 if edge else "array<long long, 3> want = {(long long)toNodeVal(a[1]), a[0], -1};")
        lines.append(f'      else if (op == "{tg}Assign") {{ t.{tg}Assign({one}, to{T}Val(a[{k}])); if (!bad) {{ {check} '
                     f'if (leafLog[{int(edge)}].back() != want) {{ cerr << "{tg}Assign: {tg}Leaf was handed the wrong thing\\n"; return 3; }} }} }}')
        lines.append(f'      else if (op == "{tg}PathQuery") {{ auto r = t.{tg}PathQuery(a[0], a[1]); if (!bad) cout << show{T}(r) << \'\\n\'; }}')
        lines.append(f'      else if (op == "{tg}SubtreeQuery") {{ auto r = t.{tg}SubtreeQuery(a[0]); if (!bad) cout << show{T}(r) << \'\\n\'; }}')
        if lazy:
            lines.append(f'      else if (op == "{tg}Update") {{ t.{tg}Update({one}, to{T}Tag(a + {k})); }}')
            lines.append(f'      else if (op == "{tg}PathUpdate") {{ t.{tg}PathUpdate(a[0], a[1], to{T}Tag(a + 2)); }}')
            lines.append(f'      else if (op == "{tg}SubtreeUpdate") {{ t.{tg}SubtreeUpdate(a[0], to{T}Tag(a + 1)); }}')
    lines += ["      else { cerr << \"unknown op \" << op << '\\n'; return 1; }",
              "      if (bad) cout << \"no error\\n\";",
              "      } catch (const out_of_range&) { cout << (bad ? \"raised\\n\" : \"raised (it should not have)\\n\"); }",
              "    }", "  }", "}"]
    return "\n".join(lines) + "\n"


def run_cpp(name, text, trials):
    os.makedirs(TT.BUILD, exist_ok=True)
    src = os.path.join(TT.BUILD, "generic-" + name.replace(".", "-") + ".cpp")
    exe = src[:-4]
    open(src, "w").write(cpp_driver(name, text))
    comp = subprocess.run([cxx(), "-std=c++17", "-O2", "-Wall", *sanitize_flags(), "-o", exe, src], capture_output=True, text=True)
    if comp.returncode:
        raise RuntimeError("compile error:\n" + comp.stderr[:2500])
    if comp.stderr.strip():
        raise RuntimeError("compiler warnings:\n" + comp.stderr[:1500])
    inp = [str(len(trials))]
    for edges, root, lo, vals, seq in trials:
        n = len(edges) + 1
        par, dep, bfs = plain_tree(edges, root, lo)
        above = {(e[0] if par[e[0]] == e[1] else e[1]): e[2] for e in edges if len(e) == 3}
        inp.append(f"{n} {lo} {root}")
        inp += [" ".join(map(str, [len(e)] + list(e))) for e in edges]
        inp.append(" ".join(map(str, vals)))
        inp.append(" ".join(str(par.get(v, 0)) for v in range(lo + n)))
        inp.append(" ".join(str(above.get(v, 0)) for v in range(lo + n)))
        inp.append(str(len(seq)))
        inp += [" ".join(map(str, [op, len(args)] + args)) for op, args in seq]
    run = subprocess.run([exe], input="\n".join(inp) + "\n", capture_output=True, text=True, timeout=300)
    for path in (src, exe):
        os.remove(path)
    if run.returncode:
        raise RuntimeError(f"binary exited {run.returncode}: {run.stderr[:500]}")
    lines, out, at = run.stdout.split("\n"), [], 0
    for edges, root, lo, vals, seq in trials:
        order = list(map(int, lines[at].split()[1:]))
        answering = sum(op.startswith("!") or op == "lca" or op.endswith(("Get", "Query")) for op, _ in seq)
        out.append((order, lines[at + 1:at + 1 + answering]))
        at += 1 + answering
    return out


# ---------------------------------------------------------------- one file

def mismatch(name, trials, results):
    """None, or what the first wrong answer was."""
    for k, (trial, (order, got)) in enumerate(zip(trials, results)):
        exp = expected(name, trial, order)
        answering = [(op, args) for op, args in trial[4] if op.startswith("!") or op == "lca" or op.endswith(("Get", "Query"))]
        if len(got) != len(exp):
            return f"trial {k}: {len(got)} answers, expected {len(exp)}"
        for (op, args), g, e in zip(answering, got, exp):
            if g != e:
                return f"trial {k} ({len(trial[0]) + 1} nodes): {op}{tuple(args)} gave {g!r}, expected {e!r}"
    return None


def test_file(name, trials_n=40):
    text = open(os.path.join(DIR, name), encoding="utf-8").read()
    try:
        trials = make_trials(name, trials_n)
        results = (run_py if name.endswith(".py") else run_cpp)(name, text, trials)
        bad = mismatch(name, trials, results)
    except Exception as e:  # noqa: BLE001
        bad = f"{type(e).__name__}: {str(e)[:1500]}"
    answers = sum(len(r[1]) for r in results) if not bad else 0
    return f"FAIL  {name}: {bad}" if bad else f"PASS  {name}: {answers} answers"


def main():
    args = sys.argv[1:]
    exts = tuple(e for e, flag in ((".py", "--cpp"), (".cpp", "--py")) if flag not in args)
    prefixes = [a for a in args if not a.startswith("--")]
    names = sorted(f for f in os.listdir(DIR) if f.endswith(exts) and (not prefixes or f.startswith(tuple(prefixes))))
    fails = 0
    for name in names:
        line = test_file(name)
        fails += line.startswith("FAIL")
        print(line, flush=True)
    print(f"{'FAIL' if fails else 'PASS'}  generic tree templates: {len(names)} files, {fails} failures")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
