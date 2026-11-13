"""Tests the tree templates that hold values (tree-queries/node-*, edge-* and both-*) against a brute force.

The brute force is a plain tree: a value per node, every path walked node by node through parent pointers, every
subtree listed. What an op means on a list of values comes from the range-query tests (range-query-tests/
test_templates.py: BRUTE_QUERIES, brute_update, and domain() for the values each range template allows), so a tree op
is checked as "collect the values along the path (or in the subtree), ask the range brute force". Nothing here knows
about heavy-light decomposition. For an edge template the values are the weights of the path's (or the subtree's)
edges, each edge kept under its lower end; what a query answers with no edges at all is listed in NO_EDGES.

Random op scripts run on template.py and are compared with the brute force; the same scripts then go to
template.cpp (built from a generated driver), which has to print the same. Both labelings (0..n-1 and 1..n), six tree
shapes, a few shape ops per script, and calls with a node that is not in the tree (must raise).

    python3 test_tree.py                 # every folder, both languages
    python3 test_tree.py --py            # Python only
    python3 test_tree.py --cpp           # C++ only
    python3 test_tree.py rangeAdd beats  # folders whose name contains one of these
    python3 test_tree.py --shard 3/8     # every 8th folder from the 3rd (run 8 side by side)
    python3 test_tree.py --trials 60     # more random trees per folder (default 24)
    python3 test_tree.py --from f.txt    # exactly the folders listed in f.txt (one per line)
"""
import hashlib
import os
import random
import re
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DIR = os.path.join(ROOT, "tree-queries")
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "range-query-tests"))
import gen_tree as G  # noqa: E402
import test_templates as RT  # noqa: E402
import test_tree_shape as TS  # noqa: E402
from find_compiler import cxx, sanitize_flags  # noqa: E402

BUILD = os.path.join(tempfile.gettempdir(), "tree-query-template-tests")
OPS_PER_TRIAL = 45
SHAPE_OPS = [op for op in TS.OPS if op != "pathNodes"]  # (a few per script: they must still work beside the values)


def op_table(target="node"):
    """tree op -> (where, how the brute force answers it, the range op that says what it means, extra arg count)."""
    t = {}
    for suffix, rop, args, _ in G.POINT:
        t[target + suffix] = ("one", "get" if suffix == "Get" else "update", rop, len(args))
    for suffix, rop, args, _ in G.UPDATES:
        t[f"{target}Path{suffix}"] = ("path", "update", rop, len(args))
        t[f"{target}Subtree{suffix}"] = ("subtree", "update", rop, len(args))
    for suffix, rop in (("AddArithSeq", "rangeAddArithSeq"), ("AddArithSeqMod", "rangeAddArithSeqMod")):
        t[f"{target}Path{suffix}"] = ("path", "update", rop, 2)
    for suffix, rop, args, fold, _ in G.QUERIES:
        t[f"{target}Subtree{suffix}"] = ("subtree", "query", rop, len(args))
        if fold and suffix not in G.SUBTREE_ONLY:
            t[f"{target}Path{suffix}"] = ("path", "query", rop, len(args))
    for table in (G.SEARCHES, G.PREFIX_SEARCHES):
        prefix = table is G.PREFIX_SEARCHES
        for suffix, _, left, right in table:
            first, last = ("FirstPrefixSum", "LastSuffixSum") if prefix else ("First", "Last")
            t[f"{target}Path{first}{suffix}"] = ("path", "find", left, 1)
            t[f"{target}Path{last}{suffix}"] = ("path", "find", right, 1)
            if not prefix:
                t[f"{target}NearestAncestor{suffix}"] = ("up", "find", left, 1)
    for big in ("Max", "Min"):
        t[f"{target}Path{big}PrefixSum"] = ("path", "query", f"{big.lower()}PrefixSum", 0)
        t[f"{target}Path{big}SuffixSum"] = ("path", "query", f"{big.lower()}SuffixSum", 0)
    return t


