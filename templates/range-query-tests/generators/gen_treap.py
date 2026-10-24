"""Implicit treap (sequence edits: insert / erase anywhere, reverse, rotate, cut and paste), one template per set of
range aggregates it keeps.

    python3 gen_treap.py

Every variant has the sequence edits and the point ops. Sum, min and max each cost one more array per node, so every
subset of {rangeSum, rangeMin, rangeMax} gets its own template; a variant with at least one of them also takes
rangeAdd / rangeAssign (lazy tags), and the one with none keeps only the reverse tag.
"""
import itertools
import os

from note_lang import write_template

DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "range-queries")
SEQ = ["eraseAt", "eraseRange", "insertAt", "moveRange", "pushBack", "rangeReverse", "rangeRotateLeft", "rangeRotateRight"]
POINT = ["pointAdd", "pointAssign", "pointChmax", "pointChmin", "pointGet"]
AGG_OPS = {"sum": "rangeSum", "min": "rangeMin", "max": "rangeMax"}
AGG_FIELD = {"sum": "sm", "min": "mn", "max": "mx"}


def header(cm, ops, aggs):
    lines = [f"@operations: {' '.join(ops)}", "@data-structure-type: treap", "@complexities:"]
    lines += [f"  {op}: log(N) expected" for op in ops] + ["  build: N", "@memory:", "  layout: none"]
    node = ["val", "sz", "L", "R", "pri"] + [AGG_FIELD[a] for a in aggs]
    tags = ["rev"] + (["add", "asg", "hasAsg"] if aggs else [])
    lines += [f"  node: {' '.join(f'{f}[1*N]' for f in node)}", f"  tags: {' '.join(f'{f}[1*N]' for f in tags)}", "  other: none",
              "  note: N = every value ever inserted (the initial array plus each insertAt; erased nodes are not reused); "
              "split / merge recurse O(log N) deep in expectation"]
    return "\n".join(f"{cm} {x}" for x in lines) + "\n"


def describe(aggs):
    what = ", ".join(AGG_OPS[a] for a in aggs)
    return (f"Implicit treap: an array you can insert into / erase from anywhere, reverse, rotate and cut-and-paste, each in "
            f"O(logN) expected, plus point ops" + (f", rangeAdd / rangeAssign and {what}" if aggs else "") + ". "
            "All indices 0-based, ranges inclusive [l, r], and an index always means the position in the CURRENT array. "
            "Nodes keep their values in array order (an in-order walk); a node's position is the size of everything left "
            "of it. Lazy tags mean \"already applied to this node, not yet to its children\".")


def wrap(text, cm, width=118):
    out, line = [], cm
    for word in text.split():
        if len(line) + 1 + len(word) > width:
            out.append(line)
            line = cm
        line += " " + word
    out.append(line)
    return "\n".join(out) + "\n"


# ------------------------------------------------------------------------------------------------ Python

