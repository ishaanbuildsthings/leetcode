"""rangeTwinSpin(l, r): swap a[l] with a[l + 1], a[l + 2] with a[l + 3], ... in O(log N), alongside the sequence edits.

    python3 gen_pair_treap.py

The array is two implicit treaps in one node pool: E holds the even positions (a[0], a[2], ...), O the odd ones. A
range [l, r] is a slice of each. Swapping pairs trades the two slices; a reverse reverses them in place (l + r even:
parities stay) or crosses them over (l + r odd); an insert or erase shifts everything after it by one or more places,
which flips the parity of that tail when the shift is odd, so the two tails trade places. One template per subset of
{rangeSum, rangeMin, rangeMax} (with any of them, also rangeAdd / rangeAssign), like gen_treap.py.
"""
import itertools
import os
import shutil

from gen_treap import AGG_FIELD, AGG_OPS, wrap
from gen_treap import no_push
from note_lang import folder_name, write_template

DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "range-queries")
DTYPE = "pair-treap"
SEQ = ["append", "appendLeft", "eraseRange", "getAll", "insertAt", "pop", "popLeft", "rangeTwinSpin"]
POINT = ["pointAdd", "pointAssign", "pointChmax", "pointChmin", "pointGet"]


def header(cm, ops, aggs):
    lines = [f"@operations: {' '.join(ops)}", f"@data-structure-type: {DTYPE}", "@complexities:"]
    lines += [f"  {op}: {'N' if op == 'getAll' else 'log(N) expected'}" for op in ops] + ["  build: N", "@memory:", "  layout: none"]
    node = ["val", "sz", "L", "R", "pri"] + [AGG_FIELD[a] for a in aggs]
    tags = (["rev"] if "rangeReverse" in ops else []) + (["add"] if "rangeAdd" in ops else []) + (
        ["asg", "hasAsg"] if "rangeAssign" in ops else [])
    lines += [f"  node: {' '.join(f'{f}[1*N]' for f in node)}", f"  tags: {' '.join(f'{f}[1*N]' for f in tags) or 'none'}", "  other: none",
              "  note: N = every value ever inserted (erased nodes are not reused); two treaps (even / odd positions) share "
              "one node pool"]
    return "\n".join(f"{cm} {x}" for x in lines) + "\n"


def describe(aggs, ops=()):
    what = ", ".join([o for o in ("rangeAdd", "rangeAssign") if o in ops] + [AGG_OPS[a] for a in aggs])
    return ("Implicit treap pair: an array you can insert into / erase from anywhere, " + ("reverse ranges and " if "rangeReverse" in ops else "") +
            "swap adjacent pairs in a range (a[l] <-> a[l + 1], a[l + 2] <-> a[l + 3], ...), each in O(logN) expected, plus point ops" +
            (f", {what}" if what else "") + ". The even positions a[0], a[2], ... are one treap "
            "(E) and the odd ones another (O), in one node pool; a range [l, r] is a slice of each. All indices 0-based, "
            "ranges inclusive, always positions in the CURRENT array.")


# ------------------------------------------------------------------------------------------------ Python

