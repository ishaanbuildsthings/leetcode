"""Tests every 2D / 3D range query template (templates/ultimate-template-tool/range-queries-2d/*) against a brute force.

A folder's header says what it supports (@operations) and what its constructor is given (@input). Random op scripts
are run on a plain dictionary of set cells (the brute force below knows every op), and template.py and template.cpp
must give exactly the same answers, bad arguments included (they must raise / throw, never answer). Nothing here is
per-template: a new folder is covered as soon as its ops are in OPS.

    python3 test_templates_2d.py                 # everything, Python then C++
    python3 test_templates_2d.py grid-bit seg    # only folders whose name contains one of these
    python3 test_templates_2d.py --py            # Python only (no compiler needed)
    python3 test_templates_2d.py --cpp           # C++ only
    python3 test_templates_2d.py --trials 60     # random scripts per template (default 40)
    python3 test_templates_2d.py --shard 2/4     # every 4th folder from the third (shards 0/4 .. 3/4 side by side)
    python3 test_templates_2d.py --jobs 4        # C++ builds side by side (default: the CPU count)

    python3 test_templates_2d.py --as-shipped    # C++ built exactly as the file is (see below)

C++ needs a GCC with bits/stdc++.h (see ../find_compiler.py); each template.cpp is built with sanitizers when the
compiler has them, with T = long long, and also instantiated with T = int. The templates skip sanitizers inside
themselves (LEETCODE_NO_SANITIZE), which would blind this test, so by default it switches the skip off
(-DLEETCODE_NO_SANITIZE=: the templates only define it when nobody else has). --as-shipped leaves it on: the same
answers must come out of the file exactly as it is served.
"""
import concurrent.futures
import math
import os
import random
import re
import subprocess
import sys
import tempfile
from functools import reduce

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
DIR = os.path.join(os.path.dirname(HERE), "range-queries-2d")
sys.path.insert(0, os.path.dirname(HERE))
from find_compiler import cxx, sanitize_flags  # noqa: E402

AGG_FN = {
    "sum": lambda vs: sum(vs),
    "min": lambda vs: min(vs) if vs else None,
    "max": lambda vs: max(vs) if vs else None,
    "gcd": lambda vs: reduce(math.gcd, vs, 0),
    "xor": lambda vs: reduce(lambda a, b: a ^ b, vs, 0),
    "and": lambda vs: reduce(lambda a, b: a & b, vs, -1),
    "or": lambda vs: reduce(lambda a, b: a | b, vs, 0),
}
AGG_KEYS = list(AGG_FN)
CAP = {k: k[0].upper() + k[1:] for k in AGG_KEYS}
CMP = {"Lte": lambda a, b: a <= b, "Gte": lambda a, b: a >= b}

# op -> (argument shape, result kind). Shapes: p = a cell, v = a value, rect = two corners (low, then high), k = a
# count; results: void, val (a number, or nothing), bool
OPS = {"pointGet": ("p", "val"), "getAll": ("", "grid")}
for _op in ("pointAssign", "pointAdd", "pointChmax", "pointChmin"):
    OPS[_op] = ("pv", "void")
for _op in ("rectAdd", "rectAssign", "rectChmax", "rectChmin"):
    OPS[_op] = ("rectv", "void")
for _k in AGG_KEYS:
    OPS[f"rect{CAP[_k]}"] = ("rect", "val")
    OPS[f"{_k}All"] = ("", "val")
    OPS[f"square{CAP[_k]}"] = ("square", "val")
    OPS[f"window{CAP[_k]}"] = ("window", "val")
    OPS[f"box{CAP[_k]}"] = ("rect", "val")
for _k in ("min", "max"):
    for _a in CMP:
        for _b in CMP:
            OPS[f"{_k}{_a}{_b}"] = ("corner", "val")
        OPS[f"{_k}{_a}{_a}{_a}"] = ("corner", "val")
for _a in CMP:  # (3D only: a sum from one corner)
    OPS[f"sum{_a}{_a}{_a}"] = ("corner", "val")