TABLE = {**op_table("node"), **op_table("edge")}


def is_edge(op):
    return op.lstrip("!").startswith("edge")


def node_count(op):
    """How many nodes op takes before its other arguments (an edge is named by its two ends)."""
    where = TABLE[op.lstrip("!")][0]
    return 2 if where == "path" or (where == "one" and is_edge(op)) else 1


# What an edge query must answer when there are no edges to look at (a path a..a, a leaf's subtree), by the op's name
# after "edgePath" / "edgeSubtree". "raise": it must raise; +inf / -inf are the largest / smallest value in C++.
NO_EDGES = {}
for _name in ("Sum", "SumMod", "Gcd", "XOR", "OR", "CountLtX", "CountLteX", "CountGtX", "CountGteX", "CountInValRange", "SumLtX",
              "SumLteX", "SumGtX", "SumGteX", "SumInValRange", "SumAbsDiffToX", "CountOccurrences", "CountDistinct", "Mex"):
    NO_EDGES[_name] = 0
for _name in ("Min", "MinXorAgainstX", "MinPrefixSum", "MinSuffixSum"):
    NO_EDGES[_name] = ("+inf",)
for _name in ("Max", "MaxXorAgainstX", "MaxPrefixSum", "MaxSuffixSum"):
    NO_EDGES[_name] = ("-inf",)
for _name in ("SmallestGteX", "SmallestGtX", "LargestLteX", "LargestLtX"):
    NO_EDGES[_name] = None
for _name in ("AllDistinct", "AllEvenFrequency"):
    NO_EDGES[_name] = True
NO_EDGES["AND"] = -1
for _name in ("KthSmallest", "KthLargest", "SumSmallestK", "SumLargestK", "SumKthSmallestRange", "SumKthLargestRange",
              "SumAbsDiffToMedian", "Mode"):
    NO_EDGES[_name] = "raise"


def no_edges(op):
    return NO_EDGES[re.sub(r"^edge(Path|Subtree)", "", op)]
# range ops that need every value >= 0, and the range ops whose presence already keeps a template's values >= 0
NONNEG_SEARCHES = {"leftmostPrefixSumGteX", "leftmostPrefixSumGtX", "rightmostSuffixSumGteX", "rightmostSuffixSumGtX"}
KEEPS_NONNEG = {"rangeAndApply", "rangeOrApply", "rangeXorApply", "rangeAndQuery", "rangeOrQuery", "rangeXorQuery", "rangeGcd",
                "rangeMod", "rangeFloorSqrt", "rangeFloorDiv", "lcmAll"} | RT.MOD_OPS


def read_ops(folder):
    text = open(os.path.join(DIR, folder, "template.py"), encoding="utf-8").read()
    ops = re.search(r"^# @operations: (.*)$", text, re.M).group(1).split()
    rng_folder = re.search(r"^# The range structure inside is \S*/range-queries/([^/]+)/", text, re.M).group(1)
    return ops, rng_folder, text


def extra_args(rop, how, size, rng, gen, delta, mod):
    """The arguments after the nodes, valid for a path / subtree of `size` values (the range tests' rules)."""
    if how == "update":
        if rop in RT.POINT_UPDATES:
            return [delta(rng) if rop == "pointAdd" else gen(rng)]
        return RT.update_args(rop, rng, gen, mod)
    if how == "get":
        return []
    kind = RT.BRUTE_QUERIES[rop][0]
    if kind == "lr":
        return []
    if kind == "lrx":
        return [rng.randint(-2, 25) if "PrefixSum" in rop or "SuffixSum" in rop else gen(rng)]
    if kind == "lrkv":
        return [rng.randint(1, size)]
    if kind == "lrk0":
        return [rng.randint(0, size)]
    if kind == "lrij":
        return sorted((rng.randint(1, size), rng.randint(1, size)))
    if kind == "lrlohi":
        return sorted((gen(rng), gen(rng)))
    raise AssertionError(f"no argument rule for {rop} ({kind})")


