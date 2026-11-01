"""Tag-only clamp trees for two of {add, chmin, chmax} (no range aggregates, point reads), so neither pays for the
third tag the full ClampTree (add + assign + chmin + chmax: tags A, B, C) keeps:

    python3 gen_clamp_tags.py

    add + chmin:              x -> min(A, x + C)         tags A, C
    add + chmax:              x -> max(B, x + C)         tags B, C
    chmin + chmax (+ assign): x -> min(A, max(B, x))     tags A, B   (assign v is the clamp with A = B = v)

The single-update cases are elsewhere (range add: a BIT; chmin / chmax / assign alone: tag-only seg trees). The tree is
the same 2N one as ClampTree: tags on internal nodes, leaves in val; clamps compose but not commutatively, so an
update first pushes the tags on the paths to l and r; pointGet applies the ancestors' tags bottom-up.
"""
import os

from note_lang import folder_name, write_template

DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "range-queries")
POINT = ["pointAdd", "pointAssign", "pointChmax", "pointChmin", "pointGet"]
VARIANTS = {"AC": ("AddChminTree", ["rangeAdd", "rangeChmin"], "x -> min(A, x + C)"),
            "BC": ("AddChmaxTree", ["rangeAdd", "rangeChmax"], "x -> max(B, x + C)"),
            "AB": ("ChminChmaxTree", ["rangeAssign", "rangeChmax", "rangeChmin"], "x -> min(A, max(B, x))")}
DOC = {"rangeAdd": "a[i] += v", "rangeChmin": "a[i] = min(a[i], v)", "rangeChmax": "a[i] = max(a[i], v)", "rangeAssign": "a[i] = v"}


def header(cm, comps, ops):
    tags = " ".join(f"{t}[1*N]" for t in comps)
    lines = [f"@operations: {' '.join(ops)}", "@data-structure-type: lazy-seg-tree", "@complexities:"]
    lines += [f"  {op}: {'N' if op == 'getAll' else 'log(N)'}" for op in ops] + ["  build: N", "@memory:", "  layout: 2n-iterative",
              "  node: val[1*N]", f"  tags: {tags}", "  other: none",
              f"  note: each internal node holds one pending clamp {VARIANTS[comps][2]}; val holds the leaf values"]
    return "\n".join(f"{cm} {x}" for x in lines) + "\n"


def args(comps, op):
    """(A, B, C) of the clamp an update is, Python / C++ sentinels as words"""
    a = {"rangeAdd": ("INF", "NEG", "v"), "rangeChmin": ("v", "NEG", "0"), "rangeChmax": ("INF", "v", "0"), "rangeAssign": ("v", "v", "0")}[op]
    return [x for t, x in zip("ABC", a) if t in comps]