OPS["rectHash"] = ("rectpair", "bool")  # tested as: do two rectangles hash equal exactly when their cells are equal
OPS["rectsEqual"] = ("rectpair", "bool")
OPS["hashAll"] = ("", "bool")  # tested as: hashAll() == rectHash(the whole grid)


def op_agg(op):
    """(aggregate, family) of a query op: rectMax -> ("max", "rect"); maxLteGte -> ("max", "corner")."""
    for k in AGG_KEYS:
        for fam in ("rect", "square", "window", "box"):
            if op == f"{fam}{CAP[k]}":
                return k, fam
        if op == f"{k}All":
            return k, "all"
        if op.startswith(k) and op[len(k):len(k) + 3] in CMP:
            return k, "corner"
    return None, None


# ------------------------------------------------------------------------------------------------ header
def read_header(path):
    tags, block = {}, None
    costs = {}
    for line in open(path, encoding="utf-8"):
        m = re.match(r"^\s*(?:#|//) @([a-z-]+):\s*(.*?)\s*$", line)
        if m:
            tags[m.group(1)] = m.group(2)
            block = m.group(1)
            continue
        m = re.match(r"^\s*(?:#|//)\s+(\w+):\s*(.+?)\s*$", line)
        if m and block == "complexities":
            costs[m.group(1)] = m.group(2)
        elif not line.strip() and tags:
            break
    tags["operations"] = tags.get("operations", "").split()
    return tags


# ------------------------------------------------------------------------------------------------ brute force
class Brute:
    """The set cells, as a dictionary. dims = 2 or 3. `universe` is every cell an update may touch: all of a grid, the
    points given, or None when any cell of the coordinate range can be set (online)."""

    def __init__(self, kind, ops, bounds, universe, cells, window=None, empties=False):
        self.kind, self.ops, self.bounds, self.universe = kind, ops, bounds, universe
        self.cells = dict(cells)
        self.window = window
        self.dims = len(bounds)
        # @empty-cells: yes = a cell nobody set is empty (queries skip it); otherwise it is 0
        self.empty_read = None if empties else 0
        if self.empty_read == 0 and universe is not None:
            for p in universe:
                self.cells.setdefault(p, 0)

    def point_ok(self, p):
        if self.kind == "batch":
            return True  # (any coordinates)
        if self.kind == "points":
            return p in self.universe
        return all(lo <= x <= hi for x, (lo, hi) in zip(p, self.bounds))

    def rect_ok(self, lo, hi):
        if any(a > b for a, b in zip(lo, hi)):
            return False
        if self.kind in ("points", "batch"):
            return True
        return all(blo <= a and b <= bhi for a, b, (blo, bhi) in zip(lo, hi, self.bounds))

    def inside(self, lo, hi):
        vals = [v for p, v in self.cells.items() if all(a <= x <= b for x, a, b in zip(p, lo, hi))]
        if self.empty_read == 0 and self.universe is None:  # any cell of the range exists and is 0 until set
            area = 1
            for a, b in zip(lo, hi):
                area *= b - a + 1
            if area > len(vals):
                vals.append(0)
        return vals

    def targets(self, lo, hi):
        if self.universe is not None:
            return [p for p in self.universe if all(a <= x <= b for x, a, b in zip(p, lo, hi))]
        raise AssertionError("a rectangle update needs a finite set of cells")

    def run(self, op, args):
        """The answer (None = nothing), or the string "E" for arguments the template must refuse."""
        shape = OPS[op][0]
        d = self.dims
        cells = self.cells
        if shape in ("p", "pv"):
            p = tuple(args[:d])
            if not self.point_ok(p):
                return "E"
            if op == "pointGet":
                return cells.get(p, self.empty_read)
            v = args[d]
            if op == "pointAssign":
                cells[p] = v
            elif op == "pointAdd":
                cells[p] = cells.get(p, 0) + v
            elif op in ("pointChmax", "pointChmin"):
                cur = cells.get(p, self.empty_read)  # (a cell nobody set: empty, or 0 where cells can't be empty)
                cells[p] = v if cur is None else (max if op == "pointChmax" else min)(cur, v)
            return "-"
        if shape == "rectv":
            lo, hi, v = tuple(args[:d]), tuple(args[d:2 * d]), args[2 * d]
            if not self.rect_ok(lo, hi):
                return "E"
            for p in self.targets(lo, hi):
                if op == "rectAdd":
                    cells[p] = cells.get(p, 0) + v
                elif op == "rectAssign":
                    cells[p] = v
                elif op == "rectChmax":
                    cells[p] = max(cells.get(p, v), v)
                elif op == "rectChmin":
                    cells[p] = min(cells.get(p, v), v)
            return "-"
        if op == "getAll":
            (r0, r1), (c0, c1) = self.bounds
            return [[cells.get((r, c), self.empty_read) for c in range(c0, c1 + 1)] for r in range(r0, r1 + 1)]
        if shape == "rectpair":
            if op == "hashAll":
                return True
            lo, hi, lo2 = tuple(args[:2]), tuple(args[2:4]), tuple(args[4:6])
            hi2 = (lo2[0] + hi[0] - lo[0], lo2[1] + hi[1] - lo[1])
            if not self.rect_ok(lo, hi) or not self.rect_ok(lo2, hi2):
                return "E"
            return all(cells.get((lo[0] + i, lo[1] + j)) == cells.get((lo2[0] + i, lo2[1] + j))
                       for i in range(hi[0] - lo[0] + 1) for j in range(hi[1] - lo[1] + 1))
        if op == "hashAll":
            return True
        k, fam = op_agg(op)
        if fam == "all":
            return AGG_FN[k](self.inside([b[0] for b in self.bounds], [b[1] for b in self.bounds]))
        if fam in ("rect", "box"):
            lo, hi = tuple(args[:d]), tuple(args[d:2 * d])
            return AGG_FN[k](self.inside(lo, hi)) if self.rect_ok(lo, hi) else "E"
        if fam == "square":
            r, c, side = args
            lo, hi = (r, c), (r + side - 1, c + side - 1)
            return AGG_FN[k](self.inside(lo, hi)) if side >= 1 and self.rect_ok(lo, hi) else "E"
        if fam == "window":
            r, c = args
            lo, hi = (r, c), (r + self.window[0] - 1, c + self.window[1] - 1)
            return AGG_FN[k](self.inside(lo, hi)) if self.rect_ok(lo, hi) else "E"
        if fam == "corner":
            p = tuple(args)
            if self.kind != "points" and not self.point_ok(p):
                return "E"
            sides = [CMP[op[len(k) + 3 * i:len(k) + 3 * i + 3]] for i in range(d)]
            return AGG_FN[k]([v for q, v in cells.items() if all(f(x, y) for f, x, y in zip(sides, q, p))])
        raise AssertionError(f"the brute force doesn't know {op}")


