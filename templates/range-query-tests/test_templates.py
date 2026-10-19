"""Test every range-query template, in every language it has, against a brute force.

For each folder in templates/range-queries, the @operations header says what the template supports. This script
replays random op sequences on a plain Python list (the brute force below knows every op) and checks that
template.py and template.cpp give the same answers. Nothing here is per-template: a new template is covered as
soon as its ops are in BRUTE_UPDATES / BRUTE_QUERIES.

    python3 test_templates.py                 # everything
    python3 test_templates.py rangeGcd beats  # only folders whose name contains one of these
    python3 test_templates.py --py            # Python only (no compiler needed)
    python3 test_templates.py --cpp           # C++ only
    python3 test_templates.py --trials 300    # more random sequences per template (default 120)

C++ needs a GCC with bits/stdc++.h: set CXX, or it tries g++-15 ... g++-11, then g++.
Each template.cpp is compiled with T = long long and also explicitly instantiated with T = int.
"""
import bisect
import importlib.util
import inspect
import math
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from functools import reduce

sys.dont_write_bytecode = True  # never leave __pycache__ inside a template folder
sys.setrecursionlimit(10000)

HERE = os.path.dirname(os.path.abspath(__file__))
DIR = os.path.join(os.path.dirname(HERE), "range-queries")
BUILD = os.path.join(tempfile.gettempdir(), "range-query-template-tests")
OPS_PER_TRIAL = 60

# ------------------------------------------------------------------------------------------------ brute force

POINT_UPDATES = ("pointAssign", "pointAdd", "pointChmax", "pointChmin", "pointAssignMod", "pointAddMod")
RANGE_UPDATES = {  # op -> number of args after (l, r)
    "rangeAdd": 1, "rangeAssign": 1, "rangeAddMod": 1, "rangeAssignMod": 1, "rangeChmax": 1, "rangeChmin": 1, "rangeMultMod": 1, "rangeAffineMod": 2,
    "rangeAddArithSeq": 2, "rangeAddArithSeqMod": 2, "rangeMod": 1, "rangeFloorDiv": 1, "rangeFloorSqrt": 0,
    "rangeAndApply": 1, "rangeOrApply": 1, "rangeXorApply": 1,
}
MOD_OPS = {"rangeMultMod", "rangeAffineMod", "rangeAddArithSeqMod", "rangeAddMod", "rangeAssignMod", "rangeSumMod",
           "pointAddMod", "pointAssignMod"}  # any of these: every value lives mod p


def _first(a, idxs, pred):
    return next((i for i in idxs if pred(a[i])), -1)


def _kth(a, l, r, k, pred):
    hits = [i for i in range(l, r + 1) if pred(a[i])]
    return hits[k - 1] if 0 < k <= len(hits) else -1


def _max_sub(seg):
    best = cur = seg[0]
    for v in seg[1:]:
        cur = max(v, cur + v)
        best = max(best, cur)
    return best


def _prefix_search(a, l, r, x, strict):
    run = 0
    for i in range(l, r + 1):
        run += a[i]
        if run > x or (not strict and run == x):
            return i
    return -1


def _lis(seq):
    tails = []
    for v in seq:
        k = bisect.bisect_left(tails, v)
        if k == len(tails):
            tails.append(v)
        else:
            tails[k] = v
    return len(tails)


def _cost_mono_dec(seg):
    return _cost_mono_inc(seg[::-1])


def _longest_run(seg):
    best = run = 1
    for x, y in zip(seg, seg[1:]):
        run = run + 1 if x == y else 1
        best = max(best, run)
    return best


def _max_alt(seg):
    plus = minus = float("-inf")  # best sum of a non-empty alternating subsequence ending on + / on -
    for v in seg:
        plus, minus = max(plus, v, minus + v), max(minus, plus - v)
    return max(plus, minus)


def _cost_mono_inc(seg):
    mx, cost = seg[0], 0
    for v in seg:
        mx = max(mx, v)
        cost += mx - v
    return cost