def make_trials(folder, ops, range_folder, trials):
    """[(edges, root, vals, [(op, args)])] and the range tests' context for this folder's range template."""
    range_ops = RT.parse_ops(os.path.join(RT.DIR, range_folder, "template.py"), "#")
    gen, delta, extra, ctx = RT.domain(range_folder, range_ops)
    value_ops = [op for op in ops if op in TABLE]
    weights, node_vals = not folder.startswith("node-"), not folder.startswith("edge-")  # (both- has the two)
    updates = [op for op in value_ops if TABLE[op][1] == "update"]
    queries = [op for op in value_ops if TABLE[op][1] != "update"]
    wide = [op for op in updates if TABLE[op][0] != "one"]  # (path / subtree updates: their tags interact the most)
    # The range tests keep values >= 0 whenever a template has a prefix-sum search that needs it, which would leave
    # the max / min prefix sums of a path untested on negative values (where a backwards piece's prefixes and suffixes
    # differ). So where nothing else needs values >= 0, every other trial uses signed values and skips those searches.
    signed_ok = "leftmostPrefixSumGteX" in range_ops and not (set(range_ops) & KEEPS_NONNEG)
    base_gen, base_queries = gen, queries
    called = set()  # the value ops that got a real call (not only one that must raise)

    def build(t, force=()):
        """Trial t: a random tree and script. force: ops to call once more each, on a 20-node tree (see below)."""
        rng = random.Random(int(hashlib.md5(f"{folder}/{t}".encode()).hexdigest()[:8], 16))
        gen, queries = base_gen, base_queries
        if signed_ok and t % 2:
            gen = lambda r: r.randint(-6, 6)  # noqa: E731
            queries = [op for op in base_queries if TABLE[op][2] not in NONNEG_SEARCHES]
        n = 20 if force else rng.choice((1, 2, 3, 5, 8, 13, 20, 30, 45, 60))
        edges, root, lo = TS.make_tree(n, rng.choice(TS.SHAPES), rng)
        hi = lo + n - 1
        if weights:  # an edge / both template: every edge carries its weight
            edges = [[e[0], e[1], gen(rng)] for e in edges]
        vals = [gen(rng) for _ in range(hi + 1)] if node_vals else None
        sim = Sim(edges, root, vals, ctx)
        ref = sim.ref
        # (a path between two leaves crosses the most chains: half the path ops get one)
        leaves = [v for v in ref.nodes if len(ref.below[v]) == 1]
        seq = []

        def call(op):
            """One call of a value op with random arguments, as (op, args), or ("!" + op, args) when it must raise;
            None when this tree has no place for it (an edge op on one node)."""
            where, how, rop, _ = TABLE[op]
            if is_edge(op) and where == "one":  # an edge: a node and its parent, in either order
                if n == 1:
                    return None
                child = rng.choice([v for v in ref.nodes if v != root])
                nodes = [child, ref.par[child]][::rng.choice((1, -1))]
            else:
                nodes = [rng.choice(leaves) if where == "path" and rng.random() < 0.5 else rng.randrange(lo, hi + 1)
                         for _ in range(2 if where == "path" else 1)]
            seg = sim.values(op, nodes)
            if not seg and how == "query" and no_edges(op) == "raise":  # nothing to rank: the call must raise
                return "!" + op, nodes + [1] * TABLE[op][3]
            if how == "find" and "Sum" not in rop:
                rest = [search_x(seg, rop, rng, gen)]
            else:
                rest = extra_args(rop, how, max(1, len(seg)), rng, gen, delta, ctx["mod"])
            return op, nodes + rest

        def add(made):
            seq.append(made)
            if not made[0].startswith("!"):
                called.add(made[0])
                sim.run(*made)  # (keeps the values current for the next search)

        for _ in range(OPS_PER_TRIAL * (2 if weights and node_vals else 1)):  # (a both- template has twice the ops)
            roll = rng.random()
            if roll < 0.08:  # a shape op
                op = rng.choice(SHAPE_OPS)
                args = [rng.randrange(lo, hi + 1) if k == "n" else rng.randrange(0, n + 2) for k in TS.OPS[op]]
                seq.append((op, args))
                continue
            if updates and roll < 0.5:
                op = rng.choice(wide) if wide and rng.random() < 0.6 else rng.choice(updates)
            else:
                op = rng.choice(queries or updates)
            made = call(op)
            if made:
                add(made)
        for op in force:  # (up to 60 tries each: an edge op needs a path or subtree that has an edge)
            for _ in range(60):
                made = call(op)
                if made and not made[0].startswith("!"):
                    add(made)
                    break
        # a few calls with a node that is not in the tree: each must raise
        for op, args in rng.sample(seq, min(3, len(seq))):
            if op in TABLE:
                bad = list(args)
                bad[rng.randrange(node_count(op))] = rng.choice((lo - 1, hi + 1))
                seq.append(("!" + op, bad))
                if is_edge(op) and TABLE[op][0] == "one":  # and two nodes with no edge between them (a node and itself)
                    seq.append(("!" + op, [args[0], args[0]] + args[2:]))
        return edges, root, vals, seq

    out = [build(t) for t in range(trials)]
    # A random script can miss an op, or only ever catch an edge op where there are no edges (a leaf's subtree) and it
    # must raise. Every op gets one real call at least: the ones left over go into one more trial.
    missing = [op for op in value_ops if op not in called]
    if missing:
        out.append(build(trials, force=missing))
    return out, extra, ctx


