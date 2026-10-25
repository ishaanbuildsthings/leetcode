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
"""
import bisect
import importlib.util
import inspect
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
DIR = os.path.join(os.path.dirname(HERE), "sets")
BUILD = os.path.join(tempfile.gettempdir(), "set-template-tests")
OPS_PER_TRIAL = 80

# op -> argument kind; results are printed for every op but add / addCount
ARG_KINDS = {
    "clear": "",
    "add": "x", "addCount": "xc", "remove": "x", "removeCount": "xc", "removeAll": "x", "popMin": "", "popMax": "",
    "size": "", "count": "x", "sumAll": "", "countDistinct": "", "min": "", "max": "", "medianLow": "", "medianHigh": "",
    "mex": "", "sumAbsDiffToMedian": "", "kth": "k", "pop": "k", "sumSmallestK": "k", "sumLargestK": "k",
    "sumKthSmallestRange": "ij", "sumKthLargestRange": "ij", "largestLtX": "x", "largestLteX": "x", "smallestGtX": "x",
    "smallestGteX": "x", "countLtX": "x", "countLteX": "x", "countGtX": "x", "countGteX": "x", "countInValRange": "lohi", "firstIndex": "x", "lastIndex": "x",
    "sumLtX": "x", "sumLteX": "x", "sumGtX": "x", "sumGteX": "x", "sumInValRange": "lohi", "sumAbsDiffToX": "x",
}
NO_RESULT = {"add", "addCount", "clear"}
# ops that need the values to be numbers; a template tagged "@keys: any" is also run with tuple / pair keys on the rest
NUMERIC_OPS = {"sumAll", "sumSmallestK", "sumLargestK", "sumKthSmallestRange", "sumKthLargestRange", "sumLtX", "sumLteX",
               "sumGtX", "sumGteX", "sumInValRange", "sumAbsDiffToX", "sumAbsDiffToMedian", "mex"}
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
    return "None" if v is None else v if v == ERR else str(int(v))


# ------------------------------------------------------------------------------------------------ trials

def make_trials(ops, values_kind, trials, max_range=None):
    """[(ctor args, [(op, args)])]. Values mostly small (lots of duplicates, 0..few for mex) with some negatives; a
    third of the trials use huge values too. Offline trials pass every value the sequence will add."""
    updates = [o for o in ops if o in ("add", "addCount", "remove", "removeCount", "removeAll", "popMin", "popMax", "pop", "clear")]
    queries = [o for o in ops if o not in updates]
    out = []
    for t in range(trials):
        rng = random.Random(t)
        big = t % 3 == 0 and max_range is None  # (a structure with an array over [lo, hi] can't take a huge range)
        long_trial = t % 25 == 7  # thousands of distinct values: block splits, deep trees, multi-block walks
        lo, hi = (-10**12, 10**12) if big else (-rng.randint(0, 6), rng.randint(4, 16))
        if long_trial:
            lo, hi = (-10**12, 10**12) if big else (-50, 5000)
        pool = [rng.randint(lo, hi) for _ in range(4)] if big else []
        pool += [rng.randint(0, 6) for _ in range(6)] + [rng.randint(lo, hi) for _ in range(3)]
        if long_trial:
            pool += list(range(0, 1500)) + [rng.randint(lo, hi) for _ in range(1500)]
        pool = [v for v in pool if lo <= v <= hi]
        seq, added = [], set()
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
            if kind == "x":
                if op in ("add",):
                    x = rng.choice(pool)
                args = [x]
            elif kind == "xc":
                args = [rng.choice(pool) if op == "addCount" else x, rng.randint(-1, 3)]
            elif kind == "k":
                args = [rng.randint(-1, 3000 if long_trial else 12)]
            elif kind == "ij":
                top = 3000 if long_trial else 12
                args = sorted((rng.randint(-1, top), rng.randint(-1, top)))
                if rng.random() < 0.2:
                    args = args[::-1]
            elif kind == "lohi":
                args = sorted((rng.choice(pool), rng.choice(pool)))
                if rng.random() < 0.2:
                    args = args[::-1]
            else:
                args = []
            if op in ("add", "addCount"):
                added.add(args[0])
            seq.append((op, args))
        ctor = {"offline": (sorted(added | set(rng.sample(pool, min(3, len(pool))))),),
                "online-range": (lo, hi), "online": ()}[values_kind]
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
                r = unkey(r)
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
    if values_kind == "offline":
        lines += [f"    int m; cin >> m; vector<{K}> vals(m); for (auto& v : vals) {{ long long x; cin >> x; v = {'key(x)' if keyed else 'x'}; }}",
                  f"    {name}<{K}> s(vals);"]
    elif values_kind == "online-range":
        lines += ["    long long lo, hi; cin >> lo >> hi;", f"    {name}<{K}> s(lo, hi);"]
    else:
        lines += [f"    {name}<{K}> s;"]
    if "resetPool" in text:
        lines.insert(-1, f"    {name}<{K}>::resetPool();")
    lines += ["    int q; cin >> q;", "    while (q--) {", "      string op; cin >> op;", "      if (false) {}"]
    for op in ops:
        kind = ARG_KINDS[op]
        names_ = {"x": ["x"], "xc": ["x", "c"], "k": ["k"], "ij": ["i", "j"], "lohi": ["lo", "hi"], "": []}[kind]
        decl = f"long long {', '.join(names_)}; cin >> {' >> '.join(names_)}; " if names_ else ""
        call = f"s.{op}({', '.join(f'key({a})' if keyed and k in VALUE_ARGS.get(kind, ()) else a for k, a in enumerate(names_))})"
        body = decl + (f"{call};" if op in NO_RESULT else f'try {{ out({call}); }} catch (const out_of_range&) {{ cout << "ERR\\n"; }}')
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
    filters = [a for a in args if not a.startswith("--") and not a.isdigit()]
    cxx = find_cxx() if want_cpp else None
    if want_cpp and not cxx:
        print("no GCC with bits/stdc++.h found (set CXX); running Python only\n")
        want_cpp = False
    folders = sorted(f for f in os.listdir(DIR) if os.path.isdir(os.path.join(DIR, f)))
    if filters:
        folders = [f for f in folders if any(x in f for x in filters)]
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