def python(ops, aggs):
    A = bool(aggs)
    slots = ["root", "val", "pri", "L", "R", "sz", "rev"] + [AGG_FIELD[a] for a in aggs] + (["add", "asg", "hasAsg"] if A else [])
    p = [header("#", ops, aggs), "\n", wrap(describe(aggs), "#"), "import random\n\n\nclass ImplicitTreap:\n"]
    p.append(f"    __slots__ = ({', '.join(repr(s) for s in slots)})\n\n")
    init = ["        n = len(arr)", "        self.val = [0] + list(arr)  # node 0 is the empty tree",
            "        self.pri = [0] + [random.getrandbits(62) for _ in range(n)]", "        self.L = [0] * (n + 1)",
            "        self.R = [0] * (n + 1)", "        self.sz = [0] + [1] * n", "        self.rev = [0] * (n + 1)"]
    init += [f"        self.{AGG_FIELD[a]} = [0] + list(arr)" for a in aggs]
    if A:
        init += ["        self.add = [0] * (n + 1)", "        self.asg = [0] * (n + 1)", "        self.hasAsg = [0] * (n + 1)"]
    p.append("    # O(N) -- arr: the initial array (may be empty)\n    def __init__(self, arr):\n" + "\n".join(init) + "\n")
    p.append('''        # Cartesian tree on (position, priority) in one pass: the stack is the current right spine
        pri, L, R = self.pri, self.L, self.R
        stack = []
        for x in range(1, n + 1):
            last = 0
            while stack and pri[stack[-1]] < pri[x]:
                last = stack.pop()
            L[x] = last
            if stack:
                R[stack[-1]] = x
            stack.append(x)
        self.root = stack[0] if stack else 0
        order, todo = [], ([self.root] if n else [])
        while todo:  # pre-order; pulled in reverse, so children before parents
            x = todo.pop()
            order.append(x)
            if L[x]:
                todo.append(L[x])
            if R[x]:
                todo.append(R[x])
        for x in reversed(order):
            self._pull(x)

    # O(1) -- the current length of the array
    def size(self):
        return self.sz[self.root]

''')
    pub = []
    pub.append(('insertAt', '''    # O(logN) expected -- insert v so it becomes a[i]; 0 <= i <= size() (i = size() appends)
    def insertAt(self, i, v):
        a, c = self._split(self.root, i)
        self.root = self._merge(self._merge(a, self._newNode(v)), c)
'''))
    pub.append(('pushBack', '''    # O(logN) expected -- append v to the end (it becomes a[size()])
    def pushBack(self, v):
        self.root = self._merge(self.root, self._newNode(v))
'''))
    pub.append(('eraseAt', '''    # O(logN) expected -- remove a[i]; everything after it shifts left by one
    def eraseAt(self, i):
        a, _, c = self._cut(i, i)
        self.root = self._merge(a, c)
'''))
    pub.append(('eraseRange', '''    # O(logN) expected -- remove a[l..r]; everything after it shifts left by r - l + 1
    def eraseRange(self, l, r):
        a, _, c = self._cut(l, r)
        self.root = self._merge(a, c)
'''))
    pub.append(('rangeReverse', '''    # O(logN) expected -- reverse a[l..r] in place
    def rangeReverse(self, l, r):
        a, b, c = self._cut(l, r)
        self._applyRev(b)
        self._join(a, b, c)
'''))
    pub.append(('rangeRotateLeft', '''    # O(logN) expected -- cyclic shift a[l..r] left by k (a[l + k] moves to l); any integer k, negative shifts right
    def rangeRotateLeft(self, l, r, k):
        a, b, c = self._cut(l, r)
        k %= r - l + 1
        if k:
            b1, b2 = self._split(b, k)
            b = self._merge(b2, b1)
        self._join(a, b, c)
'''))
    pub.append(('rangeRotateRight', '''    # O(logN) expected -- cyclic shift a[l..r] right by k (a[r - k + 1..r] move to the front); any integer k,
    # negative shifts left
    def rangeRotateRight(self, l, r, k):
        self.rangeRotateLeft(l, r, -k)
'''))
    pub.append(('moveRange', '''    # O(logN) expected -- cut a[l..r] out, then paste it back so it starts at index i of the array without it
    # (0 <= i <= size() - (r - l + 1); i = 0 moves it to the front, the max moves it to the end)
    def moveRange(self, l, r, i):
        a, b, c = self._cut(l, r)
        x, y = self._split(self._merge(a, c), i)
        self.root = self._merge(self._merge(x, b), y)
'''))
    pub.append(('pointGet', '''    # O(logN) expected -- a[i]
    def pointGet(self, i):
        L, sz, t = self.L, self.sz, self.root
        while True:
            self._push(t)
            ls = sz[L[t]]
            if i < ls:
                t = L[t]
            elif i == ls:
                return self.val[t]
            else:
                i -= ls + 1
                t = self.R[t]
'''))
    for op, expr, doc in (("pointAssign", "v", "a[i] = v"), ("pointAdd", "self.val[t] + v", "a[i] += v"),
                          ("pointChmax", "max(self.val[t], v)", "a[i] = max(a[i], v)"),
                          ("pointChmin", "min(self.val[t], v)", "a[i] = min(a[i], v)")):
        pub.append((op, f'''    # O(logN) expected -- {doc}
    def {op}(self, i, v):
        t, path = self._find(i)
        self.val[t] = {expr}
''' + ("        self._pull(t)\n        for x in reversed(path):\n            self._pull(x)\n" if A else "")))
    if A:
        pub.append(("rangeAdd", '''    # O(logN) expected -- a[i] += v for i in [l, r]
    def rangeAdd(self, l, r, v):
        a, b, c = self._cut(l, r)
        self._applyAdd(b, v)
        self._join(a, b, c)
'''))
        pub.append(("rangeAssign", '''    # O(logN) expected -- a[i] = v for i in [l, r]
    def rangeAssign(self, l, r, v):
        a, b, c = self._cut(l, r)
        self._applyAssign(b, v)
        self._join(a, b, c)
'''))
    for agg, (op, doc) in zip(("sum", "min", "max"), (("rangeSum", "a[l] + ... + a[r]"), ("rangeMin", "min of a[l..r]"),
                                                     ("rangeMax", "max of a[l..r]"))):
        if agg in aggs:
            pub.append((op, f'''    # O(logN) expected -- {doc}
    def {op}(self, l, r):
        a, b, c = self._cut(l, r)
        res = self.{AGG_FIELD[agg]}[b]
        self._join(a, b, c)
        return res
'''))
    pub.sort(key=lambda kv: ops.index(kv[0]))
    p.append("\n".join(body for _, body in pub))

    pull = ["        l, r = self.L[x], self.R[x]", "        self.sz[x] = self.sz[l] + self.sz[r] + 1"]
    if "sum" in aggs:
        pull.append("        self.sm[x] = self.sm[l] + self.val[x] + self.sm[r]")
    for agg, cmp in (("min", "<"), ("max", ">")):
        if agg in aggs:
            f = AGG_FIELD[agg]
            pull += [f"        m = self.val[x]", f"        if l and self.{f}[l] {cmp} m:", f"            m = self.{f}[l]",
                     f"        if r and self.{f}[r] {cmp} m:", f"            m = self.{f}[r]", f"        self.{f}[x] = m"]
    new = ["        x = len(self.val)", "        self.val.append(v)", "        self.pri.append(random.getrandbits(62))",
           "        self.L.append(0)", "        self.R.append(0)", "        self.sz.append(1)", "        self.rev.append(0)"]
    new += [f"        self.{AGG_FIELD[a]}.append(v)" for a in aggs]
    if A:
        new += ["        self.add.append(0)", "        self.asg.append(0)", "        self.hasAsg.append(0)"]
    p.append('''
    # ---- internals ----

    def _newNode(self, v):
''' + "\n".join(new) + '''
        return x

    # recompute x from its children
    def _pull(self, x):
''' + "\n".join(pull) + '''

    def _applyRev(self, x):
        if x:
            self.L[x], self.R[x] = self.R[x], self.L[x]
            self.rev[x] ^= 1
''')
    if A:
        add = ["        if not x:", "            return", "        self.val[x] += v"]
        asg = ["        if not x:", "            return", "        self.val[x] = v"]
        if "sum" in aggs:
            add.append("        self.sm[x] += v * self.sz[x]")
            asg.append("        self.sm[x] = v * self.sz[x]")
        for a in aggs:
            if a != "sum":
                add.append(f"        self.{AGG_FIELD[a]}[x] += v")
                asg.append(f"        self.{AGG_FIELD[a]}[x] = v")
        add += ["        if self.hasAsg[x]:  # an add on a pending assign shifts the assigned value", "            self.asg[x] += v",
                "        else:", "            self.add[x] += v"]
        asg += ["        self.hasAsg[x] = 1", "        self.asg[x] = v", "        self.add[x] = 0"]
        p.append('''
    def _applyAdd(self, x, v):
''' + "\n".join(add) + '''

    def _applyAssign(self, x, v):
''' + "\n".join(asg) + "\n")
    push = ['''        if self.rev[x]:
            self._applyRev(self.L[x])
            self._applyRev(self.R[x])
            self.rev[x] = 0''']
    if A:
        push.append('''        if self.hasAsg[x]:
            self._applyAssign(self.L[x], self.asg[x])
            self._applyAssign(self.R[x], self.asg[x])
            self.hasAsg[x] = 0
        elif self.add[x]:
            self._applyAdd(self.L[x], self.add[x])
            self._applyAdd(self.R[x], self.add[x])
            self.add[x] = 0''')
    p.append('''
    # hand x's pending tags to its children
    def _push(self, x):
''' + "\n".join(push) + '''

    # (first k elements of t, the rest)
    def _split(self, t, k):
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

    # a's elements, then b's
    def _merge(self, a, b):
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

    # (a[0..l-1], a[l..r], a[r+1..]) as three trees; put them back with _join
    def _cut(self, l, r):
        a, b = self._split(self.root, l)
        b, c = self._split(b, r - l + 1)
        return a, b, c

    def _join(self, a, b, c):
        self.root = self._merge(self._merge(a, b), c)

    # (node holding a[i], the nodes above it), with every tag on the way pushed
    def _find(self, i):
        L, sz, t, path = self.L, self.sz, self.root, []
        while True:
            self._push(t)
            ls = sz[L[t]]
            if i == ls:
                return t, path
            path.append(t)
            if i < ls:
                t = L[t]
            else:
                i -= ls + 1
                t = self.R[t]
''')
    return "".join(p)