SIDE = {"leftmost": lambda l, r: range(l, r + 1), "rightmost": lambda l, r: range(r, l - 1, -1)}
CMP = {"Gte": lambda v, x: v >= x, "Gt": lambda v, x: v > x, "Lte": lambda v, x: v <= x, "Lt": lambda v, x: v < x}

# query op -> (arg kind, brute(a, l, r, *args, ctx)); arg kinds: "lr", "lrx", "lrk", "lrkx", "lrlohi"
BRUTE_QUERIES = {
    "rangeSum": ("lr", lambda a, l, r, c: sum(a[l:r + 1])),
    "rangeSumMod": ("lr", lambda a, l, r, c: sum(a[l:r + 1]) % c["mod"]),
    "rangeMin": ("lr", lambda a, l, r, c: min(a[l:r + 1])),
    "rangeMax": ("lr", lambda a, l, r, c: max(a[l:r + 1])),
    "rangeGcd": ("lr", lambda a, l, r, c: reduce(math.gcd, (abs(v) for v in a[l:r + 1]), 0)),
    "rangeAndQuery": ("lr", lambda a, l, r, c: reduce(lambda x, y: x & y, a[l:r + 1])),
    "rangeOrQuery": ("lr", lambda a, l, r, c: reduce(lambda x, y: x | y, a[l:r + 1])),
    "maxSubarraySum": ("lr", lambda a, l, r, c: _max_sub(a[l:r + 1])),
    "maxPrefixSum": ("lr", lambda a, l, r, c: max(sum(a[l:i + 1]) for i in range(l, r + 1))),
    "maxSuffixSum": ("lr", lambda a, l, r, c: max(sum(a[i:r + 1]) for i in range(l, r + 1))),
    "countValue": ("lr", lambda a, l, r, c: a[l:r + 1].count(c["number"])),
    "countOccurrences": ("lrx", lambda a, l, r, x, c: a[l:r + 1].count(x)),
    "countDistinct": ("lr", lambda a, l, r, c: len(set(a[l:r + 1]))),
    "allDistinct": ("lr", lambda a, l, r, c: len(set(a[l:r + 1])) == r - l + 1),
    "rangeMode": ("lr", None),  # ties may return any mode: checked by _check_mode
    "rangeLIS": ("lr", lambda a, l, r, c: _lis(a[l:r + 1])),
    "costMonoIncreasing": ("lr", lambda a, l, r, c: _cost_mono_inc(a[l:r + 1])),
    "costMonoDecreasing": ("lr", lambda a, l, r, c: _cost_mono_dec(a[l:r + 1])),
    "costStrictIncreasing": ("lr", lambda a, l, r, c: _cost_mono_inc([v - i for i, v in enumerate(a[l:r + 1])])),
    "costStrictDecreasing": ("lr", lambda a, l, r, c: _cost_mono_dec([v + i for i, v in enumerate(a[l:r + 1])])),
    "longestEqualRun": ("lr", lambda a, l, r, c: _longest_run(a[l:r + 1])),
    "maxAltSubseqSum": ("lr", lambda a, l, r, c: _max_alt(a[l:r + 1])),
    "kthOccurrence": ("lrk", lambda a, l, r, k, c: _kth(a, l, r, k, lambda v: v == c["number"])),
    "doAllElementsAppearEvenFrequency": ("lr", lambda a, l, r, c: all(v % 2 == 0 for v in Counter(a[l:r + 1]).values())),
    "countInValRange": ("lrlohi", lambda a, l, r, lo, hi, c: sum(lo <= v <= hi for v in a[l:r + 1])),
    "sumInValRange": ("lrlohi", lambda a, l, r, lo, hi, c: sum(v for v in a[l:r + 1] if lo <= v <= hi)),
    "leftmostPrefixSumGteX": ("lrx", lambda a, l, r, x, c: _prefix_search(a, l, r, x, False)),
    "leftmostPrefixSumGtX": ("lrx", lambda a, l, r, x, c: _prefix_search(a, l, r, x, True)),
}
for _side, _idx in SIDE.items():
    for _name, _cmp in CMP.items():
        BRUTE_QUERIES[f"{_side}{_name}X"] = ("lrx", lambda a, l, r, x, c, _idx=_idx, _cmp=_cmp: _first(a, _idx(l, r), lambda v: _cmp(v, x)))
