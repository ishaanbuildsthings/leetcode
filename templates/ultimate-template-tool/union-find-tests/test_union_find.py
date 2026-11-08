"""Tests every union find template (templates/ultimate-template-tool/union-find/*): random op scripts run on the Python
template are checked against a brute force (component labels, kept the slow way), then the same scripts are fed to the
C++ template (built with sanitizers), which has to print exactly what the Python one did.

    python3 test_union_find.py              # every template, Python then C++
    python3 test_union_find.py --py         # Python only
    python3 test_union_find.py rollback     # folders whose name contains one of these
    python3 test_union_find.py --budget 150 # stop starting C++ builds after this many seconds (rerun to continue)

hdlt (fully dynamic connectivity) gets its own scripts: edges added and removed at random, many parallel copies of the
same pair among them, checked against connectivity recomputed from the live edges, then replayed on the C++ one.
"""
import concurrent.futures
import os
import random
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
DIR = os.path.join(os.path.dirname(HERE), "union-find")
CACHE = os.environ.get("UF_CACHE", "/tmp/uf-test")
sys.path.insert(0, HERE)
from gen_union_find import CLASS  # noqa: E402

SCRIPTS = 8


def parse(name):
    mode, *feats = name.split("-")
    return mode, set(feats)


def load_py(name):
    text = open(os.path.join(DIR, name, "template.py")).read()
    k = text.index("\nclass ")
    head = re.sub(r"^( +)# (return )", r"\1\2", text[:k], flags=re.M)  # (the merge example switched on)
    ns = {}
    exec(head + text[k:], ns)
    return ns


# ------------------------------------------------------------------------------------------------ brute force
class Brute:
    def __init__(self, vals):
        n = len(vals)
        self.vals = list(vals)
        self.comp = list(range(n))  # a label per element
        self.val = [0] * n  # the potentials, made consistent
        self.edges = {i: 0 for i in range(n)}
        self.hist = [self.comp[:]]  # comp after each unite call
        self.snaps = []

    def n(self):
        return len(self.comp)

    def members(self, i):
        return [k for k in range(self.n()) if self.comp[k] == self.comp[i]]

    def unite(self, i, j, w, roll):
        if roll:
            self.snaps.append((self.comp[:], self.val[:], dict(self.edges)))
        merged = self.comp[i] != self.comp[j]
        if not merged:
            self.edges[self.comp[i]] += 1
        else:
            ci, cj, shift = self.comp[i], self.comp[j], self.val[i] + w - self.val[j]
            for k in range(self.n()):
                if self.comp[k] == cj:
                    self.comp[k] = ci
                    self.val[k] += shift
            self.edges[ci] += self.edges.pop(cj) + 1
        self.hist.append(self.comp[:])
        return merged

    def rollback(self):
        comp, val, edges = self.snaps.pop()
        m = len(comp)
        self.comp = comp + list(range(m, self.n()))  # (elements added since: back on their own)
        self.val = val + [0] * (self.n() - m)
        self.edges = edges
        for k in range(m, self.n()):
            self.edges[k] = 0

    def add(self, v):
        k = self.n()
        self.vals.append(v)
        self.comp.append(k)
        self.val.append(0)
        self.edges[k] = 0
        return k

    def first_time(self, i, j):
        if i == j:
            return 0
        if self.comp[i] != self.comp[j]:
            return -1
        for t, c in enumerate(self.hist):
            if i < len(c) and j < len(c) and c[i] == c[j]:
                return t
        raise AssertionError("never connected")


def fmt(x):
    if isinstance(x, bool):
        return "1" if x else "0"
    if x is None:
        return "none"
    if isinstance(x, (int, str)):
        return str(x)
    if isinstance(x, tuple):
        return " ".join(map(fmt, x))
    if x and isinstance(x[0], list):
        return "|".join(" ".join(map(str, g)) for g in x)
    if isinstance(x, list) and all(isinstance(g, list) for g in x):
        return "|".join(" ".join(map(str, g)) for g in x)
    return " ".join(map(str, x))


