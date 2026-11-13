"""Tests the tree templates that hold values (tree-queries/node-*) against a brute force.

The brute force is a plain tree: a value per node, every path walked node by node through parent pointers, every
subtree listed. What an op means on a list of values comes from the range-query tests (range-query-tests/
test_templates.py: BRUTE_QUERIES, brute_update, and domain() for the values each range template allows), so a tree op
is checked as "collect the values along the path (or in the subtree), ask the range brute force". Nothing here knows
about heavy-light decomposition.

Random op scripts run on template.py and are compared with the brute force; the same scripts then go to
template.cpp (built from a generated driver), which has to print the same. Both labelings (0..n-1 and 1..n), six tree
shapes, a few shape ops per script, and calls with a node that is not in the tree (must raise).

    python3 test_tree.py                 # every folder, both languages
    python3 test_tree.py --py            # Python only
    python3 test_tree.py --cpp           # C++ only
    python3 test_tree.py rangeAdd beats  # folders whose name contains one of these
    python3 test_tree.py --shard 3/8     # every 8th folder from the 3rd (run 8 side by side)
    python3 test_tree.py --trials 60     # more random trees per folder (default 24)
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


TABLE = op_table()
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
    updates = [op for op in value_ops if TABLE[op][1] == "update"]
    queries = [op for op in value_ops if TABLE[op][1] != "update"]
    wide = [op for op in updates if TABLE[op][0] != "one"]  # (path / subtree updates: their tags interact the most)
    # The range tests keep values >= 0 whenever a template has a prefix-sum search that needs it, which would leave
    # the max / min prefix sums of a path untested on negative values (where a backwards piece's prefixes and suffixes
    # differ). So where nothing else needs values >= 0, every other trial uses signed values and skips those searches.
    signed_ok = "leftmostPrefixSumGteX" in range_ops and not (set(range_ops) & KEEPS_NONNEG)
    base_gen, base_queries = gen, queries
    out = []
    for t in range(trials):
        rng = random.Random(int(hashlib.md5(f"{folder}/{t}".encode()).hexdigest()[:8], 16))
        gen, queries = base_gen, base_queries
        if signed_ok and t % 2:
            gen = lambda r: r.randint(-6, 6)  # noqa: E731
            queries = [op for op in base_queries if TABLE[op][2] not in NONNEG_SEARCHES]
        n = rng.choice((1, 2, 3, 5, 8, 13, 20, 30, 45, 60))
        edges, root, lo = TS.make_tree(n, rng.choice(TS.SHAPES), rng)
        hi = lo + n - 1
        vals = [gen(rng) for _ in range(hi + 1)]
        sim = Sim(edges, root, vals, ctx)
        ref = sim.ref
        # (a path between two leaves crosses the most chains: half the path ops get one)
        leaves = [v for v in ref.nodes if len(ref.below[v]) == 1]
        seq = []
        for _ in range(OPS_PER_TRIAL):
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
            where, how, rop, _ = TABLE[op]
            nodes = [rng.choice(leaves) if where == "path" and rng.random() < 0.5 else rng.randrange(lo, hi + 1)
                     for _ in range(2 if where == "path" else 1)]
            size = (len(ref.path(*nodes)) if where == "path" else len(ref.below[nodes[0]]) if where == "subtree" else 1)
            if how == "find" and "Sum" not in rop:
                rest = [search_x(sim.values(op, nodes), rop, rng, gen)]
            else:
                rest = extra_args(rop, how, size, rng, gen, delta, ctx["mod"])
            seq.append((op, nodes + rest))
            sim.run(op, nodes + rest)  # (keeps the values current for the next search)
        # a few calls with a node that is not in the tree: each must raise
        for op, args in rng.sample(seq, min(3, len(seq))):
            if op in TABLE:
                bad = list(args)
                bad[rng.randrange(2 if TABLE[op][0] == "path" else 1)] = rng.choice((lo - 1, hi + 1))
                seq.append(("!" + op, bad))
        out.append((edges, root, vals, seq))
    return out, extra, ctx


class Sim:
    """The brute force for one tree: a value per node, every path and subtree listed node by node."""

    def __init__(self, edges, root, vals, ctx):
        self.ref, self.ctx = TS.Brute(edges, root), ctx
        self.val = {v: (vals[v] % ctx["mod"] if ctx["mod"] else vals[v]) for v in self.ref.nodes}

    def reach(self, op, args):
        """(the nodes op covers, in the order it reads them; the arguments after the nodes)."""
        where, ref = TABLE[op][0], self.ref
        if where == "path":
            return ref.path(args[0], args[1]), args[2:]
        if where == "subtree":
            return sorted(ref.below[args[0]]), args[1:]
        if where == "up":  # node, its parent, ..., the root
            return ref.up(args[0]), args[1:]
        return [args[0]], args[1:]

    def values(self, op, args):
        return [self.val[v] for v in self.reach(op, args)[0]]

    def run(self, op, args):
        """What op returns (None for an update, which is applied)."""
        if op.startswith("!"):
            return "OOR"
        if op not in TABLE:  # a shape op
            return self.ref.run(op, args)
        where, how, rop, _ = TABLE[op]
        nodes, rest = self.reach(op, args)
        seg = [self.val[v] for v in nodes]
        last = len(seg) - 1
        if how == "get":
            return seg[0]
        if how == "update":
            RT.brute_update(seg, rop, ([0] if where == "one" else [0, last]) + rest, self.ctx)
            for v, x in zip(nodes, seg):
                self.val[v] = x
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
    if rng.random() < 0.25:
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
        tree = ns["Tree"](edges, root, vals, *extra)
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
    lines = [f'#include "{os.path.join(DIR, folder, "template.cpp")}"',
             "template struct Tree<int>;  // (type-check the generic code for int too)",
             "template <class X> void out(const X& x) { cout << x << '\\n'; }",
             "void out(bool b) { cout << (b ? 1 : 0) << '\\n'; }",
             "template <class A, class B> void out(const pair<A, B>& p) { cout << p.first << ' ' << p.second << '\\n'; }",
             "template <class X> void out(const optional<X>& o) { if (o) cout << *o << '\\n'; else cout << \"None\\n\"; }",
             "int main() {",
             "  ios::sync_with_stdio(false); cin.tie(nullptr);",
             "  int cases; cin >> cases;",
             "  while (cases--) {",
             "    int m, root; cin >> m >> root;",
             "    vector<vector<int>> edges(m);",
             "    for (auto& e : edges) { int len; cin >> len; e.resize(len); for (auto& x : e) cin >> x; }",
             "    int nv; cin >> nv; vector<long long> vals(nv); for (auto& x : vals) cin >> x;",
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
        count = len(TS.OPS[op]) if op in TS.OPS else {"one": 1, "up": 1, "subtree": 1, "path": 2}[TABLE[op][0]] + TABLE[op][3]
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
        inp.append(f"{len(vals)} " + " ".join(map(str, vals)))
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
    trials_n, shard, names, k = 24, None, [], 0
    while k < len(args):
        if args[k] == "--trials":
            trials_n = int(args[k + 1])
            k += 1
        elif args[k] == "--shard":
            shard = tuple(map(int, args[k + 1].split("/")))
            k += 1
        elif not args[k].startswith("--"):
            names.append(args[k])
        k += 1
    folders = sorted(f for f in os.listdir(DIR) if f.startswith("node-") and os.path.isdir(os.path.join(DIR, f)))
    if names:
        folders = [f for f in folders if any(n in f for n in names)]
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