class Sim:
    """The brute force for one tree: a value per node and a weight per edge (kept under its lower end), every path and
    subtree listed node by node. A node... op reads the values, an edge... op the weights."""

    def __init__(self, edges, root, vals, ctx):
        self.ref, self.ctx = TS.Brute(edges, root), ctx
        mod, par = ctx["mod"], self.ref.par
        fit = (lambda v: v % mod) if mod else (lambda v: v)
        self.val = {v: fit(vals[v]) for v in self.ref.nodes} if vals is not None else {}
        self.weight = {(e[0] if par[e[0]] == e[1] else e[1]): fit(e[2]) for e in edges if len(e) == 3}

    def store(self, op):
        return self.weight if is_edge(op) else self.val

    def reach(self, op, args):
        """(what op covers, in the order it reads it; the arguments after the nodes). Nodes for a node op; for an edge
        op the edges, each as its lower end."""
        where, ref = TABLE[op][0], self.ref
        if not is_edge(op):
            if where == "path":
                return ref.path(args[0], args[1]), args[2:]
            if where == "subtree":
                return sorted(ref.below[args[0]]), args[1:]
            if where == "up":  # node, its parent, ..., the root
                return ref.up(args[0]), args[1:]
            return [args[0]], args[1:]
        lower = lambda a, b: a if ref.par[a] == b else b  # noqa: E731
        if where == "path":
            p = ref.path(args[0], args[1])
            return [lower(p[i], p[i + 1]) for i in range(len(p) - 1)], args[2:]
        if where == "subtree":
            return sorted(ref.below[args[0]] - {args[0]}), args[1:]
        if where == "up":  # the edge above node, the one above that, ..., the one below the root
            return ref.up(args[0])[:-1], args[1:]
        return [lower(args[0], args[1])], args[2:]

    def values(self, op, args):
        return [self.store(op)[v] for v in self.reach(op, args)[0]]

    def run(self, op, args):
        """What op returns (None for an update, which is applied)."""
        if op.startswith("!"):
            return "OOR"
        if op not in TABLE:  # a shape op
            return self.ref.run(op, args)
        where, how, rop, _ = TABLE[op]
        nodes, rest = self.reach(op, args)
        held = self.store(op)
        seg = [held[v] for v in nodes]
        last = len(seg) - 1
        if not seg:  # (only an edge op: a path a..a, a leaf's subtree, the root's edge above)
            return None if how == "update" else -1 if how == "find" else no_edges(op)
        if how == "get":
            return seg[0]
        if how == "update":
            RT.brute_update(seg, rop, ([0] if where == "one" else [0, last]) + rest, self.ctx)
            for v, x in zip(nodes, seg):
                held[v] = x
            return None
        if how == "find":
            i = RT.BRUTE_QUERIES[rop][1](seg, 0, last, *rest, self.ctx)
            return nodes[i] if i != -1 else -1
        if rop == "rangeMode":
            return ("mode", seg, 0, last)
        return RT.BRUTE_QUERIES[rop][1](seg, 0, last, *rest, self.ctx)