def script(name, seed):
    """(input text for the C++ driver, the Python template's printed lines), every answer checked on the way"""
    mode, feats = parse(name)
    has = feats.__contains__
    rnd = random.Random(seed)
    ns = load_py(name)
    n0 = rnd.randint(0, 6) if has("grow") else rnd.randint(1, 9)
    vals = [rnd.randint(-20, 20) for _ in range(n0)]
    cls = ns[CLASS[mode]]
    d = cls(vals, ns["baseFn"], ns["combine"]) if has("merge") else cls(vals)
    b = Brute(vals)
    lines, outs = [], []
    roll = mode == "rollback"
    ops = ["unite"] * 6 + ["find", "areUnioned", "size", "numComponents", "largestSize", "roots", "sizes", "groups", "elementsInGroup"]
    if mode == "nocompress":
        ops += ["uniteAUnderB"] * 2
    if roll:
        ops += ["rollback"] * 3 + ["checkpoint", "rollbackTo"]
    if has("values"):
        ops += ["componentSum", "componentMin", "componentMax"]
    if has("merge"):
        ops += ["componentData"]
    if has("edges"):
        ops += ["edgeCount", "isTree"]
    if has("potential"):
        ops += ["diff"] * 2
    if has("time"):
        ops += ["firstConnectedTime", "connectedAt"]
    if has("grow"):
        ops += ["add"] * 2
    for _ in range(rnd.randint(40, 160)):
        n = b.n()
        op = rnd.choice(ops)
        if n == 0 and op not in ("add", "numComponents", "largestSize", "roots", "sizes", "groups"):
            op = "add" if has("grow") else "numComponents"
        if op in ("rollback",) and not b.snaps:
            op = "unite" if n else "numComponents"
        i, j = (rnd.randrange(n), rnd.randrange(n)) if n else (0, 0)
        w = rnd.randint(-9, 9)
        what = f"{op} {i} {j}"
        members = b.members(i) if n else []
        mv = [b.vals[k] for k in members]
        if op in ("unite", "uniteAUnderB"):
            what += f" {w}" if has("potential") else ""
            got = getattr(d, op + ("Weighted" if has("potential") else ""))(*((i, j, w) if has("potential") else (i, j)))
            want = b.unite(i, j, w, roll and op == "unite")
            assert (got is not None and got is not False) == want, (name, what, got, want)
        elif op == "find":
            what = f"find {i}"
            got = d.find(i)
            assert b.comp[got] == b.comp[i] and d.find(got) == got, (name, what)
        elif op == "areUnioned":
            got = d.areUnioned(i, j)
            assert got == (b.comp[i] == b.comp[j]), (name, what)
        elif op == "size":
            what, got = f"size {i}", d.size(i)
            assert got == len(members), (name, what, got)
        elif op == "numComponents":
            what, got = op, d.numComponents()
            assert got == len(set(b.comp)), (name, what, got)
        elif op == "largestSize":
            what, got = op, d.largestSize()
            assert got == max([b.comp.count(c) for c in set(b.comp)] or [0]), (name, what, got)
        elif op == "roots":
            what, got = op, d.roots()
            assert len(got) == len(set(b.comp)) == len({b.comp[r] for r in got}), (name, what, got)
        elif op == "sizes":
            what, got = op, d.sizes()
            assert got == sorted((b.comp.count(c) for c in set(b.comp)), reverse=True), (name, what, got)
        elif op == "groups":
            what, got = op, d.groups()
            want = sorted(sorted(b.vals[k] for k in range(n) if b.comp[k] == c) for c in set(b.comp))
            assert sorted(sorted(g) for g in got if g) == want, (name, what, got)
        elif op == "elementsInGroup":
            what, got = f"elementsInGroup {i}", d.elementsInGroup(i)
            assert sorted(got) == sorted(mv), (name, what, got)
            if has("members"):
                assert got[0] == b.vals[i], (name, what, got)
        elif op in ("componentSum", "componentMin", "componentMax"):
            what, got = f"{op} {i}", getattr(d, op)(i)
            assert got == {"componentSum": sum, "componentMin": min, "componentMax": max}[op](mv), (name, what, got)
        elif op == "componentData":
            what, got = f"componentData {i}", d.componentData(i)
            assert got == (sum(mv), max(mv)), (name, what, got)
        elif op == "edgeCount":
            what, got = f"edgeCount {i}", d.edgeCount(i)
            assert got == b.edges[b.comp[i]], (name, what, got)
        elif op == "isTree":
            what, got = f"isTree {i}", d.isTree(i)
            assert got == (b.edges[b.comp[i]] == len(members) - 1), (name, what, got)
        elif op == "diff":
            got = d.diff(i, j)
            assert got == (b.val[j] - b.val[i] if b.comp[i] == b.comp[j] else None), (name, what, got)
        elif op == "firstConnectedTime":
            got = d.firstConnectedTime(i, j)
            assert got == b.first_time(i, j), (name, what, got, b.first_time(i, j))
        elif op == "connectedAt":
            t = rnd.randint(0, len(b.hist) + 1)
            what += f" {t}"
            got = d.connectedAt(i, j, t)
            f = b.first_time(i, j)
            assert got == (f != -1 and f <= t), (name, what, got)
        elif op == "rollback":
            what = op
            d.rollbackLastUnion()
            b.rollback()
            got = "ok"
        elif op == "checkpoint":
            what, got = op, d.checkpoint()
            assert got == len(b.snaps), (name, what, got)
        elif op == "rollbackTo":
            k = rnd.randint(0, len(b.snaps))
            what = f"rollbackTo {k}"
            d.rollbackTo(k)
            while len(b.snaps) > k:
                b.rollback()
            got = "ok"
        elif op == "add":
            v = rnd.randint(-20, 20)
            what, got = f"add {v}", d.add(v)
            assert got == b.add(v), (name, what, got)
        lines.append(what)
        outs.append(fmt(got))
    if roll:  # rolling all the way back leaves every element alone again
        d.rollbackTo(0)
        assert d.numComponents() == b.n() and all(d.find(k) == k for k in range(b.n())), (name, "rollbackTo 0")
    text = f"{n0}\n{' '.join(map(str, vals))}\n" + "\n".join(lines) + "\n"
    return text, outs


