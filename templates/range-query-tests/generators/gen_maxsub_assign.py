"""Max prefix / suffix sums with range assign: one template per set of maxima, so nobody pays for one they don't ask for.

    python3 gen_maxsub_assign.py

The same tree as MaxSubarrayAssignTree (maxPrefixSum-maxSubarraySum-maxSuffixSum-...-rangeAssign-rangeSum, all four
fields): a node keeps its sum plus the best prefix (pre) and / or best suffix (suf) of its range, and an assign tag.
maxSubarraySum needs both pre and suf (and best), so it stays in that template; here:
    pre      maxPrefixSum + rangeSum                 sm, pre
    suf      maxSuffixSum + rangeSum                 sm, suf
    pre+suf  maxPrefixSum + maxSuffixSum + rangeSum  sm, pre, suf
"""
import os

from note_lang import folder_name, write_template

DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "range-queries")
POINT = ["pointAdd", "pointAssign", "pointChmax", "pointChmin", "pointGet"]
VARIANTS = {("pre",): "MaxPrefixAssignTree", ("suf",): "MaxSuffixAssignTree", ("pre", "suf"): "MaxPrefixSuffixAssignTree"}
OP = {"pre": "maxPrefixSum", "suf": "maxSuffixSum"}
PY_MERGE = {"sm": "a[0] + b[0]", "pre": "max(a[{p}], a[0] + b[{p}])", "suf": "max(b[{s}], b[0] + a[{s}])"}
CPP_MERGE = {"sm": "a.sm + b.sm", "pre": "max(a.pre, a.sm + b.pre)", "suf": "max(b.suf, b.sm + a.suf)"}
DOC = {"pre": "max over l <= i <= r of a[l] + ... + a[i]", "suf": "max over l <= i <= r of a[i] + ... + a[r]"}


def ops_of(fields):
    return sorted(POINT + ["getAll", "rangeAssign", "rangeSum"] + [OP[f] for f in fields])


def header(cm, fields):
    ops = ops_of(fields)
    F = ["sm"] + list(fields)
    lines = [f"@operations: {' '.join(ops)}", "@data-structure-type: lazy-seg-tree", "@complexities:"]
    lines += [f"  {op}: {'N' if op == 'getAll' else 'log(N)'}" for op in ops] + ["  build: N", "@memory:", "  layout: pow2-iterative",
              "  node: " + " ".join(f"{f}[4*N]" for f in F), "  tags: asg[2*N] hasAsg[2*N]", "  other: none",
              "  note: tags live on the internal nodes only"]
    return "\n".join(f"{cm} {x}" for x in lines) + "\n"


def doc(cm, fields):
    what = " / ".join(("max prefix" if f == "pre" else "max suffix") for f in fields)
    return (f"""{cm} Range {what} sum, plus range sum, with RANGE ASSIGN and point updates. All indices 0-based, ranges inclusive
{cm} [l, r]. The maxima are over NON-EMPTY pieces; when the empty piece is allowed (answer >= 0), take max(0, ...).
{cm} A node assigned v over len slots is fully known: sum = v * len, and its best {"prefix / suffix" if len(fields) > 1 else "prefix" if fields[0] == "pre" else "suffix"} is v * len if v > 0,
{cm} else just v (one element). So assign is an ordinary lazy tag. Iterative lazy tree over a power-of-two layout;
{cm} queries fold a left and a right accumulator (not commutative).
""")