def python(ops, aggs):
    A = bool(aggs)
    RV, AD, AS = "rangeReverse" in ops, "rangeAdd" in ops, "rangeAssign" in ops  # each tag only with its ops
    F = [AGG_FIELD[a] for a in aggs]
    slots = ["rE", "rO", "val", "pri", "L", "R", "sz"] + (["rev"] if RV else []) + F + (["add"] if AD else []) + (
        ["asg", "hasAsg"] if AS else [])
    p = [header("#", ops, aggs), "\n", wrap(describe(aggs, ops), "#"), "import random\n\n\nclass PairSwapTreap:\n",
         f"    __slots__ = ({', '.join(repr(s) for s in slots)})\n\n"]
    p.append('''    # O(N) -- arr: the initial array (may be empty)
    def __init__(self, arr):
        self.val, self.pri, self.L, self.R, self.sz = [0], [0], [0], [0], [0]  # node 0 = the empty tree
''' + ("        self.rev = [0]\n" if RV else "") + "".join(f"        self.{f} = [0]\n" for f in F) + ("        self.add = [0]\n" if AD else "") + (
        "        self.asg, self.hasAsg = [0], [0]\n" if AS else "") + '''        self.rE = self._build(arr[0::2])  # a[0], a[2], ...
        self.rO = self._build(arr[1::2])  # a[1], a[3], ...

    # O(1) -- the current length of the array
    def size(self):
        return self.sz[self.rE] + self.sz[self.rO]
''')
    pub = {
        "append": '''    # O(logN) expected -- append v to the end
    def append(self, v):
        self.insertAt(self.size(), v)
''',
        "insertAt": '''    # O(logN) expected -- insert v so it becomes a[i] (0 <= i <= size()); the tail after it moves one place, so its parity
    # flips: E's tail and O's tail trade places
    def insertAt(self, i, v):
        a, _, c, d, _, f = self._parts(i, i - 1)
        x, merge = self._newNode(v), self._merge
        if i % 2 == 0:
            self.rE, self.rO = merge(merge(a, x), f), merge(d, c)
        else:
            self.rE, self.rO = merge(a, f), merge(merge(d, x), c)
''',
        "appendLeft": '''    # O(logN) expected -- insert v at the front (it becomes a[0]; everything else shifts right by one)
    def appendLeft(self, v):
        self.insertAt(0, v)
''',
        "pop": '''    # O(logN) expected -- remove a[i] and return it; everything after it shifts left by one
    def pop(self, i):
        v = self.pointGet(i)
        self.eraseRange(i, i)
        return v
''',
        "popLeft": '''    # O(logN) expected -- remove a[0] and return it
    def popLeft(self):
        return self.pop(0)
''',
        "eraseRange": '''    # O(logN) expected -- remove a[l..r]; the tail moves r - l + 1 places, so with an odd count the tails trade places
    def eraseRange(self, l, r):
        a, _, c, d, _, f = self._parts(l, r)
        if (r - l + 1) % 2 == 0:
            self.rE, self.rO = self._merge(a, c), self._merge(d, f)
        else:
            self.rE, self.rO = self._merge(a, f), self._merge(d, c)
''',
        "rangeReverse": '''    # O(logN) expected -- reverse a[l..r] in place: a[p] goes to l + r - p, the same parity when l + r is even (each
    # slice reverses in place) and the other parity when it is odd (the slices, then equally long, cross over reversed)
    def rangeReverse(self, l, r):
        a, b, c, d, e, f = self._parts(l, r)
        self._applyRev(b)
        self._applyRev(e)
        if (l + r) % 2:
            b, e = e, b
        self._join(a, b, c, d, e, f)
''',
        "rangeTwinSpin": '''    # O(logN) expected -- swap a[l] <-> a[l + 1], a[l + 2] <-> a[l + 3], ... over [l, r] (with an odd length a[r] stays):
    # the pairs' even and odd halves are two slices of equal length, which trade places
    def rangeTwinSpin(self, l, r):
        k = (r - l + 1) // 2
        if k:
            a, b, c, d, e, f = self._parts(l, l + 2 * k - 1)
            self._join(a, e, c, d, b, f)
''',
        "getAll": '''    # O(N) -- the whole current array, every pending tag applied on the way
    def getAll(self):
        ev, od = self._inorder(self.rE), self._inorder(self.rO)
        out = [0] * (len(ev) + len(od))
        out[0::2], out[1::2] = ev, od
        return out
''',
        "pointGet": '''    # O(logN) expected -- a[i]
    def pointGet(self, i):
        return self.val[self._find(i)[0]]
''',
    }
    for op, expr, doc in (("pointAssign", "v", "a[i] = v"), ("pointAdd", "self.val[t] + v", "a[i] += v"),
                          ("pointChmax", "max(self.val[t], v)", "a[i] = max(a[i], v)"),
                          ("pointChmin", "min(self.val[t], v)", "a[i] = min(a[i], v)")):
        pub[op] = f'''    # O(logN) expected -- {doc}
    def {op}(self, i, v):
        t, path = self._find(i)
        self.val[t] = {expr}
''' + ("        self._pull(t)\n        for x in reversed(path):\n            self._pull(x)\n" if A else "")
    if AD or AS:
        for op, fn, doc in (("rangeAdd", "_applyAdd", "a[i] += v"), ("rangeAssign", "_applyAssign", "a[i] = v")):
            pub[op] = f'''    # O(logN) expected -- {doc} for i in [l, r]
    def {op}(self, l, r, v):
        a, b, c, d, e, f = self._parts(l, r)
        self.{fn}(b, v)
        self.{fn}(e, v)
        self._join(a, b, c, d, e, f)
'''
    if "sum" in aggs:
        pub["rangeSum"] = '''    # O(logN) expected -- a[l] + ... + a[r]
    def rangeSum(self, l, r):
        a, b, c, d, e, f = self._parts(l, r)
        res = self.sm[b] + self.sm[e]
        self._join(a, b, c, d, e, f)
        return res
'''
    for agg, op, fn in (("min", "rangeMin", "min"), ("max", "rangeMax", "max")):
        if agg in aggs:
            fl = AGG_FIELD[agg]
            pub[op] = f'''    # O(logN) expected -- {fn} of a[l..r]
    def {op}(self, l, r):
        a, b, c, d, e, f = self._parts(l, r)
        res = self.{fl}[b] if not e else self.{fl}[e] if not b else {fn}(self.{fl}[b], self.{fl}[e])
        self._join(a, b, c, d, e, f)
        return res
'''
    p.append("\n" + "\n".join(pub[op] for op in ops if op in pub))
    pull = ["        l, r = self.L[x], self.R[x]", "        self.sz[x] = self.sz[l] + self.sz[r] + 1"]
    if "sum" in aggs:
        pull.append("        self.sm[x] = self.sm[l] + self.val[x] + self.sm[r]")
    for agg, cmp in (("min", "<"), ("max", ">")):
        if agg in aggs:
            f = AGG_FIELD[agg]
            pull += ["        m = self.val[x]", f"        if l and self.{f}[l] {cmp} m:", f"            m = self.{f}[l]",
                     f"        if r and self.{f}[r] {cmp} m:", f"            m = self.{f}[r]", f"        self.{f}[x] = m"]
    new = ["        x = len(self.val)", "        self.val.append(v)", "        self.pri.append(random.getrandbits(62))",
           "        self.L.append(0)", "        self.R.append(0)", "        self.sz.append(1)"] + (["        self.rev.append(0)"] if RV else [])
    new += [f"        self.{f}.append(v)" for f in F] + (["        self.add.append(0)"] if AD else []) + (
        ["        self.asg.append(0)", "        self.hasAsg.append(0)"] if AS else [])
    p.append('''
    # ---- internals ----

    # counts of even / odd positions below x: (x + 1) // 2 and x // 2
    def _parts(self, l, r):  # (E before, E in [l, r], E after, O before, O in [l, r], O after) as six trees
        e1, e2, o1, o2 = (l + 1) // 2, (r + 2) // 2, l // 2, (r + 1) // 2
        a, b = self._split(self.rE, e1)
        b, c = self._split(b, e2 - e1)
        d, e = self._split(self.rO, o1)
        e, f = self._split(e, o2 - o1)
        return a, b, c, d, e, f

    def _join(self, a, b, c, d, e, f):
        merge = self._merge
        self.rE, self.rO = merge(merge(a, b), c), merge(merge(d, e), f)

    # (node holding a[i], the nodes above it), every tag on the way pushed
    def _find(self, i):
        L, sz, t, path, k = self.L, self.sz, self.rO if i % 2 else self.rE, [], i // 2
        while True:
            self._push(t)
            ls = sz[L[t]]
            if k == ls:
                return t, path
            path.append(t)
            if k < ls:
                t = L[t]
            else:
                k -= ls + 1
                t = self.R[t]

    def _inorder(self, t):
        L, R, val = self.L, self.R, self.val
        out, stack = [], []
        while stack or t:
            while t:
                self._push(t)
                stack.append(t)
                t = L[t]
            t = stack.pop()
            out.append(val[t])
            t = R[t]
        return out

    def _newNode(self, v):
''' + "\n".join(new) + '''
        return x

    # a treap of new nodes holding vals in order: a Cartesian tree in one pass, O(len)
    def _build(self, vals):
        pri, L, R = self.pri, self.L, self.R
        stack = []
        for v in vals:
            x, last = self._newNode(v), 0
            while stack and pri[stack[-1]] < pri[x]:
                last = stack.pop()
            L[x] = last
            if stack:
                R[stack[-1]] = x
            stack.append(x)
        root = stack[0] if stack else 0
        order, todo = [], ([root] if root else [])
        while todo:
            x = todo.pop()
            order.append(x)
            if L[x]:
                todo.append(L[x])
            if R[x]:
                todo.append(R[x])
        for x in reversed(order):
            self._pull(x)
        return root

    def _pull(self, x):
''' + "\n".join(pull) + "\n" + ('''
    def _applyRev(self, x):
        if x:
            self.L[x], self.R[x] = self.R[x], self.L[x]
            self.rev[x] ^= 1
''' if RV else ""))
    if AD or AS:
        add = ["        if not x:", "            return", "        self.val[x] += v"] + (["        self.sm[x] += v * self.sz[x]"] if "sum" in aggs else []) + [
            f"        self.{AGG_FIELD[a]}[x] += v" for a in aggs if a != "sum"] + (
            ["        if self.hasAsg[x]:", "            self.asg[x] += v", "        else:", "            self.add[x] += v"] if AS else
            ["        self.add[x] += v"])
        asg = ["        if not x:", "            return", "        self.val[x] = v"] + (["        self.sm[x] = v * self.sz[x]"] if "sum" in aggs else []) + [
            f"        self.{AGG_FIELD[a]}[x] = v" for a in aggs if a != "sum"] + ["        self.hasAsg[x] = 1", "        self.asg[x] = v"] + (["        self.add[x] = 0"] if AD else [])
        p.append(("\n    def _applyAdd(self, x, v):\n" + "\n".join(add) + "\n" if AD else "") +
                 ("\n    def _applyAssign(self, x, v):\n" + "\n".join(asg) + "\n" if AS else ""))
    push = ["        if self.rev[x]:", "            self._applyRev(self.L[x])", "            self._applyRev(self.R[x])", "            self.rev[x] = 0"] if RV else []
    if AS:
        push += ["        if self.hasAsg[x]:", "            self._applyAssign(self.L[x], self.asg[x])", "            self._applyAssign(self.R[x], self.asg[x])",
                 "            self.hasAsg[x] = 0"]
    if AD:
        push += ["        elif self.add[x]:" if AS else "        if self.add[x]:", "            self._applyAdd(self.L[x], self.add[x])",
                 "            self._applyAdd(self.R[x], self.add[x])", "            self.add[x] = 0"]
    p.append(('''
    def _push(self, x):  # hand x's pending tags to its children
''' + "\n".join(push) + "\n" if push else "") + '''
    def _split(self, t, k):  # (first k of t, the rest)
        if not t:
            return 0, 0
        self._push(t)
        L, R = self.L, self.R
        if self.sz[L[t]] >= k:
            a, L[t] = self._split(L[t], k)
            self._pull(t)
            return a, t
        R[t], b = self._split(R[t], k - self.sz[L[t]] - 1)
        self._pull(t)
        return t, b

    def _merge(self, a, b):  # a's elements, then b's
        if not a or not b:
            return a or b
        if self.pri[a] > self.pri[b]:
            self._push(a)
            self.R[a] = self._merge(self.R[a], b)
            self._pull(a)
            return a
        self._push(b)
        self.L[b] = self._merge(a, self.L[b])
        self._pull(b)
        return b
''')
    out = "".join(p)
    return out if RV or AD or AS else no_push(out, "py")