# ------------------------------------------------------------------------------------------------ hdlt
def brute_labels(n, pairs):
    label = list(range(n))

    def root(x):
        while label[x] != x:
            x = label[x]
        return x
    for a, b in pairs:
        label[root(a)] = root(b)
    return [root(x) for x in range(n)]


def hdlt_script(seed, stress=False):
    """random adds / removes (stress: hundreds of copies of a few pairs, removed one by one), every answer checked
    against connectivity recomputed from the live edges; returns (C++ driver input, printed lines)"""
    rnd = random.Random(seed)
    ns = load_py("hdlt")
    n = rnd.randint(2, 5) if stress else rnd.randint(1, 9)
    d = ns["DynamicConnectivity"](list(range(n)))
    live = {}  # edge id -> (a, b)
    lines, outs = [], []

    def pick():
        if stress:
            return rnd.choice([(0, 1), (1, 0), (0, n - 1), (1, 1)])
        return rnd.randrange(n), rnd.randrange(n)

    def removedBy(a, b):  # the id removeEdgeBetween is about to take, read off the template
        ids = d._byPair.get(d._pairKey(a, b))
        return ids[-1] if ids else None

    def check(where):
        lab = brute_labels(n, live.values())
        assert d.numComponents() == len(set(lab)), (seed, where, "numComponents")
        for x in range(n):
            for y in range(n):
                assert d.areConnected(x, y) == (lab[x] == lab[y]), (seed, where, "areConnected", x, y)
            assert d.size(x) == lab.count(lab[x]), (seed, where, "size", x)

    if stress:
        plan = ["add"] * rnd.randint(200, 400)
        plan += [rnd.choice(["rm", "rmb"]) for _ in range(len(plan) + 5)]
    else:
        plan = [rnd.choice(["add"] * 4 + ["rm"] * 2 + ["rmb", "conn", "size", "comps", "sizes", "groups"]) for _ in range(150)]
    k = 0
    while k < len(plan):
        op = plan[k]
        k += 1
        if stress and k == len(plan) and live:
            plan.append(rnd.choice(["rm", "rmb"]))  # keep removing until every copy is gone
        before = d.numComponents()
        if op == "add":
            a, b = pick()
            e = d.addEdge(a, b)
            assert e not in live, (seed, "id reused while live")
            live[e] = (a, b)
            lines.append(f"add {a} {b}")
            outs.append(str(e))
        elif op == "rm":
            if not live:
                continue
            e = rnd.choice(sorted(live))
            split = d.removeEdge(e)
            del live[e]
            assert split == (d.numComponents() == before + 1), (seed, k, "removeEdge split")
            lines.append(f"rm {e}")
            outs.append(fmt(split))
        elif op == "rmb":
            a, b = pick() if (rnd.random() < 0.3 or not live) else live[rnd.choice(sorted(live))]
            e = removedBy(a, b)
            got = d.removeEdgeBetween(a, b)
            assert got == (e is not None), (seed, k, "removeEdgeBetween result")
            if e is not None:
                assert sorted(live.pop(e)) == sorted((a, b)), (seed, k, "removeEdgeBetween took an edge of another pair")
            lines.append(f"rmb {a} {b}")
            outs.append(fmt(got))
        elif op == "conn":
            a, b = rnd.randrange(n), rnd.randrange(n)
            lines.append(f"conn {a} {b}")
            outs.append(fmt(d.areUnioned(a, b)))
        elif op == "size":
            a = rnd.randrange(n)
            lines.append(f"size {a}")
            outs.append(str(d.size(a)))
        elif op == "comps":
            lines.append("comps")
            outs.append(str(d.numComponents()))
        elif op == "sizes":
            lab = brute_labels(n, live.values())
            assert d.sizes() == sorted((lab.count(r) for r in set(lab)), reverse=True), (seed, k, "sizes")
            lines.append("sizes")
            outs.append(fmt(d.sizes()))
        elif op == "groups":
            lab = brute_labels(n, live.values())
            want = sorted(sorted(x for x in range(n) if lab[x] == r) for r in set(lab))
            assert sorted(sorted(g) for g in d.groups()) == want, (seed, k, "groups")
            lines.append("groups")
            outs.append(fmt(want))
        check((k, op))
    assert not stress or not live, (seed, "stress left edges behind")
    return f"{n}\n" + "\n".join(lines) + "\n", outs