for _name, _cmp in CMP.items():
    BRUTE_QUERIES[f"kth{_name}X"] = ("lrkx", lambda a, l, r, k, x, c, _cmp=_cmp: _kth(a, l, r, k, lambda v: _cmp(v, x)))


def _check_mode(a, l, r, got):
    """got is (value, freq); any value with the max frequency is a correct answer."""
    cnt = Counter(a[l:r + 1])
    best = max(cnt.values())
    return got[1] == best and cnt.get(got[0], 0) == best


def brute_update(a, op, args, ctx):
    mod, full = ctx["mod"], ctx["full"]
    if op in POINT_UPDATES:
        i, v = args
        a[i] = {"pointAssign": v, "pointAdd": a[i] + v, "pointChmax": max(a[i], v), "pointChmin": min(a[i], v),
                "pointAssignMod": v, "pointAddMod": a[i] + v}[op]
        if full is not None:
            a[i] &= full
        if mod:
            a[i] %= mod
        return
    l, r, *xs = args
    for i in range(l, r + 1):
        v = a[i]
        if op in ("rangeAdd", "rangeAddMod"): v += xs[0]
        elif op in ("rangeAssign", "rangeAssignMod"): v = xs[0]
        elif op == "rangeChmax": v = max(v, xs[0])
        elif op == "rangeChmin": v = min(v, xs[0])
        elif op == "rangeMultMod": v *= xs[0]
        elif op == "rangeAffineMod": v = v * xs[0] + xs[1]
        elif op in ("rangeAddArithSeq", "rangeAddArithSeqMod"): v += xs[0] + (i - l) * xs[1]
        elif op == "rangeMod": v %= xs[0]
        elif op == "rangeFloorDiv": v //= xs[0]
        elif op == "rangeFloorSqrt": v = math.isqrt(v)
        elif op == "rangeAndApply": v &= xs[0]
        elif op == "rangeOrApply": v |= xs[0]
        elif op == "rangeXorApply": v ^= xs[0]
        a[i] = v % mod if mod else v


# ------------------------------------------------------------------------------------------------ value domains

def domain(folder, ops):
    """Random-input rules for one template: values, point-add deltas, ctor extra args, and the brute context.
    Keeps inputs inside each template's documented preconditions (e.g. shrink ops need values >= 0)."""
    ctx = {"mod": None, "full": None, "number": None}
    small = lambda r: r.randint(-10, 10)  # noqa: E731
    nonneg_small = lambda r: r.randint(0, 10)  # noqa: E731
    if MOD_OPS & set(ops):
        ctx["mod"] = 97
        return (lambda r: r.randint(0, 96)), (lambda r: r.randint(0, 96)), [97], ctx
    if {"rangeAndApply", "rangeOrApply", "rangeXorApply", "rangeAndQuery", "rangeOrQuery"} & set(ops):
        if "rangeSum" in ops or "rangeMin" in ops:  # the bit-beats tree masks values to 20 bits
            ctx["full"] = (1 << 20) - 1
        return (lambda r: r.randint(0, 63)), nonneg_small, [], ctx
    if "leftmostPrefixSumGteX" in ops:
        return (lambda r: r.randint(0, 6)), nonneg_small, [], ctx
    if "rangeFloorSqrt" in ops and "rangeSum" not in ops:
        return (lambda r: r.choice([r.randint(0, 200), r.randint(0, (1 << 62) - 1)])), nonneg_small, [], ctx
    if "rangeFloorDiv" in ops and "rangeSum" not in ops:
        return (lambda r: r.choice([r.randint(-60, 60), r.randint(-10**17, 10**17)])), small, [], ctx
    if {"rangeMod", "rangeFloorSqrt", "rangeFloorDiv"} & set(ops):
        return (lambda r: r.randint(0, 200)), nonneg_small, [], ctx
    if "rangeGcd" in ops:
        return (lambda r: r.randint(0, 60)), nonneg_small, [], ctx
    if {"countDistinct", "allDistinct", "rangeMode", "doAllElementsAppearEvenFrequency", "countOccurrences"} & set(ops):
        return (lambda r: r.randint(0, 6)), nonneg_small, [], ctx
    if "countValue" in ops:
        ctx["number"] = 3
        return (lambda r: r.randint(0, 5)), nonneg_small, [3], ctx
    if "longestEqualRun" in ops:
        return (lambda r: r.randint(0, 2)), (lambda r: r.randint(-1, 1)), [], ctx
    if "costMonoIncreasing" in ops:
        return (lambda r: r.randint(0, 50)), small, [], ctx
    return (lambda r: r.randint(-50, 50)), small, [], ctx