def python(fields):
    F = ["sm"] + list(fields)
    idx = {f: k for k, f in enumerate(F)}
    name = VARIANTS[fields]
    merge = ", ".join(PY_MERGE[f].format(p=idx.get("pre"), s=idx.get("suf")) for f in F)
    slots = ", ".join(f'"{x}"' for x in ["n", "size", "H"] + F + ["asg", "hasAsg"])
    q = "".join(f'''
    # O(logN) -- {DOC[f]}
    def {OP[f]}(self, l, r):
        return self._query(l, r)[{idx[f]}]
''' for f in fields)
    return header("#", fields) + "\n" + doc("#", fields) + f'''

class {name}:
    __slots__ = ({slots})

    # O(N)
    def __init__(self, arr):
        n = self.n = len(arr)
        size, H = 1, 0
        while size < max(n, 1):
            size <<= 1
            H += 1
        self.size, self.H = size, H
{"".join(f"        self.{f} = [0] * (2 * size){chr(10)}" for f in F)}        for i, v in enumerate(arr):
            p = size + i
            {" = ".join(f"self.{f}[p]" for f in F)} = v
        for x in range(size - 1, 0, -1):
            self._pull(x)
        self.asg = [0] * size  # tags live on internal nodes only
        self.hasAsg = [False] * size

    @staticmethod
    def _merge(a, b):
        return ({merge})

    def _node(self, x):
        return {", ".join(f"self.{f}[x]" for f in F)}

    def _pull(self, x):
        {", ".join(f"self.{f}[x]" for f in F)} = self._merge(self._node(2 * x), self._node(2 * x + 1))

    # node x (covering `length` slots) becomes `length` copies of v
    def _setAll(self, x, length, v):
        s = v * length
        b = s if v > 0 else v
        self.sm[x] = s
        {" = ".join(f"self.{f}[x]" for f in fields)} = b
        if x < self.size:
            self.hasAsg[x] = True
            self.asg[x] = v

    def _push(self, x, childLen):
        if self.hasAsg[x]:
            v = self.asg[x]
            self._setAll(2 * x, childLen, v)
            self._setAll(2 * x + 1, childLen, v)
            self.hasAsg[x] = False

    def _pushToRoot(self, p):
        for s in range(self.H, 0, -1):
            self._push(p >> s, 1 << (s - 1))

    # a node assigned during this update keeps its own tag's value
    def _recomputeToRoot(self, p):
        p >>= 1
        length = 2
        while p:
            if self.hasAsg[p]:
                self._setAll(p, length, self.asg[p])
            else:
                self._pull(p)
            p >>= 1
            length <<= 1

    # O(logN) -- a[i] = v for i in [l, r]
    def rangeAssign(self, l, r, v):
        if l > r:
            return
        l0, r0 = l + self.size, r + self.size
        self._pushToRoot(l0)
        self._pushToRoot(r0)
        lo, hi, length = l0, r0 + 1, 1
        while lo < hi:
            if lo & 1:
                self._setAll(lo, length, v)
                lo += 1
            if hi & 1:
                hi -= 1
                self._setAll(hi, length, v)
            lo >>= 1
            hi >>= 1
            length <<= 1
        self._recomputeToRoot(l0)
        self._recomputeToRoot(r0)

    # O(logN) -- ({", ".join(F)}) of a[l..r], l <= r
    def _query(self, l, r):
        l += self.size
        r += self.size
        self._pushToRoot(l)
        self._pushToRoot(r)
        left = right = None
        r += 1
        while l < r:
            if l & 1:
                left = self._node(l) if left is None else self._merge(left, self._node(l))
                l += 1
            if r & 1:
                r -= 1
                right = self._node(r) if right is None else self._merge(self._node(r), right)
            l >>= 1
            r >>= 1
        if right is None:
            return left
        if left is None:
            return right
        return self._merge(left, right)
{q}
    # O(logN) -- a[l] + ... + a[r]
    def rangeSum(self, l, r):
        return self._query(l, r)[0] if l <= r else 0

    # O(logN) -- a[i]
    def pointGet(self, i):
        p = i + self.size
        self._pushToRoot(p)
        return self.sm[p]

    # O(N) -- the whole array: push every tag down one level at a time from the root, then read the leaves
    def getAll(self):
        H = self.H
        for s in range(H, 0, -1):
            for x in range(1 << (H - s), 1 << (H - s + 1)):
                self._push(x, 1 << (s - 1))
        return self.sm[self.size:self.size + self.n]

    # O(logN) -- a[i] = val
    def pointAssign(self, i, val):
        self.rangeAssign(i, i, val)

    # O(logN) -- a[i] += delta
    def pointAdd(self, i, delta):
        self.rangeAssign(i, i, self.pointGet(i) + delta)

    # O(logN) -- a[i] = max(a[i], val)
    def pointChmax(self, i, val):
        if val > self.pointGet(i):
            self.rangeAssign(i, i, val)

    # O(logN) -- a[i] = min(a[i], val)
    def pointChmin(self, i, val):
        if val < self.pointGet(i):
            self.rangeAssign(i, i, val)
'''