HDLT_DRIVER = """
int main() {
    int n; cin >> n; vector<long long> a(n); iota(a.begin(), a.end(), 0LL);
    DynamicConnectivity<long long> d(a);
    string op;
    while (cin >> op) {
        if (op == "add") { int x, y; cin >> x >> y; cout << d.unite(x, y) << "\\n"; }
        else if (op == "rm") { int e; cin >> e; cout << (int)d.removeEdge(e) << "\\n"; }
        else if (op == "rmb") { int x, y; cin >> x >> y; cout << (int)d.removeEdgeBetween(x, y) << "\\n"; }
        else if (op == "conn") { int x, y; cin >> x >> y; cout << (int)d.areUnioned(x, y) << "\\n"; }
        else if (op == "size") { int x; cin >> x; cout << d.size(x) << "\\n"; }
        else if (op == "comps") cout << d.numComponents() << "\\n";
        else if (op == "sizes") { auto x = d.sizes(); for (size_t k = 0; k < x.size(); k++) cout << (k ? " " : "") << x[k]; cout << "\\n"; }
        else if (op == "groups") {
            auto g = d.groups();
            vector<vector<long long>> s;
            for (auto& x : g) { sort(x.begin(), x.end()); s.push_back(x); }
            sort(s.begin(), s.end());
            for (size_t i = 0; i < s.size(); i++) { if (i) cout << "|"; for (size_t k = 0; k < s[i].size(); k++) cout << (k ? " " : "") << s[i][k]; }
            cout << "\\n";
        }
        else { cerr << "unknown op " << op << "\\n"; return 1; }
    }
}
"""


def hdlt_scripts():
    out = [(seed, hdlt_script(seed)) for seed in range(SCRIPTS)]
    out += [(100 + seed, hdlt_script(100 + seed, stress=True)) for seed in range(4)]
    return out