def token(res):
    if res is None:
        return "N"
    if res is True:
        return "T"
    if res is False:
        return "F"
    if isinstance(res, list):
        return " ".join("N" if v is None else str(v) for row in res for v in row)
    return str(res)


# ------------------------------------------------------------------------------------------------ trials
def value(rng, ops, tags=None):
    if tags and tags.get("values") == "non-negative":
        return rng.randrange(0, 64) if rng.random() < 0.9 else rng.randrange(0, 10**9)
    if any(op_agg(op)[0] in ("xor", "and", "or") for op in ops) and rng.random() < 0.7:
        return rng.randrange(0, 64)
    return rng.randrange(-30, 31) if rng.random() < 0.9 else rng.randrange(-10**9, 10**9)


def make_trial(rng, tags):
    """One trial: {kind, init, extra, ops: [(op, args)]}, with what the brute force answers for each op."""
    ops, kind = tags["operations"], tags["input"]
    empties = tags.get("empty-cells") == "yes"
    trial = {"kind": kind, "extra": [], "empties": empties}
    if kind in ("grid", "grid-3d"):
        dims = 3 if kind == "grid-3d" else 2
        sizes = [rng.randrange(1, 4 if dims == 3 else 7) for _ in range(dims)]
        if rng.random() < 0.15:
            sizes[rng.randrange(dims)] = rng.randrange(8, 14)
        bounds = [(0, s - 1) for s in sizes]
        every = [()]
        for s in sizes:
            every = [p + (x,) for p in every for x in range(s)]
        if kind == "grid-3d" or (tags.get("sized") and rng.random() < 0.3):
            start, cells = "empty", {}  # (every cell empty, or 0 in a template without empty cells)
        elif empties and rng.random() < 0.4:
            start = "holes"  # (Python only: C++ has no None to put in a grid)
            cells = {p: value(rng, ops, tags) for p in every if rng.random() < 0.6}
        else:
            start, cells = "full", {p: value(rng, ops, tags) for p in every}
        trial.update(sizes=sizes, start=start, cells=cells)
        window = None
        if any(OPS[op][0] == "window" for op in ops):
            window = (rng.randrange(1, sizes[0] + 1), rng.randrange(1, sizes[1] + 1))
            trial["extra"] = list(window)
        brute = Brute(kind, ops, bounds, every, cells, window, empties)
    elif kind == "points":
        span = rng.choice([3, 6, 10**9])
        pts = [(rng.randrange(-span, span + 1), rng.randrange(-span, span + 1)) for _ in range(rng.randrange(1, 14))]
        pts += [rng.choice(pts) for _ in range(rng.randrange(0, 3))]  # (duplicates are allowed)
        if rng.random() < 0.3:  # many points sharing an x or a y
            x = rng.randrange(-span, span + 1)
            pts += [(x, rng.randrange(-span, span + 1)) for _ in range(4)] + [(rng.randrange(-span, span + 1), x) for _ in range(4)]
        rng.shuffle(pts)
        trial.update(points=pts, span=span)
        brute = Brute(kind, ops, [(-span, span)] * 2, set(pts), {}, None, empties)
    elif kind in ("online", "batch"):
        span = rng.choice([4, 8, 10**9, 10**18])
        lo = [rng.choice([-span, 0]) for _ in range(2)]
        hi = [span, span]
        trial.update(lo=lo, hi=hi, span=span)
        pool = [(rng.randrange(lo[0], hi[0] + 1), rng.randrange(lo[1], hi[1] + 1)) for _ in range(rng.randrange(1, 12))]
        trial["pool"] = pool
        brute = Brute(kind, ops, [(lo[0], hi[0]), (lo[1], hi[1])], None, {}, None, empties)
    else:
        raise AssertionError(kind)

    d = brute.dims

    def coord(axis):
        blo, bhi = brute.bounds[axis]
        if kind == "points":
            if rng.random() < 0.6:
                return rng.choice(trial["points"])[axis] + rng.choice([0, 0, 0, -1, 1])
            return rng.randrange(blo - 2, bhi + 3)
        if kind in ("online", "batch"):
            if rng.random() < 0.7:
                return min(bhi, max(blo, rng.choice(trial["pool"])[axis] + rng.choice([0, 0, -1, 1])))
            return rng.randrange(blo, bhi + 1)
        return rng.randrange(blo, bhi + 1)

    def point():
        if kind == "points":
            return list(rng.choice(trial["points"]))
        if kind in ("online", "batch") and rng.random() < 0.8:
            return list(rng.choice(trial["pool"]))
        return [coord(a) for a in range(d)]

    def bad(args, shape):
        """The same arguments made invalid: off the grid, or a low corner past its high corner."""
        args = list(args)
        axis = rng.randrange(d)
        blo, bhi = brute.bounds[axis]
        if shape in ("rect", "rectv") and rng.random() < 0.5:
            args[axis], args[axis + d] = max(args[axis], args[axis + d]) + 1, min(args[axis], args[axis + d])
        elif kind == "points":
            if shape == "corner":
                return args  # (any corner is fine)
            if shape in ("p", "pv"):
                args[axis] = bhi + 5  # (not one of the points given)
            else:
                args[axis], args[axis + d] = args[axis + d] + 1, args[axis]
        else:
            args[axis] = rng.choice([blo - 1, bhi + 1])
        return args

    script, expected = [], []
    updates = [op for op in ops if OPS[op][1] == "void"]
    queries = [op for op in ops if OPS[op][1] != "void"]
    for _ in range(rng.randrange(8, 40)):
        op = rng.choice(updates) if updates and (not queries or rng.random() < 0.45) else rng.choice(queries)
        shape = OPS[op][0]
        if shape in ("p", "pv"):
            args = point()
        elif shape in ("rect", "rectv"):
            a, b = [coord(x) for x in range(d)], [coord(x) for x in range(d)]
            args = [min(x, y) for x, y in zip(a, b)] + [max(x, y) for x, y in zip(a, b)]
        elif shape == "corner":
            args = [coord(a) for a in range(d)]
        elif shape == "square":
            r, c = coord(0), coord(1)
            args = [r, c, rng.randrange(1, min(brute.bounds[0][1] - r, brute.bounds[1][1] - c) + 2)]
        elif shape == "window":
            args = [rng.randrange(0, brute.bounds[0][1] - brute.window[0] + 2), rng.randrange(0, brute.bounds[1][1] - brute.window[1] + 2)]
        elif shape == "rectpair":
            if op == "hashAll":
                args = []
            else:
                h, w = rng.randrange(1, brute.bounds[0][1] + 2), rng.randrange(1, brute.bounds[1][1] + 2)
                r, c = rng.randrange(0, brute.bounds[0][1] - h + 2), rng.randrange(0, brute.bounds[1][1] - w + 2)
                r2, c2 = rng.randrange(0, brute.bounds[0][1] - h + 2), rng.randrange(0, brute.bounds[1][1] - w + 2)
                if rng.random() < 0.3:
                    r2, c2 = r, c
                args = [r, c, r + h - 1, c + w - 1, r2, c2]
        else:
            args = []
        if shape in ("pv", "rectv"):
            args.append(value(rng, ops, tags))
        if args and shape not in ("rectpair", "square", "window") and rng.random() < 0.06:
            args = bad(args, shape)
        script.append((op, args))
        expected.append(token(brute.run(op, args)))
    trial["ops"], trial["expected"] = script, expected
    return trial