# ------------------------------------------------------------------------------------------------ C++

def cpp(ops, aggs):
    A = bool(aggs)
    c = [header("//", ops, aggs), "\n", wrap(describe(aggs), "//"), "// T: int, long long, ...;" +
         (" sums are kept in S (long long for small T).\n" if "sum" in aggs else " values are stored as T.\n")]
    c.append("template <typename T>\nstruct ImplicitTreap {\n")
    if "sum" in aggs:
        c.append("    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;\n")
    fields = ["    int root = 0;", "    vector<T> val;  // node 0 is the empty tree", "    vector<unsigned long long> pri;",
              "    vector<int> L, R, sz;", "    vector<char> rev;"]
    if "sum" in aggs:
        fields.append("    vector<S> sm;")
    mm = [AGG_FIELD[a] for a in aggs if a != "sum"]
    if mm:
        fields.append(f"    vector<T> {', '.join(mm)};")
    if A:
        fields += ["    vector<T> add, asg;", "    vector<char> hasAsg;"]
    c.append("\n".join(fields) + "\n\n")
    c.append('''    static unsigned long long rnd() {
        static mt19937_64 g(chrono::steady_clock::now().time_since_epoch().count());
        return g();
    }

''')
    init = ["        int n = (int)arr.size();", "        val.assign(1, T(0)), val.insert(val.end(), arr.begin(), arr.end());",
            "        pri.assign(n + 1, 0), L.assign(n + 1, 0), R.assign(n + 1, 0), sz.assign(n + 1, 1), rev.assign(n + 1, 0);",
            "        sz[0] = 0;", "        for (int x = 1; x <= n; x++) pri[x] = rnd();"]
    if "sum" in aggs:
        init.append("        sm.assign(n + 1, S(0));")
    for f in mm:
        init.append(f"        {f} = val;")
    if A:
        init.append("        add.assign(n + 1, T(0)), asg.assign(n + 1, T(0)), hasAsg.assign(n + 1, 0);")
    c.append("    // O(N) -- arr: the initial array (may be empty)\n    explicit ImplicitTreap(const vector<T>& arr) {\n" + "\n".join(init) + '''
        // Cartesian tree on (position, priority) in one pass: the stack is the current right spine
        vector<int> stk;
        for (int x = 1; x <= n; x++) {
            int last = 0;
            while (!stk.empty() && pri[stk.back()] < pri[x]) last = stk.back(), stk.pop_back();
            L[x] = last;
            if (!stk.empty()) R[stk.back()] = x;
            stk.push_back(x);
        }
        root = stk.empty() ? 0 : stk[0];
        vector<int> order, todo;
        if (n) todo.push_back(root);
        while (!todo.empty()) {  // pre-order; pulled in reverse, so children before parents
            int x = todo.back();
            todo.pop_back(), order.push_back(x);
            if (L[x]) todo.push_back(L[x]);
            if (R[x]) todo.push_back(R[x]);
        }
        for (int k = (int)order.size() - 1; k >= 0; k--) pull(order[k]);
    }

    // O(1) -- the current length of the array
    int size() const { return sz[root]; }

''')
    pub = []
    pub.append(("insertAt", '''    // O(logN) expected -- insert v so it becomes a[i]; 0 <= i <= size() (i = size() appends)
    void insertAt(int i, T v) {
        int a, c;
        split(root, i, a, c);
        root = merge(merge(a, newNode(v)), c);
    }
'''))
    pub.append(("pushBack", '''    // O(logN) expected -- append v to the end (it becomes a[size()])
    void pushBack(T v) {
        int x = newNode(v);
        root = merge(root, x);
    }
'''))
    pub.append(("eraseAt", '''    // O(logN) expected -- remove a[i]; everything after it shifts left by one
    void eraseAt(int i) { eraseRange(i, i); }
'''))
    pub.append(("eraseRange", '''    // O(logN) expected -- remove a[l..r]; everything after it shifts left by r - l + 1
    void eraseRange(int l, int r) {
        int a, b, c;
        cut(l, r, a, b, c);
        root = merge(a, c);
    }
'''))
    pub.append(("rangeReverse", '''    // O(logN) expected -- reverse a[l..r] in place
    void rangeReverse(int l, int r) {
        int a, b, c;
        cut(l, r, a, b, c);
        applyRev(b);
        root = merge(merge(a, b), c);
    }
'''))
    pub.append(("rangeRotateLeft", '''    // O(logN) expected -- cyclic shift a[l..r] left by k (a[l + k] moves to l); any integer k, negative shifts right
    void rangeRotateLeft(int l, int r, long long k) {
        int a, b, c, len = r - l + 1;
        cut(l, r, a, b, c);
        k = ((k % len) + len) % len;
        if (k) {
            int b1, b2;
            split(b, (int)k, b1, b2);
            b = merge(b2, b1);
        }
        root = merge(merge(a, b), c);
    }
'''))
    pub.append(("rangeRotateRight", '''    // O(logN) expected -- cyclic shift a[l..r] right by k (a[r - k + 1..r] move to the front); any integer k,
    // negative shifts left
    void rangeRotateRight(int l, int r, long long k) { rangeRotateLeft(l, r, -k); }
'''))
    pub.append(("moveRange", '''    // O(logN) expected -- cut a[l..r] out, then paste it back so it starts at index i of the array without it
    // (0 <= i <= size() - (r - l + 1); i = 0 moves it to the front, the max moves it to the end)
    void moveRange(int l, int r, int i) {
        int a, b, c, x, y;
        cut(l, r, a, b, c);
        split(merge(a, c), i, x, y);
        root = merge(merge(x, b), y);
    }
'''))
    pub.append(("pointGet", '''    // O(logN) expected -- a[i]
    T pointGet(int i) { return val[find(i)]; }
'''))
    for op, expr, doc in (("pointAssign", "v", "a[i] = v"), ("pointAdd", "val[t] + v", "a[i] += v"),
                          ("pointChmax", "max(val[t], v)", "a[i] = max(a[i], v)"),
                          ("pointChmin", "min(val[t], v)", "a[i] = min(a[i], v)")):
        pub.append((op, f'''    // O(logN) expected -- {doc}
    void {op}(int i, T v) {{
''' + ("        vector<int> path;\n        int t = find(i, &path);\n" if A else "        int t = find(i);\n") + f"        val[t] = {expr};\n"
                    + ("        pull(t);\n        for (int k = (int)path.size() - 1; k >= 0; k--) pull(path[k]);\n" if A else "") + "    }\n"))
    if A:
        for op, fn, doc in (("rangeAdd", "applyAdd", "a[i] += v"), ("rangeAssign", "applyAssign", "a[i] = v")):
            pub.append((op, f'''    // O(logN) expected -- {doc} for i in [l, r]
    void {op}(int l, int r, T v) {{
        int a, b, c;
        cut(l, r, a, b, c);
        {fn}(b, v);
        root = merge(merge(a, b), c);
    }}
'''))
    for agg, op, doc, typ in (("sum", "rangeSum", "a[l] + ... + a[r]", "S"), ("min", "rangeMin", "min of a[l..r]", "T"),
                              ("max", "rangeMax", "max of a[l..r]", "T")):
        if agg in aggs:
            pub.append((op, f'''    // O(logN) expected -- {doc}
    {typ} {op}(int l, int r) {{
        int a, b, c;
        cut(l, r, a, b, c);
        {typ} res = {AGG_FIELD[agg]}[b];
        root = merge(merge(a, b), c);
        return res;
    }}
'''))
    pub.sort(key=lambda kv: ops.index(kv[0]))
    c.append("\n".join(body for _, body in pub))

    new = ["        val.push_back(v), pri.push_back(rnd()), L.push_back(0), R.push_back(0), sz.push_back(1), rev.push_back(0);"]
    if "sum" in aggs:
        new.append("        sm.push_back(S(v));")
    for f in mm:
        new.append(f"        {f}.push_back(v);")
    if A:
        new.append("        add.push_back(T(0)), asg.push_back(T(0)), hasAsg.push_back(0);")
    pull = ["        int l = L[x], r = R[x];", "        sz[x] = sz[l] + sz[r] + 1;"]
    if "sum" in aggs:
        pull.append("        sm[x] = sm[l] + S(val[x]) + sm[r];")
    for agg, fn in (("min", "min"), ("max", "max")):
        if agg in aggs:
            f = AGG_FIELD[agg]
            pull += [f"        {f}[x] = val[x];", f"        if (l) {f}[x] = {fn}({f}[x], {f}[l]);", f"        if (r) {f}[x] = {fn}({f}[x], {f}[r]);"]
    c.append('''
    // ---- internals ----

    int newNode(T v) {
''' + "\n".join(new) + '''
        return (int)val.size() - 1;
    }

    // recompute x from its children
    void pull(int x) {
''' + "\n".join(pull) + '''
    }

    void applyRev(int x) {
        if (x) swap(L[x], R[x]), rev[x] ^= 1;
    }
''')
    if A:
        add = ["        if (!x) return;", "        val[x] += v;"]
        asg = ["        if (!x) return;", "        val[x] = v;"]
        if "sum" in aggs:
            add.append("        sm[x] += S(v) * sz[x];")
            asg.append("        sm[x] = S(v) * sz[x];")
        for f in mm:
            add.append(f"        {f}[x] += v;")
            asg.append(f"        {f}[x] = v;")
        add.append("        (hasAsg[x] ? asg[x] : add[x]) += v;  // an add on a pending assign shifts the assigned value")
        asg.append("        hasAsg[x] = 1, asg[x] = v, add[x] = 0;")
        c.append('''
    void applyAdd(int x, T v) {
''' + "\n".join(add) + '''
    }

    void applyAssign(int x, T v) {
''' + "\n".join(asg) + '''
    }
''')
    push = ["        if (rev[x]) applyRev(L[x]), applyRev(R[x]), rev[x] = 0;"]
    if A:
        push += ["        if (hasAsg[x]) applyAssign(L[x], asg[x]), applyAssign(R[x], asg[x]), hasAsg[x] = 0;",
                 "        else if (add[x] != T(0)) applyAdd(L[x], add[x]), applyAdd(R[x], add[x]), add[x] = 0;"]
    c.append('''
    // hand x's pending tags to its children
    void push(int x) {
''' + "\n".join(push) + '''
    }

    // a = first k elements of t, b = the rest
    void split(int t, int k, int& a, int& b) {
        if (!t) { a = b = 0; return; }
        push(t);
        if (sz[L[t]] >= k) split(L[t], k, a, L[t]), b = t;
        else split(R[t], k - sz[L[t]] - 1, R[t], b), a = t;
        pull(t);
    }

    // a's elements, then b's
    int merge(int a, int b) {
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

    // a = a[0..l-1], b = a[l..r], c = a[r+1..] as three trees; put them back with merge(merge(a, b), c)
    void cut(int l, int r, int& a, int& b, int& c) {
        split(root, l, a, b);
        split(b, r - l + 1, b, c);
    }

    // the node holding a[i], with every tag on the way pushed; path (if given) gets the nodes above it
    int find(int i, vector<int>* path = nullptr) {
        int t = root;
        while (true) {
            push(t);
            int ls = sz[L[t]];
            if (i == ls) return t;
            if (path) path->push_back(t);
            if (i < ls) t = L[t];
            else i -= ls + 1, t = R[t];
        }
    }
};
''')
    return "".join(c)


def main():
    for k in range(4):
        for aggs in itertools.combinations(("sum", "min", "max"), k):
            ops = sorted(SEQ + POINT + ([AGG_OPS[a] for a in aggs] + ["rangeAdd", "rangeAssign"] if aggs else []))
            folder = os.path.join(DIR, "-".join(ops))
            os.makedirs(folder, exist_ok=True)
            write_template(os.path.join(folder, "template.py"), python(ops, aggs))
            write_template(os.path.join(folder, "template.cpp"), cpp(ops, aggs))
            print("wrote", os.path.basename(folder))


if __name__ == "__main__":
    main()