# ------------------------------------------------------------------------------------------------ C++ driver
def driver(name):
    mode, feats = parse(name)
    has = feats.__contains__
    cls = CLASS[mode] + ("" if has("merge") else "<long long>")
    W = ", w" if has("potential") else ""
    rw = " >> w" if has("potential") else ""
    decl = " long long w;" if has("potential") else ""
    U, UB = ("uniteWeighted", "uniteAUnderBWeighted") if has("potential") else ("unite", "uniteAUnderB")
    vec = 'for (size_t k = 0; k < x.size(); k++) cout << (k ? " " : "") << x[k]; cout << "\\n";'
    c = [f"    if (op == \"unite\") {{ int i, j;{decl} cin >> i >> j{rw}; auto x = d.{U}(i, j{W}); " +
         ('if (x.first < 0) cout << "none\\n"; else cout << x.first << " " << x.second << "\\n"; }' if mode == "nocompress" else "cout << (int)x << \"\\n\"; }"),
         "    else if (op == \"find\") { int i; cin >> i; cout << d.find(i) << \"\\n\"; }",
         "    else if (op == \"areUnioned\") { int i, j; cin >> i >> j; cout << (int)d.areUnioned(i, j) << \"\\n\"; }",
         "    else if (op == \"size\") { int i; cin >> i; cout << d.size(i) << \"\\n\"; }",
         "    else if (op == \"numComponents\") cout << d.numComponents() << \"\\n\";",
         "    else if (op == \"largestSize\") cout << d.largestSize() << \"\\n\";",
         f"    else if (op == \"roots\") {{ auto x = d.roots(); {vec} }}",
         f"    else if (op == \"sizes\") {{ auto x = d.sizes(); {vec} }}",
         "    else if (op == \"groups\") { auto g = d.groups(); for (size_t a = 0; a < g.size(); a++) { if (a) cout << \"|\"; "
         "for (size_t k = 0; k < g[a].size(); k++) cout << (k ? \" \" : \"\") << g[a][k]; } cout << \"\\n\"; }",
         f"    else if (op == \"elementsInGroup\") {{ int i; cin >> i; auto x = d.elementsInGroup(i); {vec} }}"]
    if mode == "nocompress":
        c.append(f"    else if (op == \"uniteAUnderB\") {{ int i, j;{decl} cin >> i >> j{rw}; cout << (int)d.{UB}(i, j{W}) << \"\\n\"; }}")
    if mode == "rollback":
        c += ["    else if (op == \"rollback\") { d.rollbackLastUnion(); cout << \"ok\\n\"; }",
              "    else if (op == \"checkpoint\") cout << d.checkpoint() << \"\\n\";",
              "    else if (op == \"rollbackTo\") { int k; cin >> k; d.rollbackTo(k); cout << \"ok\\n\"; }"]
    if has("values"):
        c += [f"    else if (op == \"{f}\") {{ int i; cin >> i; cout << d.{f}(i) << \"\\n\"; }}" for f in ("componentSum", "componentMin", "componentMax")]
    if has("merge"):
        c.append("    else if (op == \"componentData\") { int i; cin >> i; auto x = d.componentData(i); cout << x.tot << \" \" << x.mx << \"\\n\"; }")
    if has("edges"):
        c += ["    else if (op == \"edgeCount\") { int i; cin >> i; cout << d.edgeCount(i) << \"\\n\"; }",
              "    else if (op == \"isTree\") { int i; cin >> i; cout << (int)d.isTree(i) << \"\\n\"; }"]
    if has("potential"):
        c.append("    else if (op == \"diff\") { int i, j; cin >> i >> j; auto x = d.diff(i, j); if (!x) cout << \"none\\n\"; else cout << *x << \"\\n\"; }")
    if has("time"):
        c += ["    else if (op == \"firstConnectedTime\") { int i, j; cin >> i >> j; cout << d.firstConnectedTime(i, j) << \"\\n\"; }",
              "    else if (op == \"connectedAt\") { int i, j, t; cin >> i >> j >> t; cout << (int)d.connectedAt(i, j, t) << \"\\n\"; }"]
    if has("grow"):
        c.append("    else if (op == \"add\") { long long v; cin >> v; cout << d.add(v) << \"\\n\"; }")
    c.append("    else { cerr << \"unknown op \" << op << \"\\n\"; return 1; }")
    return ("\nint main() {\n    int n; cin >> n; vector<long long> a(n); for (auto& x : a) cin >> x;\n"
            f"    {cls} d(a);\n    string op;\n    while (cin >> op) {{\n" + "\n".join("    " + x for x in c) + "\n    }\n}\n")