def update_args(op, rng, gen, mod):
    if op in ("rangeAddArithSeq", "rangeAddArithSeqMod"):
        return [gen(rng), rng.randint(0, mod - 1) if mod else rng.randint(-20, 20)]
    if op == "rangeAffineMod":
        return [gen(rng), gen(rng)]
    if op == "rangeFloorDiv":
        return [rng.choice([2, 2, 3, 5, 7, 10**6, 10**12])]
    if op == "rangeMod":
        return [rng.randint(1, 60)]
    if op == "rangeFloorSqrt":
        return []
    return [gen(rng)]


def make_trials(folder, ops, trials):
    """Deterministic random op sequences: [(initial array, [(op, args)])]."""
    gen, delta, _, ctx = domain(folder, ops)
    updates = [o for o in ops if o in POINT_UPDATES or o in RANGE_UPDATES]
    queries = [o for o in ops if o not in updates]
    out = []
    for t in range(trials):
        rng = random.Random(t)
        n = rng.randint(1, 30)
        a = [gen(rng) for _ in range(n)]
        seq = []
        for _ in range(OPS_PER_TRIAL):
            op = rng.choice(updates) if updates and rng.random() < 0.5 else rng.choice(queries or updates)
            if op == "pointGet":
                args = [rng.randrange(n)]
            elif op in POINT_UPDATES:
                args = [rng.randrange(n), delta(rng) if op in ("pointAdd", "pointAddMod") else gen(rng)]
            else:
                l, r = sorted((rng.randrange(n), rng.randrange(n)))
                kind = "upd" if op in RANGE_UPDATES else BRUTE_QUERIES[op][0]
                if kind == "upd":
                    args = [l, r] + update_args(op, rng, gen, ctx["mod"])
                elif kind == "lrx":
                    args = [l, r, rng.randint(-2, 25) if "PrefixSum" in op else gen(rng)]
                elif kind == "lrkx":
                    args = [l, r, rng.randint(1, 5), gen(rng)]
                elif kind == "lrk":
                    args = [l, r, rng.randint(0, 6)]
                elif kind == "lrlohi":
                    args = [l, r, *sorted((gen(rng), gen(rng)))]
                else:
                    args = [l, r]
            seq.append((op, args))
        out.append((a, seq))
    return out, ctx


def expected_outputs(trials, ctx):
    """Replay every sequence on the brute force; returns per query either a value or ("mode", a, l, r)."""
    exp = []
    for a0, seq in trials:
        a = list(a0)
        if ctx["mod"]:
            a = [v % ctx["mod"] for v in a]
        for op, args in seq:
            if op == "pointGet":
                exp.append(a[args[0]])
            elif op in POINT_UPDATES or op in RANGE_UPDATES:
                brute_update(a, op, args, ctx)
            elif op == "rangeMode":
                exp.append(("mode", list(a), *args))
            else:
                exp.append(BRUTE_QUERIES[op][1](a, *args, ctx))
    return exp