def python(comps):
    name, upd, form = VARIANTS[comps]
    ops = sorted(POINT + ["getAll"] + upd)
    A, B, C = ("A" in comps), ("B" in comps), ("C" in comps)
    params = ", ".join(t.lower() for t in comps)
    ident = {"A": "INF", "B": "NEG", "C": "0"}
    leaf = []
    if C: leaf.append("            v = val[x - n] + c")
    else: leaf.append("            v = val[x - n]")
    if B: leaf += ["            if v < b:", "                v = b"]
    if A: leaf += ["            if v > a:", "                v = a"]
    comp = []
    if A and C:
        comp += ["            p = A[x] + c", "            A[x] = a if a < p else p", "            C[x] += c"]
    elif B and C:
        comp += ["            q = B[x] + c", "            B[x] = b if b > q else q", "            C[x] += c"]
    else:  # A and B
        comp += ["            na = A[x] if A[x] > b else b", "            if a < na:", "                na = a",
                 "            nb = B[x] if B[x] > b else b", "            A[x] = na", "            B[x] = nb if nb < na else na"]
    cond = " or ".join(f"{t}[x] != {ident[t]}" for t in comps)
    tv = ", ".join(f"{t}[x]" for t in comps)
    reset = "\n".join(f"                {t}[x] = {ident[t]}" for t in comps)
    getv = []
    if C: getv.append("            v += C[p]")
    if B: getv += ["            b = B[p]", "            if v < b:", "                v = b"]
    if A: getv += ["            a = A[p]", "            if v > a:", "                v = a"]
    upd_text = "".join(f'''
    # O(logN) -- {DOC[op]} for i in [l, r]
    def {op}(self, l, r, v):
        self._update(l, r, {", ".join(args(comps, op))})
''' for op in upd)
    tags = ", ".join(f"self.{t}" for t in comps)
    lhs = ", ".join(comps)
    return header("#", comps, ops) + f'''
# Range {" / ".join(o[5:].lower() for o in upd)} + point ops, no range aggregates. All indices 0-based, ranges inclusive.
# Every update is a clamp {form}; clamps compose into a clamp, but not commutatively, so before tagging
# the covering nodes we push the tags on the paths to l and r (the standard 2N trick for point reads).
{'INF = float("inf")' + chr(10) if A else ""}{'NEG = float("-inf")' + chr(10) if B else ""}

class {name}:
    __slots__ = ("n", {", ".join(f'"{t}"' for t in comps)}, "val")

    # O(N)
    def __init__(self, arr):
        n = self.n = len(arr)
{"".join(f"        self.{t} = [{ident[t]}] * n{chr(10)}" for t in comps)}        self.val = list(arr)

    # apply clamp ({params}) on top of whatever node x already holds
    def _apply(self, x, {params}):
        n = self.n
        if x >= n:
            val = self.val
{chr(10).join(leaf)}
            val[x - n] = v
        else:
            {lhs}{"," if len(comps) == 1 else ""} = {tags}
{chr(10).join(comp)}

    # O(logN) -- push every pending clamp on leaf p's root-to-leaf path down to its children
    def _push(self, p):
        {lhs} = {tags}
        apply = self._apply
        for h in range(p.bit_length() - 1, 0, -1):
            x = p >> h
            if {cond}:
                {params} = {tv}
                y = x << 1
                apply(y, {params})
                apply(y | 1, {params})
{reset}

    def _update(self, l, r, {params}):
        n = self.n
        l += n
        r += n
        self._push(l)
        self._push(r)
        r += 1
        apply = self._apply
        while l < r:
            if l & 1:
                apply(l, {params})
                l += 1
            if r & 1:
                r -= 1
                apply(r, {params})
            l >>= 1
            r >>= 1
{upd_text}
    # O(logN) -- a[i]: start from the leaf and apply ancestors' clamps bottom-up (deeper tags are older)
    def pointGet(self, i):
        {lhs} = {tags}
        v = self.val[i]
        p = (i + self.n) >> 1
        while p:
{chr(10).join(getv)}
            p >>= 1
        return v

    # O(N) -- the whole array: push every tag down (a parent's index is below its children's, so in index order
    # each node's tag is complete when it is pushed), then read the leaves
    def getAll(self):
        {lhs} = {tags}
        apply = self._apply
        for x in range(1, self.n):
            if {cond}:
                {params} = {tv}
                apply(2 * x, {params})
                apply(2 * x + 1, {params})
{reset}
        return list(self.val)

    # O(logN) -- a[i] = v
    def pointAssign(self, i, v):
        self._push(i + self.n)
        self.val[i] = v

    # O(logN) -- a[i] += delta
    def pointAdd(self, i, delta):
        self._push(i + self.n)
        self.val[i] += delta

    # O(logN) -- a[i] = max(a[i], v)
    def pointChmax(self, i, v):
        self._push(i + self.n)
        if v > self.val[i]:
            self.val[i] = v

    # O(logN) -- a[i] = min(a[i], v)
    def pointChmin(self, i, v):
        self._push(i + self.n)
        if v < self.val[i]:
            self.val[i] = v
'''