# ------------------------------------------------------------------------------------------------ Python
def load_class(path, ops):
    ns = {}
    exec(compile(open(path, encoding="utf-8").read(), path, "exec"), ns)
    classes = [v for v in ns.values() if isinstance(v, type) and any(hasattr(v, op) for op in ops)]
    return max(classes, key=lambda c: sum(hasattr(c, op) for op in ops))


def py_construct(cls, trial):
    kind = trial["kind"]
    if kind == "grid":
        R, C = trial["sizes"]
        blank = None if trial["empties"] else 0
        grid = [[trial["cells"].get((r, c), blank) for c in range(C)] for r in range(R)]
        return cls(grid, *trial["extra"])
    if kind == "grid-3d":
        return cls(*trial["sizes"])
    if kind == "points":
        return cls(list(trial["points"]))
    if kind == "online":
        return cls(trial["lo"][0], trial["hi"][0], trial["lo"][1], trial["hi"][1])
    if kind == "batch":
        return cls()
    raise AssertionError(kind)


def run_py(cls, trial):
    ds = py_construct(cls, trial)
    out = []
    for op, args in trial["ops"]:
        try:
            if op == "rectHash":
                r1, c1, r2, c2, r3, c3 = args
                res = ds.rectHash(r1, c1, r2, c2) == ds.rectHash(r3, c3, r3 + r2 - r1, c3 + c2 - c1)
            elif op == "hashAll":
                res = ds.hashAll() == ds.rectHash(0, 0, trial["sizes"][0] - 1, trial["sizes"][1] - 1)
            else:
                res = getattr(ds, op)(*args)
            out.append("-" if OPS[op][1] == "void" else token(res))
        except IndexError:
            out.append("E")
    if trial["kind"] == "batch":  # a query returned its number: the answers come from solve(), all at once
        answers = ds.solve()
        out = [token(answers[int(t)]) if OPS[op][1] != "void" and t != "E" else t for t, (op, _) in zip(out, trial["ops"])]
    return out