def matches(got_text, want):
    if isinstance(want, tuple) and want and want[0] == "mode":
        _, a, l, r = want
        parts = got_text.split()
        return len(parts) == 2 and _check_mode(a, l, r, (int(parts[0]), int(parts[1])))
    return got_text == norm(want)


def norm(v):
    if isinstance(v, bool):
        return str(int(v))
    if isinstance(v, tuple):
        return " ".join(norm(x) for x in v)
    return str(v)


def first_mismatch(got, exp, trials):
    if len(got) != len(exp):
        return f"{len(got)} outputs, expected {len(exp)}"
    for k, (g, e) in enumerate(zip(got, exp)):
        if not matches(g, e):
            want = "a mode with its frequency" if isinstance(e, tuple) and e and e[0] == "mode" else norm(e)
            return f"query #{k} ({describe_query(trials, k)}): got {g}, expected {want}"
    return None


def describe_query(trials, k):
    seen = 0
    for t, (a0, seq) in enumerate(trials):
        for step, (op, args) in enumerate(seq):
            if op in POINT_UPDATES or op in RANGE_UPDATES:
                continue
            if seen == k:
                return f"trial {t}, step {step}: {op}({', '.join(map(str, args))}), initial array {a0}"
            seen += 1
    return "?"


# ------------------------------------------------------------------------------------------------ Python side

def owner(op, table):
    """The class/struct implementing op, preferring the one implementing the most ops overall."""
    cands = [n for n, ms in table.items() if op in ms]
    return max(cands, key=lambda n: (len(table[n]), n)) if cands else None