def cpp(comps):
    name, upd, form = VARIANTS[comps]
    ops = sorted(POINT + ["getAll"] + upd)
    A, B, C = ("A" in comps), ("B" in comps), ("C" in comps)
    ident = {"A": "INF", "B": "NINF", "C": "T(0)"}
    params = ", ".join(t.lower() for t in comps)
    sig = ", ".join(f"T {t.lower()}" for t in comps)
    leafv = "val[x - n]" + (" + c" if C else "")
    if A and B:
        leaf = f"min(a, max(b, {leafv}))"
    elif A:
        leaf = f"min(a, {leafv})"
    else:
        leaf = f"max(b, {leafv})"
    if A and C:
        comp = ["        A[x] = min(a, A[x] == INF ? INF : A[x] + c);", "        C[x] += c;"]
    elif B and C:
        comp = ["        B[x] = max(b, B[x] == NINF ? NINF : B[x] + c);", "        C[x] += c;"]
    else:
        comp = ["        T na = min(a, max(b, A[x]));", "        B[x] = min(max(b, B[x]), na);", "        A[x] = na;"]
    cond = " || ".join(f"{t}[x] != {ident[t]}" for t in comps)
    tv = ", ".join(f"{t}[x]" for t in comps)
    reset = ", ".join(f"{t}[x] = {ident[t]}" for t in comps)
    getv = (f"min(A[p], max(B[p], v))" if A and B else f"min(A[p], v + C[p])" if A else f"max(B[p], v + C[p])")
    cargs = {"rangeAdd": ("INF", "NINF", "v"), "rangeChmin": ("v", "NINF", "T(0)"), "rangeChmax": ("INF", "v", "T(0)"), "rangeAssign": ("v", "v", "T(0)")}
    upd_text = "".join(f'''
    // O(logN) -- {DOC[op]} for i in [l, r]
    void {op}(int l, int r, T v) {{ update(l, r, {", ".join(x for t, x in zip("ABC", cargs[op]) if t in comps)}); }}
''' for op in upd)
    inits = ", ".join(f"{t}(a.size(), {ident[t]})" for t in comps)
    return header("//", comps, ops) + f'''
// Range {" / ".join(o[5:].lower() for o in upd)} + point ops, no range aggregates. All indices 0-based, ranges inclusive.
// Every update is a clamp {form}; clamps compose into a clamp, but not commutatively, so before tagging
// the covering nodes we push the tags on the paths to l and r (the standard 2N trick for point reads).
// T: int, long long, ...; values must stay strictly inside (min(T), max(T)), which are the sentinels.
template <typename T>
struct {name} {{
    static constexpr T INF = numeric_limits<T>::max(), NINF = numeric_limits<T>::lowest();
    int n;
    vector<T> {", ".join(comps)};  // internal nodes 1 .. n-1: pending clamp {form}
    vector<T> val;  // leaf values

    // O(N)
    explicit {name}(const vector<T>& a) : n((int)a.size()), {inits}, val(a) {{}}

    // apply clamp ({params}) on top of whatever node x already holds
    void apply(int x, {sig}) {{
        if (x >= n) {{ val[x - n] = {leaf}; return; }}
{chr(10).join(comp)}
    }}

    // O(logN) -- push every pending tag on leaf p's root-to-leaf path down to its children
    void push(int p) {{
        for (int h = 31 - __builtin_clz(p); h > 0; h--) {{
            int x = p >> h;
            if ({cond}) apply(2 * x, {tv}), apply(2 * x + 1, {tv}), {reset};
        }}
    }}

    void update(int l, int r, {sig}) {{
        l += n, r += n;
        push(l), push(r);
        for (r++; l < r; l >>= 1, r >>= 1) {{
            if (l & 1) apply(l++, {params});
            if (r & 1) apply(--r, {params});
        }}
    }}
{upd_text}
    // O(logN) -- a[i]: start from the leaf and apply ancestors' clamps bottom-up (deeper tags are older)
    T pointGet(int i) const {{
        T v = val[i];
        for (int p = (i + n) >> 1; p; p >>= 1) v = {getv};
        return v;
    }}

    // O(N) -- the whole array: push every tag down (a parent's index is below its children's, so in index order
    // each node's tag is complete when it is pushed), then read the leaves
    vector<T> getAll() {{
        for (int x = 1; x < n; x++)
            if ({cond}) apply(2 * x, {tv}), apply(2 * x + 1, {tv}), {reset};
        return val;
    }}

    // O(logN) -- a[i] = v
    void pointAssign(int i, T v) {{ push(i + n); val[i] = v; }}

    // O(logN) -- a[i] += delta
    void pointAdd(int i, T delta) {{ push(i + n); val[i] = val[i] + delta; }}

    // O(logN) -- a[i] = max(a[i], v)
    void pointChmax(int i, T v) {{ push(i + n); if (v > val[i]) val[i] = v; }}

    // O(logN) -- a[i] = min(a[i], v)
    void pointChmin(int i, T v) {{ push(i + n); if (v < val[i]) val[i] = v; }}
}};
'''


def main():
    for comps, (name, upd, _) in VARIANTS.items():
        folder = os.path.join(DIR, folder_name(sorted(POINT + upd)))
        os.makedirs(folder, exist_ok=True)
        write_template(os.path.join(folder, "template.py"), python(comps))
        write_template(os.path.join(folder, "template.cpp"), cpp(comps))
        print("wrote", os.path.basename(folder))


if __name__ == "__main__":
    main()