def cpp_source(name):
    text = open(os.path.join(DIR, name, "template.cpp")).read()
    if name == "hdlt":
        return text + HDLT_DRIVER
    mode, _ = parse(name)
    k = text.index(f"struct {CLASS[mode]} {{")
    k = text.rfind("\n", 0, text.rfind("template <typename T>", 0, k) if "template <typename T>" in text[:k] else k)
    head = re.sub(r"^( +)// (?!\()", r"\1", text[:k], flags=re.M)  # (the merge example switched on; notes in brackets stay)
    return head + text[k:] + driver(name)


def check_cpp(name, scripts):
    os.makedirs(CACHE, exist_ok=True)
    src, exe = os.path.join(CACHE, name + ".cpp"), os.path.join(CACHE, name)
    code = cpp_source(name)
    if not (os.path.exists(src) and open(src).read() == code and os.path.exists(exe)):
        open(src, "w").write(code)
        r = subprocess.run(["g++", "-std=c++17", "-O0", "-Wall", "-Wno-unused-parameter", "-fsanitize=address,undefined",
                            "-fno-sanitize-recover=all", "-o", exe, src], capture_output=True, text=True)
        if r.returncode:
            return f"FAIL  {name} [cpp]: compile error\n{r.stderr[:1500]}"
        if "warning" in r.stderr:
            return f"FAIL  {name} [cpp]: warning\n{r.stderr[:1500]}"
    for seed, (text, outs) in scripts:
        r = subprocess.run([exe], input=text, capture_output=True, text=True, timeout=60)
        if r.returncode:
            return f"FAIL  {name} [cpp] seed {seed}: exit {r.returncode}\n{r.stderr[:1200]}"
        got = r.stdout.split("\n")[:-1]
        if got != outs:
            k = next((k for k in range(min(len(got), len(outs))) if got[k] != outs[k]), min(len(got), len(outs)))
            line = text.split("\n")[2 + k] if 2 + k < len(text.split("\n")) else "?"
            return f"FAIL  {name} [cpp] seed {seed}: op {k} '{line}': got {got[k] if k < len(got) else 'nothing'}, python {outs[k] if k < len(outs) else 'nothing'}"
    return f"PASS  {name} [py cpp]"


def main():
    args = sys.argv[1:]
    budget = float(args[args.index("--budget") + 1]) if "--budget" in args else 1e9
    want = [a for k, a in enumerate(args) if not a.startswith("--") and (k == 0 or args[k - 1] != "--budget")]
    names = sorted(d for d in os.listdir(DIR) if (d.split("-")[0] in CLASS or d == "hdlt") and (not want or any(w in d for w in want)))
    start = time.time()
    scripts = {}
    for name in names:
        if name == "hdlt":
            try:
                scripts[name] = hdlt_scripts()
            except AssertionError as e:
                print(f"FAIL  hdlt [py]: {e}")
                sys.exit(1)
            continue
        scripts[name] = []
        for seed in range(SCRIPTS):
            try:
                scripts[name].append((seed, script(name, seed * 7919 + len(name))))
            except AssertionError as e:
                print(f"FAIL  {name} [py] seed {seed}: {e}")
                sys.exit(1)
    print(f"python: all {len(names)} templates agree with the brute force ({time.time() - start:.0f}s)", flush=True)
    if "--py" in args:
        return
    lines = []
    with concurrent.futures.ThreadPoolExecutor(os.cpu_count() or 2) as pool:
        futures = {}
        for name in names:
            if time.time() - start > budget:
                break
            futures[pool.submit(check_cpp, name, scripts[name])] = name
            while sum(not f.done() for f in futures) >= 2 * (os.cpu_count() or 2):
                time.sleep(0.05)
                if time.time() - start > budget:
                    break
        for f in futures:
            lines.append(f.result())
    fails = [x for x in lines if x.startswith("FAIL")]
    print("\n".join(fails[:5]))
    print(f"cpp: {len(lines) - len(fails)} of {len(lines)} pass" + (f" ({len(names) - len(lines)} not run: budget)" if len(lines) < len(names) else ""))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