def run_python(folder, ops, trials, ctor_extra):
    path = os.path.join(DIR, folder, "template.py")
    spec = importlib.util.spec_from_file_location("t_" + re.sub(r"\W", "_", folder), path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    classes = {n: c for n, c in inspect.getmembers(mod, inspect.isclass) if c.__module__ == mod.__name__}
    table = {n: {o for o in ops if hasattr(c, o)} for n, c in classes.items()}
    missing = [o for o in ops if owner(o, table) is None]
    if missing:
        raise RuntimeError(f"template.py has no method for {missing}")
    out = []
    for a0, seq in trials:
        objs = {}
        for op, args in seq:
            name = owner(op, table)
            if name not in objs:
                objs[name] = classes[name](list(a0), *ctor_extra)
            res = getattr(objs[name], op)(*args)
            if not (op in POINT_UPDATES or op in RANGE_UPDATES):
                out.append(norm(res))
    return out


# ------------------------------------------------------------------------------------------------ C++ side

def find_cxx():
    cands = [os.environ["CXX"]] if os.environ.get("CXX") else [f"g++-{v}" for v in range(15, 10, -1)] + ["g++"]
    for c in cands:
        exe = shutil.which(c) or (c if os.path.exists(c) else None)
        if not exe:
            continue
        probe = subprocess.run([exe, "-std=c++17", "-x", "c++", "-fsyntax-only", "-"], input="#include <bits/stdc++.h>\n",
                               capture_output=True, text=True)
        if probe.returncode == 0:
            return exe
    return None


def cpp_structs(path):
    """{struct name: set of method names} for each top-level `template <typename T> struct X`."""
    lines = open(path).read().split("\n")
    out, i = {}, 0
    while i < len(lines):
        if re.match(r"\s*template\s*<\s*typename\s+T", lines[i]) and i + 1 < len(lines):
            m = re.match(r"\s*struct\s+(\w+)", lines[i + 1])
            if m:
                name, depth, methods, j = m.group(1), 0, set(), i + 1
                while j < len(lines):
                    mm = re.match(r"\s*(?:[\w:<>,\s\*&]+?)\s+(\w+)\s*\(", lines[j]) if depth == 1 else None
                    if mm:
                        methods.add(mm.group(1))
                    depth += lines[j].count("{") - lines[j].count("}")
                    if depth == 0 and "}" in lines[j]:
                        break
                    j += 1
                out[name] = methods
                i = j
        i += 1
    return out


def cpp_driver(folder, ops, structs, ctor_extra):
    owners = {op: owner(op, structs) for op in ops}
    missing = [op for op, o in owners.items() if o is None]
    if missing:
        raise RuntimeError(f"template.cpp has no method for {missing}")
    used = sorted(set(owners.values()))
    extra = "".join(f", {e}" for e in ctor_extra)
    lines = ["#include <bits/stdc++.h>", "using namespace std;", f'#include "{os.path.join(DIR, folder, "template.cpp")}"']
    lines += [f"template struct {s}<int>;" for s in used]  # type-check the generic code for int too
    lines += [
        "template <class X> void out(const X& x) { cout << x << '\\n'; }",
        "void out(bool b) { cout << (b ? 1 : 0) << '\\n'; }",
        "template <class A, class B> void out(const pair<A, B>& p) { cout << p.first << ' ' << p.second << '\\n'; }",
        "int main() {",
        "  ios::sync_with_stdio(false); cin.tie(nullptr);",
        "  int cases; cin >> cases;",
        "  while (cases--) {",
        "    int n; cin >> n; vector<long long> a(n); for (auto& x : a) cin >> x;",
        "    int q; cin >> q;",
    ]
    lines += [f"    {s}<long long> s_{s}(a{extra});" for s in used]
    lines += ["    while (q--) {", "      string op; cin >> op;", "      if (false) {}"]
    for op in ops:
        s = f"s_{owners[op]}"
        if op == "pointGet":
            body = f"int i; cin >> i; out({s}.pointGet(i));"
        elif op in POINT_UPDATES:
            body = f"int i; long long v; cin >> i >> v; {s}.{op}(i, v);"
        elif op in RANGE_UPDATES:
            names = ["x", "y"][:RANGE_UPDATES[op]]
            decl = ", ".join(names)
            reads = "".join(f" >> {nm}" for nm in names)
            body = (f"int l, r; long long {decl}; cin >> l >> r{reads}; {s}.{op}(l, r, {decl});" if names
                    else f"int l, r; cin >> l >> r; {s}.{op}(l, r);")
        else:
            kind = BRUTE_QUERIES[op][0]
            if kind == "lr":
                body = f"int l, r; cin >> l >> r; out({s}.{op}(l, r));"
            elif kind == "lrx":
                body = f"int l, r; long long x; cin >> l >> r >> x; out({s}.{op}(l, r, x));"
            elif kind == "lrkx":
                body = f"int l, r, k; long long x; cin >> l >> r >> k >> x; out({s}.{op}(l, r, k, x));"
            elif kind == "lrk":
                body = f"int l, r, k; cin >> l >> r >> k; out({s}.{op}(l, r, k));"
            else:
                body = f"int l, r; long long lo, hi; cin >> l >> r >> lo >> hi; out({s}.{op}(l, r, lo, hi));"
        lines.append(f'      else if (op == "{op}") {{ {body} }}')
    lines += ["      else { cerr << \"unknown op \" << op << '\\n'; return 1; }", "    }", "  }", "}"]
    return "\n".join(lines) + "\n"


def run_cpp(folder, ops, trials, ctor_extra, cxx):
    path = os.path.join(DIR, folder, "template.cpp")
    os.makedirs(BUILD, exist_ok=True)
    src = os.path.join(BUILD, folder[:150] + ".cpp")
    exe = src[:-4]
    open(src, "w").write(cpp_driver(folder, ops, cpp_structs(path), ctor_extra))
    comp = subprocess.run([cxx, "-std=c++17", "-O2", "-Wall", "-o", exe, src], capture_output=True, text=True)
    if comp.returncode:
        raise RuntimeError("compile error:\n" + comp.stderr[:3000])
    inp = [str(len(trials))]
    for a0, seq in trials:
        inp += [str(len(a0)), " ".join(map(str, a0)), str(len(seq))]
        inp += [f"{op} {' '.join(map(str, args))}" for op, args in seq]
    run = subprocess.run([exe], input="\n".join(inp) + "\n", capture_output=True, text=True, timeout=300)
    if run.returncode:
        raise RuntimeError(f"binary exited {run.returncode}: {run.stderr[:500]}")
    return run.stdout.split("\n")[:-1], comp.stderr.strip()


# ------------------------------------------------------------------------------------------------ main

def parse_ops(path, comment):
    m = re.search(rf"^{re.escape(comment)} @operations: (.*)$", open(path).read(), re.M)
    return m.group(1).split() if m else None


def main():
    args = sys.argv[1:]
    want_py = "--cpp" not in args
    want_cpp = "--py" not in args
    trials_n = 120
    if "--trials" in args:
        trials_n = int(args[args.index("--trials") + 1])
        args = [x for k, x in enumerate(args) if x != "--trials" and (k == 0 or args[k - 1] != "--trials")]
    filters = [x for x in args if not x.startswith("--")]
    cxx = find_cxx() if want_cpp else None
    if want_cpp and not cxx:
        print("no GCC with bits/stdc++.h found (set CXX); running Python only\n")
        want_cpp = False

    folders = sorted(f for f in os.listdir(DIR) if os.path.isdir(os.path.join(DIR, f)))
    if filters:
        folders = [f for f in folders if any(x in f for x in filters)]
    failed, total_queries = [], 0
    for folder in folders:
        py = os.path.join(DIR, folder, "template.py")
        cpp = os.path.join(DIR, folder, "template.cpp")
        ops = parse_ops(py, "#") if os.path.exists(py) else parse_ops(cpp, "//")
        unknown = [o for o in ops if o not in BRUTE_QUERIES and o not in RANGE_UPDATES and o not in POINT_UPDATES and o != "pointGet"]
        if unknown:
            failed.append(folder)
            print(f"FAIL  {folder}\n      no brute force for {unknown}: add it to BRUTE_QUERIES / RANGE_UPDATES")
            continue
        trials, ctx = make_trials(folder, ops, trials_n)
        ctor_extra = domain(folder, ops)[2]
        exp = expected_outputs(trials, ctx)
        total_queries += len(exp)
        results = []
        for lang, ok_lang, path in (("py", want_py, py), ("cpp", want_cpp, cpp)):
            if not ok_lang or not os.path.exists(path):
                continue
            try:
                if lang == "py":
                    got, warn = run_python(folder, ops, trials, ctor_extra), ""
                else:
                    got, warn = run_cpp(folder, ops, trials, ctor_extra, cxx)
                    if parse_ops(cpp, "//") != ops:
                        raise RuntimeError("template.cpp @operations differ from template.py")
                bad = first_mismatch(got, exp, trials)
                results.append((lang, bad, warn))
            except Exception as e:  # noqa: BLE001 -- report and keep going
                results.append((lang, f"{type(e).__name__}: {e}", ""))
        bad = [(lang, msg) for lang, msg, _ in results if msg]
        warns = [(lang, w) for lang, _, w in results if w]
        status = "FAIL" if bad else "PASS"
        print(f"{status}  {folder}  [{' '.join(lang for lang, _, _ in results)}]")
        for lang, msg in bad:
            print(f"      {lang}: {msg}")
        for lang, w in warns:
            print(f"      {lang} compiler warnings: {w[:400]}")
        if bad:
            failed.append(folder)
    print(f"\n{len(folders) - len(failed)}/{len(folders)} templates passed ({total_queries} brute-force answers each checked per language)")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