def describe(trial, i):
    head = {k: v for k, v in trial.items() if k not in ("ops", "expected")}
    lines = [f"    setup: {head}"]
    for j, (op, args) in enumerate(trial["ops"][: i + 1]):
        lines.append(f"    {op}({', '.join(map(str, args))}) -> {trial['expected'][j]}")
    return "\n".join(lines)


def first_mismatch(got, trial):
    for i, (g, e) in enumerate(zip(got, trial["expected"])):
        if g != e:
            return f"op {i}: got {g}, expected {e}\n{describe(trial, i)}"
    if len(got) != len(trial["expected"]):
        return f"{len(got)} answers for {len(trial['expected'])} ops"
    return None


# ------------------------------------------------------------------------------------------------ C++
def none_check(op, ops, source):
    """C++: the expression saying a result `res` of this op means "nothing" (false in a template with no such value)."""
    k, _ = op_agg(op)
    if op == "pointGet":
        has = {op_agg(o)[0] for o in ops}
        k = "max" if "max" in has else "min" if "min" in has else None
    name = {"max": "NO_MAX", "min": "NO_MIN"}.get(k)
    return f"res == DS::{name}" if name and name in source else "false"


def cpp_driver(folder, tags, struct):
    ops, kind = tags["operations"], tags["input"]
    source = open(os.path.join(DIR, folder, "template.cpp"), encoding="utf-8").read()
    d = 3 if kind == "grid-3d" else 2
    L = [f'#include "{os.path.join(DIR, folder, "template.cpp")}"', f"template struct {struct}<int>;",
         f"using DS = {struct}<long long>;", "typedef long long ll;", "int main() {", "    int trials;", "    scanf(\"%d\", &trials);",
         "    while (trials--) {", "        unique_ptr<DS> ds;"]
    if kind == "grid":
        L += ["        int R, C, full, nextra; scanf(\"%d %d %d %d\", &R, &C, &full, &nextra);", "        vector<ll> extra(nextra);",
              "        for (auto& x : extra) scanf(\"%lld\", &x);",
              "        if (full) {", "            vector<vector<ll>> g(R, vector<ll>(C));",
              "            for (auto& row : g) for (auto& x : row) scanf(\"%lld\", &x);",
              "            if (nextra == 2) ds.reset(new DS(g, (int)extra[0], (int)extra[1]));" if any(OPS[o][0] == "window" for o in ops)
              else "            ds.reset(new DS(g));",
              "        } else {",
              "            ds.reset(new DS(R, C));" if tags.get("sized") else "            return 3;",
              "        }"]
    elif kind == "grid-3d":
        L += ["        int X, Y, Z; scanf(\"%d %d %d\", &X, &Y, &Z);", "        ds.reset(new DS(X, Y, Z));"]
    elif kind == "points":
        L += ["        int n; scanf(\"%d\", &n);", "        vector<pair<ll, ll>> pts(n);",
              "        for (auto& p : pts) scanf(\"%lld %lld\", &p.first, &p.second);", "        ds.reset(new DS(pts));"]
    elif kind == "online":
        L += ["        ll a, b, c, e; scanf(\"%lld %lld %lld %lld\", &a, &b, &c, &e);", "        ds.reset(new DS(a, b, c, e));"]
    batch = kind == "batch"
    if batch:
        L += ["        ds.reset(new DS());", "        vector<string> lines;", "        vector<pair<int, int>> asked;  // (line, query number)"]
    L += ["        int q; scanf(\"%d\", &q);", "        while (q--) {", "            char name[64]; scanf(\"%63s\", name);", "            string op = name;",
          "            ll a[8] = {0};", "            try {"]
    first = True
    for op in ops:
        shape, result = OPS[op]
        n = {"p": d, "pv": d + 1, "rect": 2 * d, "rectv": 2 * d + 1, "corner": d, "square": 3, "window": 2, "rectpair": 6, "": 0}[shape]
        if op == "hashAll":
            n = 0
        read = "".join(f' scanf("%lld", &a[{i}]);' for i in range(n))
        call_args = ", ".join(f"a[{i}]" for i in range(n))
        L.append(f'                {"" if first else "else "}if (op == "{op}") {{{read}')
        first = False
        if op == "rectHash":
            L.append("                    bool same = ds->rectHash(a[0], a[1], a[2], a[3]) == ds->rectHash(a[4], a[5], a[4] + a[2] - a[0], a[5] + a[3] - a[1]);")
            L.append('                    puts(same ? "T" : "F");')
        elif op == "hashAll":
            L.append('                    puts(ds->hashAll() == ds->rectHash(0, 0, R - 1, C - 1) ? "T" : "F");')
        elif batch and result == "void":
            L.append(f'                    ds->{op}({call_args}); lines.push_back("-");')
        elif batch:
            L.append(f'                    int id = ds->{op}({call_args}); asked.push_back({{(int)lines.size(), id}}); lines.push_back("");')
        elif result == "void":
            L.append(f'                    ds->{op}({call_args}); puts("-");')
        elif result == "bool":
            L.append(f'                    puts(ds->{op}({call_args}) ? "T" : "F");')
        elif result == "grid":
            L.append(f"                    auto g = ds->{op}();")
            L.append('                    string s; for (auto& row : g) for (auto x : row) s += to_string((ll)x) + " ";')
            L.append('                    if (!s.empty()) s.pop_back(); puts(s.c_str());')
        else:
            L.append(f"                    auto res = ds->{op}({call_args});")
            L.append(f'                    if ({none_check(op, ops, source)}) puts("N"); else printf("%lld\\n", (ll)res);')
        L.append("                }")
    L += ['                else { fprintf(stderr, "unknown op %s\\n", name); return 2; }',
          '            } catch (const out_of_range&) { lines.push_back("E"); }' if batch else '            } catch (const out_of_range&) { puts("E"); }', "        }"]
    if batch:
        L += ["        auto answers = ds->solve();", "        for (auto& [line, id] : asked) lines[line] = to_string((ll)answers[id]);", "        for (auto& s : lines) puts(s.c_str());"]
    L += ["    }", "    return 0;", "}"]
    return "\n".join(L) + "\n"


