"""Test every ordered-multiset template in templates/sets/<folder>/template.{py,cpp} against a brute force.

Each template's @operations header says what it supports and @values what it needs up front:
    offline       the constructor takes every value that will ever be added
    online-range  the constructor takes (lo, hi); every value added lies in [lo, hi]
    online        the constructor takes nothing
Random op sequences run on a plain sorted list and on the template, in Python and in C++; every answer must match.

    python3 test_sets.py                 # everything
    python3 test_sets.py avl blocks      # only folders whose name contains one of these
    python3 test_sets.py --py / --cpp    # one language only
    python3 test_sets.py --trials 300    # more random sequences per template (default 150)
    python3 test_sets.py --shard 3/16    # every 16th folder from the 3rd (run 16 of these side by side)
"""
import bisect
from collections import Counter
from functools import reduce
import importlib.util
import inspect
import operator
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
sys.setrecursionlimit(10000)

HERE = os.path.dirname(os.path.abspath(__file__))
DIR = os.environ.get("SETS_DIR") or os.path.join(os.path.dirname(HERE), "sets")
BUILD = os.path.join(tempfile.gettempdir(), "set-template-tests")
OPS_PER_TRIAL = 80

# op -> argument kind; results are printed for every op but add / addCount
ARG_KINDS = {
    "maxXor": "xv", "minXor": "xv", "kthXor": "xi", "countXorLtK": "xk", "countXorLteK": "xk", "countXorGtK": "xk",
    "countXorGteK": "xk", "largestXorLtK": "xk", "largestXorLteK": "xk", "smallestXorGtK": "xk", "smallestXorGteK": "xk",
    "mexXor": "xv", "sumXor": "xv", "maxXorWithVLtM": "xm", "maxXorWithVLteM": "xm", "maxXorWithVGtM": "xm",
    "maxXorWithVGteM": "xm", "minXorWithVLtM": "xm", "minXorWithVLteM": "xm", "minXorWithVGtM": "xm", "minXorWithVGteM": "xm",
    "maxXorWithVInValRange": "xlohi", "minXorWithVInValRange": "xlohi", "xorAll": "y", "shiftAll": "d",
    "clear": "", "removeInValRange": "lohi", "countDistinctInValRange": "lohi", "mode": "", "minAdjacentDiff": "", "maxGap": "",
    "add": "x", "addCount": "xc", "remove": "x", "removeCount": "xc", "removeAll": "x", "popMin": "", "popMax": "",
    "size": "", "count": "x", "sumAll": "", "countDistinct": "", "min": "", "max": "", "medianLow": "", "medianHigh": "",
    "mex": "", "sumAbsDiffToMedian": "", "kth": "k", "pop": "k", "sumSmallestK": "k", "sumLargestK": "k",
    "sumKthSmallestRange": "ij", "sumKthLargestRange": "ij", "largestLtX": "x", "largestLteX": "x", "smallestGtX": "x",
    "smallestGteX": "x", "countLtX": "x", "countLteX": "x", "countGtX": "x", "countGteX": "x", "countInValRange": "lohi", "firstIndex": "x", "lastIndex": "x",
    "sumLtX": "x", "sumLteX": "x", "sumGtX": "x", "sumGteX": "x", "sumInValRange": "lohi", "sumAbsDiffToX": "x",
}
AGG_KINDS = {"All": "", "LtX": "x", "LteX": "x", "GtX": "x", "GteX": "x", "InValRange": "lohi", "SmallestK": "k", "LargestK": "k",
             "KthSmallestRange": "ij", "KthLargestRange": "ij"}
ARG_KINDS.update({agg + "Of" + suf: kind for agg in ("xor", "or", "and") for suf, kind in AGG_KINDS.items()})
NO_RESULT = {"add", "addCount", "clear", "xorAll", "shiftAll"}
# ops that need the values to be numbers; a template tagged "@keys: any" is also run with tuple / pair keys on the rest
NUMERIC_OPS = {"sumAll", "sumSmallestK", "sumLargestK", "sumKthSmallestRange", "sumKthLargestRange", "sumLtX", "sumLteX",
               "sumGtX", "sumGteX", "sumInValRange", "sumAbsDiffToX", "sumAbsDiffToMedian", "mex",
               "minAdjacentDiff", "maxGap"} | {op for op, k in ARG_KINDS.items() if k in ("xv", "xi", "xk", "xm", "xlohi", "y")} | {
    op for op in ARG_KINDS if op.startswith(("xorOf", "orOf", "andOf"))}