def expected(trials, ctx):
    """What every op that returns something must return (in script order)."""
    exp = []
    for edges, root, vals, seq in trials:
        sim = Sim(edges, root, vals, ctx)
        for op, args in seq:
            res = sim.run(op, args)
            if answers(op):
                exp.append(res)
    return exp


def search_x(seg, rop, rng, gen):
    """The x of a search: mostly one of the few largest (or smallest) values it will read, so that only a node or two
    matches and the first match can sit anywhere along the walk (a random x matches the very first nodes)."""
    if not seg or rng.random() < 0.25:
        return gen(rng)
    if "IndexOf" in rop:
        return rng.choice(seg)
    ranked = sorted(seg)
    m = rng.randint(1, min(4, len(ranked)))
    return ranked[-m] if "Gt" in rop else ranked[m - 1]


def returns(op):
    return op.lstrip("!") not in TABLE or TABLE[op.lstrip("!")][1] != "update"


def answers(op):
    """Does a script line print something? Every query, and every call that must raise (it prints OOR)."""
    return op.startswith("!") or returns(op)


def run_py(text, trials, extra):
    ns = {}
    exec(compile(text, "template.py", "exec"), ns)
    out = []
    for edges, root, vals, seq in trials:
        tree = ns["Tree"](edges, root, *extra) if vals is None else ns["Tree"](edges, root, vals, *extra)
        for op, args in seq:
            if op.startswith("!"):
                try:
                    out.append(f"no error, returned {RT.norm(getattr(tree, op[1:])(*args))}")
                except IndexError:
                    out.append("OOR")
                continue
            res = getattr(tree, op)(*args)
            if returns(op):
                out.append(RT.norm(res))
    return out