def cpp_input(trials):
    out = [str(len(trials))]
    for t in trials:
        kind = t["kind"]
        if kind == "grid":
            R, C = t["sizes"]
            full = t["start"] == "full"
            out.append(f"{R} {C} {int(full)} {len(t['extra'])} " + " ".join(map(str, t["extra"])))
            if full:
                out.append(" ".join(str(t["cells"][(r, c)]) for r in range(R) for c in range(C)))
        elif kind == "grid-3d":
            out.append(" ".join(map(str, t["sizes"])))
        elif kind == "points":
            out.append(str(len(t["points"])) + " " + " ".join(f"{x} {y}" for x, y in t["points"]))
        elif kind == "online":
            out.append(f"{t['lo'][0]} {t['hi'][0]} {t['lo'][1]} {t['hi'][1]}")
        out.append(str(len(t["ops"])))
        out += [op + "".join(f" {a}" for a in args) for op, args in t["ops"]]
    return "\n".join(out) + "\n"


def struct_name(path, ops):
    """The C++ struct implementing the most ops (the last such one)."""
    text = open(path, encoding="utf-8").read()
    best, best_n = None, -1
    for m in re.finditer(r"^(template <typename T>\n)?struct (\w+) \{", text, re.M):
        end = text.find("\n};", m.end())
        body = text[m.end():end]
        n = sum(bool(re.search(rf"\b{op}\(", body)) for op in ops)
        if n >= best_n:
            best, best_n = m.group(2), n
    return best