# ------------------------------------------------------------------------------------------------ C++

def cpp(ops, aggs):
    A = bool(aggs)
    RV, AD, AS = "rangeReverse" in ops, "rangeAdd" in ops, "rangeAssign" in ops  # each tag only with its ops
    mm = [AGG_FIELD[a] for a in aggs if a != "sum"]
    c = [header("//", ops, aggs), "\n", wrap(describe(aggs, ops), "//"), "// T: int, long long, ..." +
         ("; sums are kept in S (long long for small T)" if "sum" in aggs else "") + ".\ntemplate <typename T>\nstruct PairSwapTreap {\n"]
    if "sum" in aggs:
        c.append("    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;\n")
    fields = ["    int rE = 0, rO = 0;  // the even positions a[0], a[2], ... and the odd ones", "    vector<T> val{T(0)};  // node 0 is the empty tree",
              "    vector<unsigned long long> pri{0};", "    vector<int> L{0}, R{0}, sz{0};"] + (["    vector<char> rev{0};"] if RV else [])
    if "sum" in aggs:
        fields.append("    vector<S> sm{S(0)};")
    if mm:
        fields.append(f"    vector<T> {', '.join(f + '{T(0)}' for f in mm)};")
    if AD:
        fields.append("    vector<T> add{T(0)};")
    if AS:
        fields += ["    vector<T> asg{T(0)};", "    vector<char> hasAsg{0};"]
    c.append("\n".join(fields) + '''

    static unsigned long long rnd() {
        static mt19937_64 g(chrono::steady_clock::now().time_since_epoch().count());
        return g();
    }

    // O(N) -- arr: the initial array (may be empty)
    explicit PairSwapTreap(const vector<T>& arr) {
        vector<T> ev, od;
        for (size_t i = 0; i < arr.size(); i++) (i % 2 ? od : ev).push_back(arr[i]);
        rE = build(ev), rO = build(od);
    }

    // O(1) -- the current length of the array
    int size() const { return sz[rE] + sz[rO]; }
''')
    pub = {
        "append": '''    // O(logN) expected -- append v to the end
    void append(T v) { insertAt(size(), v); }
''',
        "insertAt": '''    // O(logN) expected -- insert v so it becomes a[i] (0 <= i <= size()); the tail after it moves one place, so its parity
    // flips: E's tail and O's tail trade places
    void insertAt(int i, T v) {
        int a, b, c, d, e, f, x = newNode(v);
        parts(i, i - 1, a, b, c, d, e, f);
        if (i % 2 == 0) rE = merge(merge(a, x), f), rO = merge(d, c);
        else rE = merge(a, f), rO = merge(merge(d, x), c);
    }
''',
        "appendLeft": '''    // O(logN) expected -- insert v at the front (it becomes a[0]; everything else shifts right by one)
    void appendLeft(T v) { insertAt(0, v); }
''',
        "pop": '''    // O(logN) expected -- remove a[i] and return it; everything after it shifts left by one
    T pop(int i) {
        T v = pointGet(i);
        eraseRange(i, i);
        return v;
    }
''',
        "popLeft": '''    // O(logN) expected -- remove a[0] and return it
    T popLeft() { return pop(0); }
''',
        "eraseRange": '''    // O(logN) expected -- remove a[l..r]; the tail moves r - l + 1 places, so with an odd count the tails trade places
    void eraseRange(int l, int r) {
        int a, b, c, d, e, f;
        parts(l, r, a, b, c, d, e, f);
        if ((r - l + 1) % 2 == 0) rE = merge(a, c), rO = merge(d, f);
        else rE = merge(a, f), rO = merge(d, c);
    }
''',
        "rangeReverse": '''    // O(logN) expected -- reverse a[l..r] in place: a[p] goes to l + r - p, the same parity when l + r is even (each
    // slice reverses in place) and the other parity when it is odd (the slices, then equally long, cross over reversed)
    void rangeReverse(int l, int r) {
        int a, b, c, d, e, f;
        parts(l, r, a, b, c, d, e, f);
        applyRev(b), applyRev(e);
        if ((l + r) % 2) swap(b, e);
        join(a, b, c, d, e, f);
    }
''',
        "rangeTwinSpin": '''    // O(logN) expected -- swap a[l] <-> a[l + 1], a[l + 2] <-> a[l + 3], ... over [l, r] (with an odd length a[r] stays):
    // the pairs' even and odd halves are two slices of equal length, which trade places
    void rangeTwinSpin(int l, int r) {
        int k = (r - l + 1) / 2, a, b, c, d, e, f;
        if (!k) return;
        parts(l, l + 2 * k - 1, a, b, c, d, e, f);
        join(a, e, c, d, b, f);
    }
''',
        "getAll": '''    // O(N) -- the whole current array, every pending tag applied on the way
    vector<T> getAll() {
        vector<T> ev = inorder(rE), od = inorder(rO), out(ev.size() + od.size());
        for (size_t i = 0; i < ev.size(); i++) out[2 * i] = ev[i];
        for (size_t i = 0; i < od.size(); i++) out[2 * i + 1] = od[i];
        return out;
    }
''',
        "pointGet": '''    // O(logN) expected -- a[i]
    T pointGet(int i) { return val[find(i)]; }
''',
    }
    for op, expr, doc in (("pointAssign", "v", "a[i] = v"), ("pointAdd", "val[t] + v", "a[i] += v"),
                          ("pointChmax", "max(val[t], v)", "a[i] = max(a[i], v)"), ("pointChmin", "min(val[t], v)", "a[i] = min(a[i], v)")):
        pub[op] = (f"    // O(logN) expected -- {doc}\n    void {op}(int i, T v) {{\n" +
                   ("        vector<int> path;\n        int t = find(i, &path);\n" if A else "        int t = find(i);\n") + f"        val[t] = {expr};\n" +
                   ("        pull(t);\n        for (int k = (int)path.size() - 1; k >= 0; k--) pull(path[k]);\n" if A else "") + "    }\n")
    if AD or AS:
        for op, fn, doc in (("rangeAdd", "applyAdd", "a[i] += v"), ("rangeAssign", "applyAssign", "a[i] = v")):
            pub[op] = f'''    // O(logN) expected -- {doc} for i in [l, r]
    void {op}(int l, int r, T v) {{
        int a, b, c, d, e, f;
        parts(l, r, a, b, c, d, e, f);
        {fn}(b, v), {fn}(e, v);
        join(a, b, c, d, e, f);
    }}
'''
    if "sum" in aggs:
        pub["rangeSum"] = '''    // O(logN) expected -- a[l] + ... + a[r]
    S rangeSum(int l, int r) {
        int a, b, c, d, e, f;
        parts(l, r, a, b, c, d, e, f);
        S res = sm[b] + sm[e];
        join(a, b, c, d, e, f);
        return res;
    }
'''
    for agg, op, fn in (("min", "rangeMin", "min"), ("max", "rangeMax", "max")):
        if agg in aggs:
            fl = AGG_FIELD[agg]
            pub[op] = f'''    // O(logN) expected -- {fn} of a[l..r]
    T {op}(int l, int r) {{
        int a, b, c, d, e, f;
        parts(l, r, a, b, c, d, e, f);
        T res = !e ? {fl}[b] : !b ? {fl}[e] : {fn}({fl}[b], {fl}[e]);
        join(a, b, c, d, e, f);
        return res;
    }}
'''
    c.append("\n" + "\n".join(pub[op] for op in ops if op in pub))
    pull = ["        int l = L[x], r = R[x];", "        sz[x] = sz[l] + sz[r] + 1;"] + (["        sm[x] = sm[l] + S(val[x]) + sm[r];"] if "sum" in aggs else [])
    for agg, fn in (("min", "min"), ("max", "max")):
        if agg in aggs:
            f = AGG_FIELD[agg]
            pull += [f"        {f}[x] = val[x];", f"        if (l) {f}[x] = {fn}({f}[x], {f}[l]);", f"        if (r) {f}[x] = {fn}({f}[x], {f}[r]);"]
    new = ["        val.push_back(v), pri.push_back(rnd()), L.push_back(0), R.push_back(0), sz.push_back(1)" + (", rev.push_back(0);" if RV else ";")] + (
        ["        sm.push_back(S(v));"] if "sum" in aggs else []) + [f"        {f}.push_back(v);" for f in mm] + (
        ["        add.push_back(T(0));"] if AD else []) + (["        asg.push_back(T(0)), hasAsg.push_back(0);"] if AS else [])
    c.append('''
    // ---- internals ----

    // E before, E in [l, r], E after, O before, O in [l, r], O after; even / odd positions below x: (x + 1) / 2 and x / 2
    void parts(int l, int r, int& a, int& b, int& c, int& d, int& e, int& f) {
        int e1 = (l + 1) / 2, e2 = (r + 2) / 2, o1 = l / 2, o2 = (r + 1) / 2;
        split(rE, e1, a, b), split(b, e2 - e1, b, c);
        split(rO, o1, d, e), split(e, o2 - o1, e, f);
    }

    void join(int a, int b, int c, int d, int e, int f) { rE = merge(merge(a, b), c), rO = merge(merge(d, e), f); }

    // the node holding a[i], every tag on the way pushed; path (if given) gets the nodes above it
    int find(int i, vector<int>* path = nullptr) {
        int t = i % 2 ? rO : rE, k = i / 2;
        while (true) {
            push(t);
            int ls = sz[L[t]];
            if (k == ls) return t;
            if (path) path->push_back(t);
            if (k < ls) t = L[t];
            else k -= ls + 1, t = R[t];
        }
    }

    vector<T> inorder(int t) {
        vector<T> out;
        vector<int> st;
        while (!st.empty() || t) {
            while (t) push(t), st.push_back(t), t = L[t];
            t = st.back(), st.pop_back();
            out.push_back(val[t]);
            t = R[t];
        }
        return out;
    }

    int newNode(T v) {
''' + "\n".join(new) + '''
        return (int)val.size() - 1;
    }

    // a treap of new nodes holding vals in order: a Cartesian tree in one pass, O(len)
    int build(const vector<T>& vals) {
        vector<int> stk, order, todo;
        for (const T& v : vals) {
            int x = newNode(v), last = 0;
            while (!stk.empty() && pri[stk.back()] < pri[x]) last = stk.back(), stk.pop_back();
            L[x] = last;
            if (!stk.empty()) R[stk.back()] = x;
            stk.push_back(x);
        }
        int rt = stk.empty() ? 0 : stk[0];
        if (rt) todo.push_back(rt);
        while (!todo.empty()) {
            int x = todo.back();
            todo.pop_back(), order.push_back(x);
            if (L[x]) todo.push_back(L[x]);
            if (R[x]) todo.push_back(R[x]);
        }
        for (int k = (int)order.size() - 1; k >= 0; k--) pull(order[k]);
        return rt;
    }

    void pull(int x) {
''' + "\n".join(pull) + '''
    }
''' + ('''
    void applyRev(int x) {
        if (x) swap(L[x], R[x]), rev[x] ^= 1;
    }
''' if RV else ""))
    if AD or AS:
        add = ["        if (!x) return;", "        val[x] += v;"] + (["        sm[x] += S(v) * sz[x];"] if "sum" in aggs else []) + [
            f"        {f}[x] += v;" for f in mm] + ["        (hasAsg[x] ? asg[x] : add[x]) += v;" if AS else "        add[x] += v;"]
        asg = ["        if (!x) return;", "        val[x] = v;"] + (["        sm[x] = S(v) * sz[x];"] if "sum" in aggs else []) + [
            f"        {f}[x] = v;" for f in mm] + ["        hasAsg[x] = 1, asg[x] = v" + (", add[x] = 0;" if AD else ";")]
        c.append(("\n    void applyAdd(int x, T v) {\n" + "\n".join(add) + "\n    }\n" if AD else "") +
                 ("\n    void applyAssign(int x, T v) {\n" + "\n".join(asg) + "\n    }\n" if AS else ""))
    push = ["        if (rev[x]) applyRev(L[x]), applyRev(R[x]), rev[x] = 0;"] if RV else []
    if AS:
        push.append("        if (hasAsg[x]) applyAssign(L[x], asg[x]), applyAssign(R[x], asg[x]), hasAsg[x] = 0;")
    if AD:
        push.append(("        else " if AS else "        ") + "if (add[x] != T(0)) applyAdd(L[x], add[x]), applyAdd(R[x], add[x]), add[x] = 0;")
    c.append(('''
    void push(int x) {  // hand x's pending tags to its children
''' + "\n".join(push) + "\n    }\n" if push else "") + '''
    void split(int t, int k, int& a, int& b) {  // a = first k of t, b = the rest
        if (!t) { a = b = 0; return; }
        push(t);
        if (sz[L[t]] >= k) split(L[t], k, a, L[t]), b = t;
        else split(R[t], k - sz[L[t]] - 1, R[t], b), a = t;
        pull(t);
    }

    int merge(int a, int b) {  // a's elements, then b's
        if (!a || !b) return a | b;
        if (pri[a] > pri[b]) {
            push(a);
            R[a] = merge(R[a], b);
            pull(a);
            return a;
        }
        push(b);
        L[b] = merge(a, L[b]);
        pull(b);
        return b;
    }
};
''')
    out = "".join(c)
    return out if RV or AD or AS else no_push(out, "cpp")