def cpp(fields):
    F = ["sm"] + list(fields)
    name = VARIANTS[fields]
    merge = ", ".join(CPP_MERGE[f] for f in F)
    q = "".join(f'''
    // O(logN) -- {DOC[f]}
    S {OP[f]}(int l, int r) {{ return query(l, r).{f}; }}
''' for f in fields)
    return header("//", fields) + "\n" + doc("//", fields) + f'''// T: int, long long, ...; sums are kept in S (long long for small T).
template <typename T>
struct {name} {{
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    struct Node {{ S {", ".join(F)}; }};
    int n, size, H;
    vector<Node> t;
    vector<T> asg;        // tags, internal nodes only
    vector<char> hasAsg;

    static Node merge(const Node& a, const Node& b) {{ return {{{merge}}}; }}

    // O(N)
    explicit {name}(const vector<T>& a) : n((int)a.size()), size(1), H(0) {{
        while (size < max(n, 1)) size <<= 1, H++;
        t.assign(2 * size, Node{{}}), asg.assign(size, 0), hasAsg.assign(size, 0);
        for (int i = 0; i < n; i++) t[size + i] = {{{", ".join("S(a[i])" for _ in F)}}};
        for (int x = size - 1; x > 0; x--) t[x] = merge(t[2 * x], t[2 * x + 1]);
    }}

    // node x (covering len slots) becomes len copies of v
    void setAll(int x, int len, T v) {{
        S s = S(v) * len, b = v > 0 ? s : S(v);
        t[x] = {{s{", b" * len(fields)}}};
        if (x < size) hasAsg[x] = 1, asg[x] = v;
    }}

    void push(int x, int childLen) {{
        if (!hasAsg[x]) return;
        setAll(2 * x, childLen, asg[x]), setAll(2 * x + 1, childLen, asg[x]);
        hasAsg[x] = 0;
    }}

    void pushToRoot(int p) {{
        for (int s = H; s > 0; s--) push(p >> s, 1 << (s - 1));
    }}

    // a node assigned during this update keeps its own tag's value
    void recomputeToRoot(int p) {{
        int len = 2;
        for (p >>= 1; p; p >>= 1, len <<= 1) {{
            if (hasAsg[p]) setAll(p, len, asg[p]);
            else t[p] = merge(t[2 * p], t[2 * p + 1]);
        }}
    }}

    // O(logN) -- a[i] = v for i in [l, r]
    void rangeAssign(int l, int r, T v) {{
        if (l > r) return;
        int l0 = l + size, r0 = r + size;
        pushToRoot(l0), pushToRoot(r0);
        for (int lo = l0, hi = r0 + 1, len = 1; lo < hi; lo >>= 1, hi >>= 1, len <<= 1) {{
            if (lo & 1) setAll(lo++, len, v);
            if (hi & 1) setAll(--hi, len, v);
        }}
        recomputeToRoot(l0), recomputeToRoot(r0);
    }}

    // O(logN) -- ({", ".join(F)}) of a[l..r], l <= r
    Node query(int l, int r) {{
        l += size, r += size;
        pushToRoot(l), pushToRoot(r);
        Node left{{}}, right{{}};
        bool lEmpty = true, rEmpty = true;
        for (r++; l < r; l >>= 1, r >>= 1) {{
            if (l & 1) left = lEmpty ? t[l] : merge(left, t[l]), lEmpty = false, l++;
            if (r & 1) --r, right = rEmpty ? t[r] : merge(t[r], right), rEmpty = false;
        }}
        if (rEmpty) return left;
        if (lEmpty) return right;
        return merge(left, right);
    }}
{q}
    // O(logN) -- a[l] + ... + a[r]
    S rangeSum(int l, int r) {{ return l <= r ? query(l, r).sm : S(0); }}

    // O(logN) -- a[i]
    T pointGet(int i) {{
        pushToRoot(i + size);
        return T(t[i + size].sm);
    }}

    // O(N) -- the whole array: push every tag down one level at a time from the root, then read the leaves
    vector<T> getAll() {{
        for (int s = H; s > 0; s--)
            for (int x = 1 << (H - s); x < 1 << (H - s + 1); x++) push(x, 1 << (s - 1));
        vector<T> out(n);
        for (int i = 0; i < n; i++) out[i] = T(t[size + i].sm);
        return out;
    }}

    // O(logN) -- a[i] = v
    void pointAssign(int i, T v) {{ rangeAssign(i, i, v); }}

    // O(logN) -- a[i] += delta
    void pointAdd(int i, T delta) {{ rangeAssign(i, i, pointGet(i) + delta); }}

    // O(logN) -- a[i] = max(a[i], v)
    void pointChmax(int i, T v) {{ if (v > pointGet(i)) rangeAssign(i, i, v); }}

    // O(logN) -- a[i] = min(a[i], v)
    void pointChmin(int i, T v) {{ if (v < pointGet(i)) rangeAssign(i, i, v); }}
}};
'''


def main():
    for fields in VARIANTS:
        folder = os.path.join(DIR, folder_name(ops_of(fields)))
        os.makedirs(folder, exist_ok=True)
        write_template(os.path.join(folder, "template.py"), python(fields))
        write_template(os.path.join(folder, "template.cpp"), cpp(fields))
        print("wrote", os.path.basename(folder))


if __name__ == "__main__":
    main()