def run_cpp(folder, tags, trials, tmp):
    """None when everything matches, else what went wrong."""
    path = os.path.join(DIR, folder, "template.cpp")
    trials = [t for t in trials if t.get("start") != "holes"]
    src, exe = os.path.join(tmp, folder + ".cpp"), os.path.join(tmp, folder + ".bin")
    open(src, "w").write(cpp_driver(folder, tags, struct_name(path, tags["operations"])))
    skip_off = [] if AS_SHIPPED else ["-DLEETCODE_NO_SANITIZE="]
    comp = subprocess.run([cxx(), "-std=c++17", "-O1", "-Wall", "-Wextra", "-Wno-unused-result", *sanitize_flags(), *skip_off, "-o", exe, src],
                          capture_output=True, text=True)
    if comp.returncode != 0:
        return "does not compile:\n" + comp.stderr[:3000]
    warn = "\n".join(line for line in comp.stderr.split("\n") if "warning" in line and "template.cpp" in line)
    run = subprocess.run([exe], input=cpp_input(trials), capture_output=True, text=True, timeout=600)
    if run.returncode != 0:
        return f"crashed (exit {run.returncode}):\n" + run.stderr[-3000:]
    got = run.stdout.split("\n")
    at = 0
    for t in trials:
        n = len(t["ops"])
        bad = first_mismatch([g.strip() for g in got[at:at + n]], t)
        if bad:
            return bad
        at += n
    os.remove(exe)
    return ("warnings:\n" + warn[:2000]) if warn else None