# ------------------------------------------------------------------------------------------------ C++
def cpp_driver(folder, ops, extra):
    extra_text = "".join(f", {e}" for e in extra)
    weights = not folder.startswith("node-")  # (an edge- or both- template: the weights ride in the edge list)
    small_vals = ", vector<long long>{1, 2, 1}" if folder.startswith("both-") else ""
    lines = [f'#include "{os.path.join(DIR, folder, "template.cpp")}"',
             "template struct Tree<int>;  // (type-check the generic code for int too)",
             "template <class X> void out(const X& x) { cout << x << '\\n'; }",
             "void out(bool b) { cout << (b ? 1 : 0) << '\\n'; }",
             "template <class A, class B> void out(const pair<A, B>& p) { cout << p.first << ' ' << p.second << '\\n'; }",
             "template <class X> void out(const optional<X>& o) { if (o) cout << *o << '\\n'; else cout << \"None\\n\"; }",
             "int main() {",
             "  ios::sync_with_stdio(false); cin.tie(nullptr);",
             # (the trials pass long long weights: this builds an edge tree from int ones, as LeetCode gives them;
             # weights 1 and 2 are inside every range template's allowed values)
             *([f"  {{ vector<vector<int>> ints = {{{{0, 1, 1}}, {{1, 2, 2}}}}; Tree<long long> small(ints, 0{small_vals}{extra_text}); "
                "if (small.subtreeSize(0) != 3) return 3; }"] if weights else []),
             "  int cases; cin >> cases;",
             "  while (cases--) {",
             "    int m, root; cin >> m >> root;",
             # (an edge template's weights ride in the edge list and can be far past int: read them as long long)
             f"    vector<vector<{'long long' if weights else 'int'}>> edges(m);",
             "    for (auto& e : edges) { int len; cin >> len; e.resize(len); for (auto& x : e) cin >> x; }",
             "    int nv; cin >> nv; vector<long long> vals(nv); for (auto& x : vals) cin >> x;",
             f"    Tree<long long> t(edges, root{extra_text});" if folder.startswith("edge-") else
             f"    Tree<long long> t(edges, root, vals{extra_text});",
             "    int q; cin >> q;",
             "    while (q--) {",
             "      string op; cin >> op;",
             "      bool bad = op[0] == '!';  // (a node that is not in the tree: must throw)",
             "      if (bad) op = op.substr(1);",
             "      long long a[6] = {0, 0, 0, 0, 0, 0};",
             "      int cnt; cin >> cnt; for (int i = 0; i < cnt; i++) cin >> a[i];",
             "      try {",
             "      if (false) {}"]
    for op in ops:
        count = len(TS.OPS[op]) if op in TS.OPS else node_count(op) + TABLE[op][3]
        call = f"t.{op}({', '.join(f'a[{i}]' for i in range(count))})"
        body = f"out({call});" if returns(op) else f"{call};"
        if op == "pathNodes":
            body = f"auto r = {call}; cout << r.size() << '\\n';"
        lines.append(f'      else if (op == "{op}") {{ {body} }}')
    lines += ["      else { cerr << \"unknown op \" << op << '\\n'; return 1; }",
              "      if (bad) cout << \"no error\\n\";",
              "      } catch (const out_of_range&) { if (!bad) throw; cout << \"OOR\\n\"; }",
              "    }", "  }", "}"]
    return "\n".join(lines) + "\n"


def run_cpp(folder, ops, trials, extra):
    os.makedirs(BUILD, exist_ok=True)
    tag = hashlib.md5(folder.encode()).hexdigest()[:10]
    src = os.path.join(BUILD, folder[:120] + "-" + tag + ".cpp")
    exe = src[:-4]
    open(src, "w").write(cpp_driver(folder, ops, extra))
    comp = subprocess.run([cxx(), "-std=c++17", "-O2", "-Wall", *sanitize_flags(), "-o", exe, src], capture_output=True, text=True)
    if comp.returncode:
        raise RuntimeError("compile error:\n" + comp.stderr[:2500])
    inp = [str(len(trials))]
    for edges, root, vals, seq in trials:
        inp.append(f"{len(edges)} {root}")
        inp += [" ".join(map(str, [len(e)] + list(e))) for e in edges]
        inp.append("0" if vals is None else f"{len(vals)} " + " ".join(map(str, vals)))
        inp.append(str(len(seq)))
        inp += [" ".join(map(str, [op, len(args)] + args)) for op, args in seq]
    run = subprocess.run([exe], input="\n".join(inp) + "\n", capture_output=True, text=True, timeout=300)
    for path in (src, exe):
        os.remove(path)
    if run.returncode:
        raise RuntimeError(f"binary exited {run.returncode}: {run.stderr[:500]}")
    return run.stdout.split("\n")[:-1], comp.stderr.strip()


def describe(trials, k):
    seen = 0
    for t, (edges, root, vals, seq) in enumerate(trials):
        for step, (op, args) in enumerate(seq):
            if not answers(op):
                continue
            if seen == k:
                return f"trial {t}, step {step}: {op}({', '.join(map(str, args))}); edges {edges}, root {root}, vals {vals}"
            seen += 1
    return "?"