VALUE_ARGS = {"x": (0,), "xc": (0,), "lohi": (0, 1)}  # which arguments are values (the rest are counts / ranks)


def key(v):  # an order-preserving int -> tuple map, so the int brute force still gives the answers
    return (v // 7, v % 7)


def unkey(t):
    return t[0] * 7 + t[1]
ERR = "ERR"  # the op must raise IndexError (Python) / throw out_of_range (C++)


# ------------------------------------------------------------------------------------------------ brute force

def brute(a, op, args):
    """Apply op to the sorted list a (in place) and return its result."""
    n = len(a)
    if op == "clear":
        a.clear()
        return None
    if op == "mode":  # any most frequent value is right: ("mode", its count, the values with it)
        if not a:
            return None
        cnt = Counter(a)
        f = max(cnt.values())
        return ("mode", f, frozenset(v for v, k in cnt.items() if k == f))
    if op == "xorAll":
        a[:] = sorted(v ^ args[0] for v in a)
        return None
    if op == "shiftAll":
        a[:] = [v + args[0] for v in a]
        return None
    if ARG_KINDS[op] in ("xv", "xi", "xk", "xm", "xlohi"):  # questions about v ^ x
        x = args[0]
        xs = sorted(v ^ x for v in a)
        if op == "maxXor": return xs[-1] if xs else None
        if op == "minXor": return xs[0] if xs else None
        if op == "kthXor": return xs[args[1]] if 0 <= args[1] < n else ERR
        if op == "mexXor":
            have, m = set(xs), 0
            while m in have:
                m += 1
            return m
        if op == "sumXor": return sum(xs)
        if op.startswith(("countXor", "largestXor", "smallestXor")):
            k = args[1]
            rel = op[-3:-1] if op[-3:-1] in ("Lt", "Gt") else op[-4:-1]
            keep = [w for w in xs if {"Lt": w < k, "Lte": w <= k, "Gt": w > k, "Gte": w >= k}[rel]]
            if op.startswith("count"): return len(keep)
            if not keep: return None
            return keep[-1] if op.startswith("largest") else keep[0]
        if op.endswith("InValRange"):
            lo, hi = args[1], args[2]
            keep = [v ^ x for v in a if lo <= v <= hi]
        else:
            m = args[1]
            rel = op[len("maxXorWithV"):-1]
            keep = [v ^ x for v in a if {"Lt": v < m, "Lte": v <= m, "Gt": v > m, "Gte": v >= m}[rel]]
        if not keep: return None
        return max(keep) if op.startswith("max") else min(keep)
    if op.startswith(("xorOf", "orOf", "andOf")):  # bitwise aggregates (xor: copies count)
        agg, suf = op.split("Of", 1)
        f, ident = {"xor": (operator.xor, 0), "or": (operator.or_, 0), "and": (operator.and_, -1)}[agg]
        if suf in ("SmallestK", "LargestK"):
            k = args[0]
            if not 0 <= k <= n:
                return ERR
            vals = a[:k] if suf == "SmallestK" else a[n - k:]
        elif suf.startswith("Kth"):
            i, j = args
            if not 1 <= i <= j <= n:
                return ERR
            vals = (a if suf == "KthSmallestRange" else a[::-1])[i - 1:j]
        elif suf == "InValRange":
            vals = [v for v in a if args[0] <= v <= args[1]]
        elif suf == "All":
            vals = a
        else:
            x = args[0]
            vals = [v for v in a if {"LtX": v < x, "LteX": v <= x, "GtX": v > x, "GteX": v >= x}[suf]]
        return reduce(f, vals, ident)
    if op == "minAdjacentDiff":
        return min(a[i + 1] - a[i] for i in range(n - 1)) if n >= 2 else None
    if op == "maxGap":
        u = sorted(set(a))
        return max(u[i + 1] - u[i] for i in range(len(u) - 1)) if len(u) >= 2 else None
    if op == "countDistinctInValRange":
        lo, hi = args
        return len({v for v in a if lo <= v <= hi})
    if op == "removeInValRange":
        lo, hi = args
        keep = [v for v in a if not lo <= v <= hi]
        removed = len(a) - len(keep)
        a[:] = keep
        return removed
    if op == "add":
        bisect.insort(a, args[0])
        return None
    if op == "addCount":
        for _ in range(max(0, args[1])):
            bisect.insort(a, args[0])
        return None
    if op in ("remove", "removeCount", "removeAll"):
        x = args[0]
        have = bisect.bisect_right(a, x) - bisect.bisect_left(a, x)
        k = {"remove": min(1, have), "removeCount": max(0, min(args[1] if op == "removeCount" else 0, have)), "removeAll": have}[op]
        i = bisect.bisect_left(a, x)
        del a[i:i + k]
        return k
    if op == "pop": return a.pop(args[0]) if 0 <= args[0] < n else ERR
    if op in ("popMin", "popMax"):
        return (a.pop(0) if op == "popMin" else a.pop()) if a else None
    if op == "size": return n
    if op == "count": return bisect.bisect_right(a, args[0]) - bisect.bisect_left(a, args[0])
    if op == "sumAll": return sum(a)
    if op == "countDistinct": return len(set(a))  # (fine: long trials ask rarely)
    if op == "min": return a[0] if a else None
    if op == "max": return a[-1] if a else None
    if op == "medianLow": return a[(n + 1) // 2 - 1] if a else None
    if op == "medianHigh": return a[n // 2] if a else None
    if op == "mex":
        s, m = set(a), 0
        while m in s:
            m += 1
        return m
    if op == "sumAbsDiffToMedian": return sum(abs(v - a[(n + 1) // 2 - 1]) for v in a) if a else 0
    if op == "kth": return a[args[0]] if 0 <= args[0] < n else ERR
    if op == "sumSmallestK": return sum(a[:args[0]]) if 0 <= args[0] <= n else ERR
    if op == "sumLargestK": return sum(a[n - args[0]:]) if 0 <= args[0] <= n else ERR
    if op in ("sumKthSmallestRange", "sumKthLargestRange"):
        i, j = args
        if not 1 <= i <= j <= n:
            return ERR
        b = a if op == "sumKthSmallestRange" else a[::-1]
        return sum(b[i - 1:j])
    x = args[0] if args else None
    if op == "largestLtX": i = bisect.bisect_left(a, x); return a[i - 1] if i else None
    if op == "largestLteX": i = bisect.bisect_right(a, x); return a[i - 1] if i else None
    if op == "smallestGtX": i = bisect.bisect_right(a, x); return a[i] if i < n else None
    if op == "smallestGteX": i = bisect.bisect_left(a, x); return a[i] if i < n else None
    lt = bisect.bisect_left(a, x) if x is not None else 0
    le = bisect.bisect_right(a, x) if x is not None else 0
    if op == "countLtX": return lt
    if op == "firstIndex": return lt if le > lt else -1
    if op == "lastIndex": return le - 1 if le > lt else -1
    if op == "countLteX": return le
    if op == "countGtX": return n - le
    if op == "countGteX": return n - lt
    if op == "sumLtX": return sum(a[:lt])
    if op == "sumLteX": return sum(a[:le])
    if op == "sumGtX": return sum(a[le:])
    if op == "sumGteX": return sum(a[lt:])
    if op == "sumAbsDiffToX": return x * lt - sum(a[:lt]) + sum(a[lt:]) - x * (n - lt)
    if op in ("countInValRange", "sumInValRange"):
        if args[0] > args[1]:
            return 0
        i, j = bisect.bisect_left(a, args[0]), bisect.bisect_right(a, args[1])
        return j - i if op == "countInValRange" else sum(a[i:j])
    raise KeyError(op)


def norm(v):
    if isinstance(v, tuple) and v and v[0] == "mode":
        return v  # checked by first_mismatch
    if isinstance(v, tuple):  # (value, count) from mode()
        return f"{norm(v[0])} {norm(v[1])}"
    return "None" if v is None else v if v == ERR else str(int(v))


# ------------------------------------------------------------------------------------------------ trials

def make_trials(ops, values_kind, trials, max_range=None):
    """[(ctor args, [(op, args)])]. Values mostly small (lots of duplicates, 0..few for mex) with some negatives; a
    third of the trials use huge values too. Offline trials pass every value the sequence will add."""
    updates = [o for o in ops if o in ("add", "addCount", "remove", "removeCount", "removeAll", "popMin", "popMax", "pop", "clear", "removeInValRange", "xorAll", "shiftAll")]
    queries = [o for o in ops if o not in updates]
    out = []
    for t in range(trials):
        rng = random.Random(t)
        big = t % 3 == 0 and max_range is None  # (a structure with an array over [lo, hi] can't take a huge range)
        long_trial = t % 25 == 7  # thousands of distinct values: block splits, deep trees, multi-block walks
        lo, hi = (-10**12, 10**12) if big else (-rng.randint(0, 6), rng.randint(4, 16))
        if long_trial:
            lo, hi = (-10**12, 10**12) if big else (-50, 5000)
        bits = None
        if values_kind == "online-bits":  # the trie: values in [0, 2^bits)
            bits = 30 if big else 13 if long_trial else rng.randint(2, 5)
            lo, hi = 0, (1 << bits) - 1
        pool = [rng.randint(lo, hi) for _ in range(4)] if big else []
        pool += [rng.randint(0, 6) for _ in range(6)] + [rng.randint(lo, hi) for _ in range(3)]
        if long_trial:
            pool += list(range(0, 1500)) + [rng.randint(lo, hi) for _ in range(1500)]
        pool = [v for v in pool if lo <= v <= hi]
        seq, added = [], set()
        drift = 0  # how far shiftAll has moved the values: value arguments follow it
        for _ in range(4000 if long_trial else OPS_PER_TRIAL):
            op = rng.choice(updates) if updates and rng.random() < (0.75 if long_trial else 0.55) else rng.choice(queries)
            if op == "clear" and rng.random() > (0.02 if long_trial else 0.15):  # rare, so the set grows between clears
                op = "add"
            if op in ("add", "addCount") and rng.random() < 0.3:
                op = "add"
            if long_trial and op in updates and "add" in ops and rng.random() < 0.6:
                op = "add"  # grow past the block size
            kind = ARG_KINDS[op]
            x = rng.choice(pool) if rng.random() < 0.8 else rng.randint(lo - 3, hi + 3)
            if drift and rng.random() < 0.8:
                x += drift
            if kind == "x":
                if op in ("add",):
                    x = rng.choice(pool) + drift
                args = [x]
            elif kind == "xc":
                args = [rng.choice(pool) + drift if op == "addCount" else x, rng.randint(-1, 3)]
            elif kind == "k":
                args = [rng.randint(-1, 3000 if long_trial else 12)]
            elif kind == "ij":
                top = 3000 if long_trial else 12
                args = sorted((rng.randint(-1, top), rng.randint(-1, top)))
                if rng.random() < 0.2:
                    args = args[::-1]
            elif kind in ("xv", "y"):
                args = [rng.choice(pool) if rng.random() < 0.5 else rng.randint(0, hi)]
            elif kind in ("xk", "xm"):
                args = [rng.randint(0, hi), rng.choice(pool) + rng.randint(-1, 1) if rng.random() < 0.7 else rng.randint(lo - 3, hi + 3)]
            elif kind == "xi":
                args = [rng.randint(0, hi), rng.randint(-1, 3000 if long_trial else 12)]
            elif kind == "xlohi":
                b = sorted((rng.choice(pool) + rng.randint(-1, 1), rng.randint(lo - 3, hi + 3)))
                args = [rng.randint(0, hi)] + (b[::-1] if rng.random() < 0.15 else b)
            elif kind == "d":
                args = [rng.randint(-3, 3) if rng.random() < 0.9 else rng.randint(lo - hi, hi - lo)]
                drift += args[0]
            elif kind == "lohi":
                args = sorted((rng.choice(pool) + drift, rng.choice(pool) + drift))
                if rng.random() < 0.2:
                    args = args[::-1]
            else:
                args = []
            if op in ("add", "addCount"):
                added.add(args[0])
            seq.append((op, args))
        ctor = {"offline": (sorted(added | set(rng.sample(pool, min(3, len(pool))))),),
                "online-range": (lo, hi), "online": (), "online-bits": (bits,)}[values_kind]
        out.append((ctor, seq))
    return out


def expected(trials, distinct=False):
    """distinct: a set without duplicates (adding a value already present does nothing), as in fastset/distinct.*"""
    exp = []
    for _, seq in trials:
        a = []
        for op, args in seq:
            if distinct and op == "add" and args[0] in a:
                continue  # (add has no result to check)
            r = brute(a, op, args)
            if op not in NO_RESULT:
                exp.append(norm(r))
    return exp


# ------------------------------------------------------------------------------------------------ runners

def parse_header(path, cm):
    text = open(path).read()
    ops = re.search(rf"^{re.escape(cm)} @operations: (.*)$", text, re.M).group(1).split()
    values = re.search(rf"^{re.escape(cm)} @values: (.*)$", text, re.M).group(1).strip()
    keys = re.search(rf"^{re.escape(cm)} @keys: (.*)$", text, re.M).group(1).strip()
    return ops, values, keys


def run_python(path, ops, trials, keyed=False):
    spec = importlib.util.spec_from_file_location("set_" + re.sub(r"\W", "_", path), path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    classes = [c for _, c in inspect.getmembers(mod, inspect.isclass) if c.__module__ == mod.__name__]
    cls = max(classes, key=lambda c: sum(hasattr(c, o) for o in ops))
    missing = [o for o in ops if not hasattr(cls, o)]
    if missing:
        raise RuntimeError(f"no method for {missing}")
    out = []
    for ctor, seq in trials:
        s = cls(*([list(map(key, c)) for c in ctor] if keyed else ctor))
        for op, args in seq:
            if keyed:
                args = [key(a) if k in VALUE_ARGS.get(ARG_KINDS[op], ()) else a for k, a in enumerate(args)]
            try:
                r = getattr(s, op)(*args)
            except IndexError:
                r = ERR
            if keyed and isinstance(r, tuple):
                r = (unkey(r[0]), r[1]) if op == "mode" else unkey(r)
            if op not in NO_RESULT:
                out.append(norm(r))
    return out


def find_cxx():
    cands = [os.environ["CXX"]] if os.environ.get("CXX") else [f"g++-{v}" for v in range(15, 10, -1)] + ["g++"]
    for c in cands:
        exe = shutil.which(c) or (c if os.path.exists(c) else None)
        if exe and subprocess.run([exe, "-std=c++17", "-x", "c++", "-fsyntax-only", "-"], input="#include <bits/stdc++.h>\n",
                                  capture_output=True, text=True).returncode == 0:
            return exe
    return None


def run_cpp(path, ops, values_kind, trials, cxx, keyed=False):
    text = open(path).read()
    names = re.findall(r"^template <typename T>\nstruct (\w+) \{", text, re.M)
    name = names[-1]
    lines = ["#include <bits/stdc++.h>", "using namespace std;", f'#include "{path}"', f"template struct {name}<int>;",
             "void out(long long v) { cout << v << '\\n'; }",
             "void out(optional<long long> v) { if (v) cout << *v << '\\n'; else cout << \"None\\n\"; }",
             "using P = pair<long long, long long>;",
             "P key(long long v) { long long q = v >= 0 ? v / 7 : -((-v + 6) / 7); return {q, v - 7 * q}; }",
             "void out(const P& p) { cout << p.first * 7 + p.second << '\\n'; }",
             "void out(optional<P> v) { if (v) out(*v); else cout << \"None\\n\"; }",

             "int main() {", "  ios::sync_with_stdio(false); cin.tie(nullptr);", "  int cases; cin >> cases;", "  while (cases--) {"]
    K = "P" if keyed else "long long"
    # mode() returns (value, count); with int keys that type is the same as optional<P>, so each driver gets only its own
    lines.insert(lines.index("int main() {"), "void out(optional<pair<P, long long>> v) { if (v) cout << v->first.first * 7 + v->first.second << ' ' << v->second << '\\n'; else cout << \"None\\n\"; }"
                 if keyed else "void outMode(optional<pair<long long, long long>> v) { if (v) cout << v->first << ' ' << v->second << '\\n'; else cout << \"None\\n\"; }")
    if values_kind == "offline":
        lines += [f"    int m; cin >> m; vector<{K}> vals(m); for (auto& v : vals) {{ long long x; cin >> x; v = {'key(x)' if keyed else 'x'}; }}",
                  f"    {name}<{K}> s(vals);"]
    elif values_kind == "online-range":
        lines += ["    long long lo, hi; cin >> lo >> hi;", f"    {name}<{K}> s(lo, hi);"]
    elif values_kind == "online-bits":
        lines += ["    int bits; cin >> bits;", f"    {name}<{K}> s(bits);"]
    else:
        lines += [f"    {name}<{K}> s;"]
    if "resetPool" in text:
        lines.insert(-1, f"    {name}<{K}>::resetPool();")
    lines += ["    int q; cin >> q;", "    while (q--) {", "      string op; cin >> op;", "      if (false) {}"]
    for op in ops:
        kind = ARG_KINDS[op]
        names_ = {"d": ["d"], "x": ["x"], "xc": ["x", "c"], "k": ["k"], "ij": ["i", "j"], "lohi": ["lo", "hi"], "": [], "xv": ["x"], "y": ["y"],
                  "xi": ["x", "i"], "xk": ["x", "k"], "xm": ["x", "m"], "xlohi": ["x", "lo", "hi"]}[kind]
        decl = f"long long {', '.join(names_)}; cin >> {' >> '.join(names_)}; " if names_ else ""
        call = f"s.{op}({', '.join(f'key({a})' if keyed and k in VALUE_ARGS.get(kind, ()) else a for k, a in enumerate(names_))})"
        printer = "outMode" if op == "mode" and not keyed else "out"
        body = decl + (f"{call};" if op in NO_RESULT else f'try {{ {printer}({call}); }} catch (const out_of_range&) {{ cout << "ERR\\n"; }}')
        lines.append(f'      else if (op == "{op}") {{ {body} }}')
    lines += ["      else { cerr << \"unknown op \" << op << '\\n'; return 1; }", "    }", "  }", "}"]
    os.makedirs(BUILD, exist_ok=True)
    src = os.path.join(BUILD, os.path.basename(os.path.dirname(path)) + "__" + os.path.basename(path)[:-4] + ("__keyed" if keyed else "") + ".cpp")
    exe = src[:-4]
    open(src, "w").write("\n".join(lines) + "\n")
    comp = subprocess.run([cxx, "-std=c++17", "-O2", "-Wall", "-o", exe, src], capture_output=True, text=True)
    if comp.returncode:
        raise RuntimeError("compile error:\n" + comp.stderr[:3000])
    inp = [str(len(trials))]
    for ctor, seq in trials:
        if values_kind == "offline":
            inp.append(f"{len(ctor[0])} " + " ".join(map(str, ctor[0])))
        elif values_kind == "online-range":
            inp.append(f"{ctor[0]} {ctor[1]}")
        elif values_kind == "online-bits":
            inp.append(str(ctor[0]))
        inp.append(str(len(seq)))
        inp += [f"{op} {' '.join(map(str, args))}" for op, args in seq]
    run = subprocess.run([exe], input="\n".join(inp) + "\n", capture_output=True, text=True, timeout=300)
    if run.returncode:
        raise RuntimeError(f"binary exited {run.returncode}: {run.stderr[:500]}")
    return run.stdout.split("\n")[:-1], comp.stderr.strip()


def first_mismatch(got, exp, trials):
    if len(got) != len(exp):
        return f"{len(got)} outputs, expected {len(exp)}"
    for k, (g, e) in enumerate(zip(got, exp)):
        if isinstance(e, tuple):  # mode: any value with the top count
            parts = g.split()
            if len(parts) == 2 and int(parts[1]) == e[1] and int(parts[0]) in e[2]:
                continue
        if g != e:
            seen = 0
            for t, (ctor, seq) in enumerate(trials):
                for step, (op, args) in enumerate(seq):
                    if op in NO_RESULT:
                        continue
                    if seen == k:
                        return f"trial {t} (ctor {ctor}), step {step}: {op}{tuple(args)} -> got {g}, expected {e}; sequence so far {seq[:step + 1]}"
                    seen += 1
    return None


def main():
    args = sys.argv[1:]
    want_py, want_cpp = "--cpp" not in args, "--py" not in args
    trials_n = 150
    if "--trials" in args:
        trials_n = int(args[args.index("--trials") + 1])
    shard = None
    if "--shard" in args:
        i, n = map(int, args[args.index("--shard") + 1].split("/"))
        shard = (i, n)
    filters = [a for k, a in enumerate(args) if not a.startswith("--") and not a.isdigit() and (k == 0 or args[k - 1] != "--shard")]
    cxx = find_cxx() if want_cpp else None
    if want_cpp and not cxx:
        print("no GCC with bits/stdc++.h found (set CXX); running Python only\n")
        want_cpp = False
    folders = sorted(f for f in os.listdir(DIR) if os.path.isdir(os.path.join(DIR, f)))
    if filters:
        folders = [f for f in folders if any(x in f for x in filters)]
    if shard:
        folders = folders[shard[0]::shard[1]]
    failed, total = [], 0
    for folder in folders:
        results = []
        for stem, lang, ok, cm in (("template", "py", want_py, "#"), ("template", "cpp", want_cpp, "//"),
                                   ("distinct", "py", want_py, "#"), ("distinct", "cpp", want_cpp, "//")):
            path = os.path.join(DIR, folder, f"{stem}.{lang}")
            if not ok or not os.path.exists(path):
                continue
            ops, values_kind, keys = parse_header(path, cm)
            if stem == "distinct":  # a no-duplicates variant (fastset/distinct.*): set semantics in the brute force
                trials = make_trials(ops, values_kind, trials_n, 10**5)
                exp = expected(trials, distinct=True)
                total += len(exp)
                try:
                    got = run_python(path, ops, trials) if lang == "py" else run_cpp(path, ops, values_kind, trials, cxx)[0]
                    results.append((lang + "(distinct)", first_mismatch(got, exp, trials)))
                except Exception as e:  # noqa: BLE001
                    results.append((lang + "(distinct)", f"{type(e).__name__}: {e}"))
                continue
            # every template with ints; "@keys: any" ones again with tuple (Python) / pair (C++) keys on the ops that
            # only compare values
            passes = [(lang, ops, False)] + ([(lang + "(tuples)" if lang == "py" else lang + "(pairs)",
                                                [o for o in ops if o not in NUMERIC_OPS], True)] if keys == "any" else [])
            for label, ops_, keyed in passes:
                trials = make_trials(ops_, values_kind, trials_n, 10**5 if folder.startswith("fastset") else None)
                exp = expected(trials)
                total += len(exp)
                try:
                    got = (run_python(path, ops_, trials, keyed) if lang == "py"
                           else run_cpp(path, ops_, values_kind, trials, cxx, keyed)[0])
                    results.append((label, first_mismatch(got, exp, trials)))
                except Exception as e:  # noqa: BLE001
                    results.append((label, f"{type(e).__name__}: {e}"))
        bad = [(lang, msg) for lang, msg in results if msg]
        print(f"{'FAIL' if bad else 'PASS'}  {folder}  [{' '.join(lang for lang, _ in results)}]")
        for lang, msg in bad:
            print(f"      {lang}: {msg[:1500]}")
        if bad:
            failed.append(folder)
    print(f"\n{len(failed)} failed across {len(folders)} templates" if failed
          else f"\nall {len(folders)} templates passed ({total} brute-force answers checked)")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