# ------------------------------------------------------------------------------------------------ main
def test_folder(folder, trials_n, do_py, do_cpp, tmp):
    fails = []
    py, cpp = os.path.join(DIR, folder, "template.py"), os.path.join(DIR, folder, "template.cpp")
    path = py if os.path.exists(py) else cpp
    tags = read_header(path)
    # a C++ template may also have a (rows, cols) constructor: every cell empty, or 0 where cells can't be empty
    tags["sized"] = os.path.exists(cpp) and bool(re.search(r"^    \w+\(int rows, int cols\)", open(cpp).read(), re.M))
    unknown = [op for op in tags["operations"] if op not in OPS]
    if unknown:
        return [f"FAIL  {folder}: the brute force doesn't know {unknown}"]
    if os.path.exists(py) and os.path.exists(cpp) and read_header(cpp) != read_header(py):
        fails.append(f"FAIL  {folder}: template.py and template.cpp headers disagree")
    rng = random.Random(folder)
    trials = [make_trial(rng, tags) for _ in range(trials_n)]
    if do_py and os.path.exists(py):
        try:
            cls = load_class(py, tags["operations"])
            missing = [op for op in tags["operations"] if not hasattr(cls, op)]
            if missing:
                fails.append(f"FAIL  {folder} [py]: {cls.__name__} has no {missing}")
            else:
                for t in trials:
                    bad = first_mismatch(run_py(cls, t), t)
                    if bad:
                        fails.append(f"FAIL  {folder} [py]: {bad}")
                        break
        except Exception as e:  # noqa: BLE001 (a template that raises anything else is a failure too)
            import traceback
            fails.append(f"FAIL  {folder} [py]: {type(e).__name__}: {e}\n{traceback.format_exc()[-1500:]}")
    if do_cpp and os.path.exists(cpp):
        try:
            bad = run_cpp(folder, tags, trials, tmp)
        except subprocess.TimeoutExpired:
            bad = "timed out"
        if bad:
            fails.append(f"FAIL  {folder} [cpp]: {bad}")
    return fails


AS_SHIPPED = False


def main():
    global AS_SHIPPED
    argv = sys.argv[1:]
    AS_SHIPPED = "--as-shipped" in argv
    do_py, do_cpp = "--cpp" not in argv and not AS_SHIPPED, "--py" not in argv
    trials_n, shard, jobs = 40, None, os.cpu_count() or 2
    names = []
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--trials":
            trials_n = int(argv[i + 1]); i += 1
        elif a == "--shard":
            shard = tuple(map(int, argv[i + 1].split("/"))); i += 1
        elif a == "--jobs":
            jobs = int(argv[i + 1]); i += 1
        elif not a.startswith("--"):
            names.append(a)
        i += 1
    folders = sorted(f for f in os.listdir(DIR) if os.path.isdir(os.path.join(DIR, f)))
    if names:
        folders = [f for f in folders if any(n in f for n in names)]
    if shard:
        folders = folders[shard[0]::shard[1]]
    fails = []
    with tempfile.TemporaryDirectory() as tmp, concurrent.futures.ThreadPoolExecutor(jobs) as pool:
        for done, res in enumerate(pool.map(lambda f: test_folder(f, trials_n, do_py, do_cpp, tmp), folders), 1):
            fails += res
            for line in res:
                print(line, flush=True)
            if done % 50 == 0:
                print(f"... {done}/{len(folders)} folders", flush=True)
    langs = " and ".join(n for n, on in (("Python", do_py), ("C++", do_cpp)) if on)
    print(f"{len(folders)} folders, {langs}: {'all passed' if not fails else f'{len(fails)} FAILED'}")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