def mismatch(got, exp, trials, wrap64=False):
    if len(got) != len(exp):
        return f"{len(got)} outputs, expected {len(exp)}"
    for k, (g, e) in enumerate(zip(got, exp)):
        if e in (("+inf",), ("-inf",)):  # (no edges to take a min / max over: Python's inf, C++'s largest long long)
            e = ({"+inf": 2**63 - 1, "-inf": -2**63} if wrap64 else {"+inf": "inf", "-inf": "-inf"})[e[0]]
        if not RT.matches(g, e, wrap64):
            want = "a mode with its frequency" if isinstance(e, tuple) and e and e[0] == "mode" else RT.norm(e)
            return f"answer #{k} ({describe(trials, k)[:900]}): got {g}, expected {want}"
    return None


def test_folder(folder, langs, trials_n):
    """One line per language: PASS / FAIL (the range tests' style)."""
    lines = []
    try:
        ops, range_folder, text = read_ops(folder)
        unknown = [op for op in ops if op not in TABLE and op not in TS.OPS]
        if unknown:
            return [f"FAIL  {folder}: the test has no brute force for {unknown}"]
        trials, extra, ctx = make_trials(folder, ops, range_folder, trials_n)
        exp = expected(trials, ctx)
    except Exception as e:  # noqa: BLE001
        return [f"FAIL  {folder}: could not set up: {type(e).__name__}: {str(e)[:300]}"]
    covered = {op for _, _, _, seq in trials for op, _ in seq}
    missed = [op for op in ops if op in TABLE and op not in covered]
    if "--py" in langs:
        try:
            bad = mismatch(run_py(text, trials, extra), exp, trials)
        except Exception as e:  # noqa: BLE001
            bad = f"{type(e).__name__}: {str(e)[:400]}"
        lines.append(f"FAIL  {folder} (py): {bad}" if bad else f"PASS  {folder} (py): {len(exp)} answers"
                     + (f", never called: {missed}" if missed else ""))
    if "--cpp" in langs:
        try:
            got, warnings = run_cpp(folder, ops, trials, extra)
            bad = mismatch(got, exp, trials, wrap64=True)
            if not bad and warnings:
                bad = "compiler warnings:\n" + warnings[:1500]
        except Exception as e:  # noqa: BLE001
            bad = f"{type(e).__name__}: {str(e)[:2500]}"
        lines.append(f"FAIL  {folder} (cpp): {bad}" if bad else f"PASS  {folder} (cpp): {len(exp)} answers")
    return lines


def main():
    args = sys.argv[1:]
    langs = [a for a in args if a in ("--py", "--cpp")] or ["--py", "--cpp"]
    trials_n, shard, names, listed, k = 24, None, [], None, 0
    while k < len(args):
        if args[k] == "--trials":
            trials_n = int(args[k + 1])
            k += 1
        elif args[k] == "--shard":
            shard = tuple(map(int, args[k + 1].split("/")))
            k += 1
        elif args[k] == "--from":
            listed = set(open(args[k + 1]).read().split())
            k += 1
        elif not args[k].startswith("--"):
            names.append(args[k])
        k += 1
    folders = sorted(f for f in os.listdir(DIR) if f.startswith(("node-", "edge-", "both-")) and os.path.isdir(os.path.join(DIR, f)))
    if names:
        folders = [f for f in folders if any(n in f for n in names)]
    if listed is not None:
        folders = [f for f in folders if f in listed]
    if shard:
        folders = folders[shard[0]::shard[1]]
    fails = 0
    for folder in folders:
        for line in test_folder(folder, langs, trials_n):
            fails += line.startswith("FAIL")
            print(line, flush=True)
    print(f"{'FAIL' if fails else 'PASS'}  tree value templates: {len(folders)} folders, {fails} failures")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