UPDATES = {"": [], "add": ["rangeAdd"], "assign": ["rangeAssign"], "addassign": ["rangeAdd", "rangeAssign"]}


def main():
    for d in os.listdir(DIR):  # this generator's folders are regenerated (names follow the op lists)
        t = os.path.join(DIR, d, "template.py")
        if os.path.exists(t) and f"@data-structure-type: {DTYPE}" in open(t).read():
            shutil.rmtree(os.path.join(DIR, d))
    count = 0
    for k in range(4):
        # aggregates, range add / assign (their tags) and reverse (its tag) each only in the variants that ask for them
        for aggs, upd, rev in itertools.product(itertools.combinations(("sum", "min", "max"), k), UPDATES, (False, True)):
            count += 1
            ops = sorted(SEQ + POINT + [AGG_OPS[a] for a in aggs] + UPDATES[upd] + (["rangeReverse"] if rev else []))
            name = folder_name(ops)
            folder = os.path.join(DIR, name if len(name) <= 180 else DTYPE + "".join("-" + a for a in aggs) + (f"-{upd}" if upd else "") +
                                  ("-rev" if rev else ""))
            os.makedirs(folder, exist_ok=True)
            write_template(os.path.join(folder, "template.py"), python(ops, aggs))
            write_template(os.path.join(folder, "template.cpp"), cpp(ops, aggs))
    print("wrote", count, "pair treaps")


if __name__ == "__main__":
    main()
