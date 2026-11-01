"""Implicit treap (sequence edits: insert / erase anywhere, reverse, rotate, cut and paste), one template per set of
range aggregates it keeps.

    python3 gen_treap.py

Every variant has the sequence edits and the point ops. Everything else costs memory or time only in the variants
that ask for it, so each combination gets its own template: every subset of {rangeSum, rangeMin, rangeMax} (one array
per node each), hashes (fh / bh / pw, plus gs only when a range add / assign must move them), rangeAdd and / or
rangeAssign (their lazy tags), rangeReverse (its tag), and pointer nodes (cut / paste between treaps). A variant with
no tag at all has no push.
"""
import itertools
import os
import shutil

from note_lang import folder_name, write_template

DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "range-queries")
SEQ = ["append", "appendLeft", "eraseRange", "insertAt", "moveRange", "pop", "popLeft", "rangeRotateLeft", "rangeRotateRight"]
UPDATES = {"": [], "add": ["rangeAdd"], "assign": ["rangeAssign"], "addassign": ["rangeAdd", "rangeAssign"]}
POINT = ["pointAdd", "pointAssign", "pointChmax", "pointChmin", "pointGet"]
AGG_OPS = {"sum": "rangeSum", "min": "rangeMin", "max": "rangeMax"}
AGG_FIELD = {"sum": "sm", "min": "mn", "max": "mx"}
HASH_OPS = ["isPalindrome", "rangeHash", "rangeHashReversed", "rangesEqual"]
HASH_FIELDS = ["fh", "bh", "pw", "gs"]  # forward / backward hash, B^size, 1 + B + ... + B^(size-1)
# first / last index in [l, r] whose value passes a comparison: a walk pruned by the subtree max (Gt / Gte) or min
SEARCH = {f"{side}{cmp}X": (side, cmp) for side in ("leftmost", "rightmost") for cmp in ("Gt", "Gte", "Lt", "Lte")}
CMP_OP = {"Gt": ">", "Gte": ">=", "Lt": "<", "Lte": "<="}


def search_field(cmp):
    return "mx" if cmp.startswith("G") else "mn"


def costs_of(op):
    return "N" if op == "getAll" else "log(N) expected"


def node_and_tags(ops, aggs):
    """The per-node arrays and the tag arrays a variant keeps: each only when an op of this variant needs it."""
    AD, AS = "rangeAdd" in ops, "rangeAssign" in ops
    hashf = [f for f in HASH_FIELDS if f != "gs" or AD or AS]
    node = ["val", "sz", "L", "R", "pri"] + [AGG_FIELD[a] for a in aggs if a != "hash"] + (hashf if "hash" in aggs else [])
    tags = (["rev"] if "rangeReverse" in ops else []) + (["add"] if AD else []) + (["asg", "hasAsg"] if AS else [])
    return node, tags


def header(cm, ops, aggs):
    lines = [f"@operations: {' '.join(ops)}", "@data-structure-type: treap", "@complexities:"]
    lines += [f"  {op}: {costs_of(op)}" for op in ops] + ["  build: N", "@memory:", "  layout: none"]
    node, tags = node_and_tags(ops, aggs)
    lines += [f"  node: {' '.join(f'{f}[1*N]' for f in node)}", f"  tags: {' '.join(f'{f}[1*N]' for f in tags) or 'none'}", "  other: none",
              "  note: N = every value ever inserted (the initial array plus each insertAt; erased nodes are not reused); "
              "split / merge recurse O(log N) deep in expectation"]
    return "\n".join(f"{cm} {x}" for x in lines) + "\n"


def describe(aggs, ops=()):
    what = ", ".join(AGG_OPS[a] for a in aggs if a != "hash") + (
        (", " if len(aggs) > 1 else "") + "range hashes / isPalindrome / rangesEqual (polynomial hashes mod 2^61 - 1 "
        "both ways, the base random per run; a reverse swaps them)" if "hash" in aggs else "")
    upd = " / ".join(o for o in ("rangeAdd", "rangeAssign") if o in ops)
    extra = ", ".join(x for x in (upd, what) if x)
    return (f"Implicit treap: an array you can insert into / erase from anywhere, " + ("reverse, " if "rangeReverse" in ops else "") +
            f"rotate and cut-and-paste, each in O(logN) expected, plus point ops" + (f", {extra}" if extra else "") + ". "
            "All indices 0-based, ranges inclusive [l, r], and an index always means the position in the CURRENT array. "
            "Nodes keep their values in array order (an in-order walk); a node's position is the size of everything left "
            "of it. Lazy tags mean \"already applied to this node, not yet to its children\".")


def no_push(text, lang):
    """A variant with no tags at all (no reverse, add or assign): every push is a no-op, so take the calls out."""
    import re
    if lang == "py":
        return re.sub(r"^[ \t]*(?:self\.)?_push\(\w+\)\n", "", text, flags=re.M)
    text = re.sub(r"^[ \t]*push\(\w+\);\n", "", text, flags=re.M)
    return re.sub(r"\bpush\((\w+)\), ", "", text)


def wrap(text, cm, width=118):
    out, line = [], cm
    for word in text.split():
        if len(line) + 1 + len(word) > width:
            out.append(line)
            line = cm
        line += " " + word
    out.append(line)
    return "\n".join(out) + "\n"


# ------------------------------------------------------------------------------------------------ every treap: whole array,
# k copies at once, searches, hashes

PY_HASH_CONST = '''_HP = (1 << 61) - 1  # range hashes are mod this prime
_HB = random.randrange(1 << 40, _HP - 1)  # with a base picked at random each run (so no test can be built against it)
_HO = random.randrange(1, _HP)  # value v hashes as v + _HO: no common value hashes as 0 (a 0 in front would vanish)


'''

CPP_HASH_HELPERS = '''    // range hashes: mod the prime 2^61 - 1, with a base picked at random each run (so no test can be built against it)
    static constexpr unsigned long long HP = (1ULL << 61) - 1;
    static unsigned long long HB() {
        static unsigned long long b = (1ULL << 40) + rnd() % (HP - (1ULL << 41));
        return b;
    }
    static unsigned long long hmul(unsigned long long a, unsigned long long b) {
        __uint128_t c = (__uint128_t)a * b;
        unsigned long long r = (unsigned long long)(c & HP) + (unsigned long long)(c >> 61);
        r = (r & HP) + (r >> 61);
        return r >= HP ? r - HP : r;
    }
    static unsigned long long hadd(unsigned long long a, unsigned long long b) { return a + b >= HP ? a + b - HP : a + b; }
    static unsigned long long hraw(T v) {  // v as a residue (what an add changes a hash by, per position)
        long long r = (long long)v % (long long)HP;
        return r < 0 ? (unsigned long long)(r + (long long)HP) : (unsigned long long)r;
    }
    static unsigned long long hval(T v) {  // the hash of value v: v + an offset random per run, so no common value is 0
        static unsigned long long off = 1 + rnd() % (HP - 1);
        return hadd(hraw(v), off);
    }

'''

HASH_DOC = {
    "rangeHash": "hash of a[l..r] read left to right (a[l] B^(len-1) + ... + a[r], mod 2^61 - 1; B random per run): equal ranges hash equal",
    "rangeHashReversed": "hash of a[l..r] read right to left (= rangeHash of the reversed range)",
    "isPalindrome": "is a[l..r] a palindrome (its two hashes agree)",
    "rangesEqual": "are a[l1..r1] and a[l2..r2] equal (same length and hash)",
}
SEARCH_DOC = {"leftmost": "first", "rightmost": "last"}


def py_extra_ops(ops, aggs, H, ptr):
    """(public ops, internal text) for getAll, insertCopiesAt, the searches and the hashes, Python."""
    pub = []
    sz = (lambda t: f"({t}.sz if {t} else 0)") if ptr else (lambda t: f"sz[{t}]")
    if "getAll" in ops:
        nxt = ("t.l", "t.val", "t.r") if ptr else ("L[t]", "val[t]", "R[t]")
        pub.append(("getAll", f'''    # O(N) -- the whole current array a[0..size()-1], every pending tag applied on the way
    def getAll(self):
''' + ("" if ptr else "        L, R, val = self.L, self.R, self.val\n") + f'''        out, stack, t = [], [], self.root
        while stack or t:
            while t:
                {"_push(t)" if ptr else "self._push(t)"}
                stack.append(t)
                t = {nxt[0]}
            t = stack.pop()
            out.append({nxt[1]})
            t = {nxt[2]}
        return out
'''))
    if "insertCopiesAt" in ops:
        pub.append(("insertCopiesAt", f'''    # O(k + logN) expected -- insert k copies of v so they become a[i..i+k-1] (nothing if k <= 0): they are built as
    # one treap in O(k), then spliced in
    def insertCopiesAt(self, i, v, k):
        if k <= 0:
            return
        a, c = {"_split(self.root, i)" if ptr else "self._split(self.root, i)"}
        self.root = {"_merge(_merge(a, _build([v] * k)), c)" if ptr else "self._merge(self._merge(a, self._build([v] * k)), c)"}
'''))
    for op, (side, cmp) in SEARCH.items():
        if op not in ops:
            continue
        f, o = search_field(cmp), CMP_OP[cmp]
        F = (lambda t: f"{t}.{f}") if ptr else (lambda t: f"F[{t}]")
        kid = (lambda t, d: f"{t}.{d}") if ptr else (lambda t, d: f"{'L' if d == 'l' else 'R'}[{t}]")
        val = "t.val" if ptr else "val[t]"
        if side == "leftmost":
            walk = f'''                if {kid("t", "l")} and {F(kid("t", "l"))} {o} x:
                    t = {kid("t", "l")}
                elif {val} {o} x:
                    res = l + i + {sz(kid("t", "l"))}
                    break
                else:
                    i += {sz(kid("t", "l"))} + 1
                    t = {kid("t", "r")}'''
        else:
            walk = f'''                if {kid("t", "r")} and {F(kid("t", "r"))} {o} x:
                    i += {sz(kid("t", "l"))} + 1
                    t = {kid("t", "r")}
                elif {val} {o} x:
                    res = l + i + {sz(kid("t", "l"))}
                    break
                else:
                    t = {kid("t", "l")}'''
        pub.append((op, f'''    # O(logN) expected -- the {SEARCH_DOC[side]} i in [l, r] with a[i] {o} x, or -1: a walk down a[l..r]'s tree, pruned by the
    # subtree {"max" if f == "mx" else "min"}
    def {op}(self, l, r, x):
        a, b, c = self._cut(l, r)
''' + ("" if ptr else f"        L, R, val, sz, F = self.L, self.R, self.val, self.sz, self.{f}\n") + f'''        t, i, res = b, 0, -1
        if t and {F("t")} {o} x:  # some value in a[l..r] passes
            while True:
                {"_push(t)" if ptr else "self._push(t)"}
{walk}
        {"self.root = _merge(_merge(a, b), c)" if ptr else "self._join(a, b, c)"}
        return res
'''))
    if H:
        fld = (lambda t, f: f"{t}.{f}") if ptr else (lambda t, f: f"self.{f}[{t}]")
        join = "self.root = _merge(_merge(a, b), c)" if ptr else "self._join(a, b, c)"
        for op, f in (("rangeHash", "fh"), ("rangeHashReversed", "bh")):
            pub.append((op, f'''    # O(logN) expected -- {HASH_DOC[op]}
    def {op}(self, l, r):
        a, b, c = self._cut(l, r)
        res = {fld("b", f)}
        {join}
        return res
'''))
        pub.append(("isPalindrome", f'''    # O(logN) expected -- {HASH_DOC["isPalindrome"]}
    def isPalindrome(self, l, r):
        a, b, c = self._cut(l, r)
        res = {fld("b", "fh")} == {fld("b", "bh")}
        {join}
        return res
'''))
        pub.append(("rangesEqual", f'''    # O(logN) expected -- {HASH_DOC["rangesEqual"]}
    def rangesEqual(self, l1, r1, l2, r2):
        return r1 - l1 == r2 - l2 and self.rangeHash(l1, r1) == self.rangeHash(l2, r2)
'''))
    if ptr:
        internal = '''

def _build(vals):  # a treap of new nodes holding vals in order: a Cartesian tree in one pass, O(len)
    stack = []
    for v in vals:
        x, last = _Node(v), None
        while stack and stack[-1].pri < x.pri:
            last = stack.pop()
        x.l = last
        if stack:
            stack[-1].r = x
        stack.append(x)
    root = stack[0] if stack else None
    order, todo = [], ([root] if root else [])
    while todo:  # pre-order; pulled in reverse, so children before parents
        x = todo.pop()
        order.append(x)
        if x.l:
            todo.append(x.l)
        if x.r:
            todo.append(x.r)
    for x in reversed(order):
        _pull(x)
    return root
''' if "insertCopiesAt" in ops else ""
    else:
        internal = '''
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
        while todo:  # pre-order; pulled in reverse, so children before parents
            x = todo.pop()
            order.append(x)
            if L[x]:
                todo.append(L[x])
            if R[x]:
                todo.append(R[x])
        for x in reversed(order):
            self._pull(x)
        return root
''' if "insertCopiesAt" in ops else ""
    return pub, internal


def cpp_extra_ops(ops, aggs, H, ptr):
    """(public ops, internal text), C++."""
    pub = []
    N = "Node*" if ptr else "int"
    szf = (lambda t: f"sz({t})") if ptr else (lambda t: f"sz[{t}]")
    kid = (lambda t, d: f"{t}->{d}") if ptr else (lambda t, d: f"{'L' if d == 'l' else 'R'}[{t}]")
    val = "t->val" if ptr else "val[t]"
    cut = "Node *a, *b, *c;\n        cut3(l, r, a, b, c);" if ptr else "int a, b, c;\n        cut(l, r, a, b, c);"
    if "getAll" in ops:
        pub.append(("getAll", f'''    // O(N) -- the whole current array a[0..size()-1], every pending tag applied on the way
    vector<T> getAll() {{
        vector<T> out;
        out.reserve(size());
        vector<{N}> st;
        {N} t = root;
        while (!st.empty() || t) {{
            while (t) push(t), st.push_back(t), t = {kid("t", "l")};
            t = st.back(), st.pop_back();
            out.push_back({val});
            t = {kid("t", "r")};
        }}
        return out;
    }}
'''))
    if "insertCopiesAt" in ops:
        pub.append(("insertCopiesAt", f'''    // O(k + logN) expected -- insert k copies of v so they become a[i..i+k-1] (nothing if k <= 0): they are built as
    // one treap in O(k), then spliced in
    void insertCopiesAt(int i, T v, long long k) {{
        if (k <= 0) return;
        {"Node *a, *c;" if ptr else "int a, c;"}
        split(root, i, a, c);
        root = merge(merge(a, build(vector<T>(k, v))), c);
    }}
'''))
    for op, (side, cmp) in SEARCH.items():
        if op not in ops:
            continue
        f, o = search_field(cmp), CMP_OP[cmp]
        F = (lambda t: f"{t}->{f}") if ptr else (lambda t: f"{f}[{t}]")
        if side == "leftmost":
            walk = f'''                if ({kid("t", "l")} && {F(kid("t", "l"))} {o} x) t = {kid("t", "l")};
                else if ({val} {o} x) {{
                    res = l + i + {szf(kid("t", "l"))};
                    break;
                }} else i += {szf(kid("t", "l"))} + 1, t = {kid("t", "r")};'''
        else:
            walk = f'''                if ({kid("t", "r")} && {F(kid("t", "r"))} {o} x) i += {szf(kid("t", "l"))} + 1, t = {kid("t", "r")};
                else if ({val} {o} x) {{
                    res = l + i + {szf(kid("t", "l"))};
                    break;
                }} else t = {kid("t", "l")};'''
        pub.append((op, f'''    // O(logN) expected -- the {SEARCH_DOC[side]} i in [l, r] with a[i] {o} x, or -1: a walk down a[l..r]'s tree, pruned by the
    // subtree {"max" if f == "mx" else "min"}
    int {op}(int l, int r, T x) {{
        {cut}
        int res = -1;
        if (b && {F("b")} {o} x) {{  // some value in a[l..r] passes
            {N} t = b;
            int i = 0;
            while (true) {{
                push(t);
{walk}
            }}
        }}
        root = merge(merge(a, b), c);
        return res;
    }}
'''))
    if H:
        fld = (lambda t, f: f"{t}->{f}") if ptr else (lambda t, f: f"{f}[{t}]")
        for op, f in (("rangeHash", "fh"), ("rangeHashReversed", "bh")):
            pub.append((op, f'''    // O(logN) expected -- {HASH_DOC[op]}
    unsigned long long {op}(int l, int r) {{
        {cut}
        unsigned long long res = {fld("b", f)};
        root = merge(merge(a, b), c);
        return res;
    }}
'''))
        pub.append(("isPalindrome", f'''    // O(logN) expected -- {HASH_DOC["isPalindrome"]}
    bool isPalindrome(int l, int r) {{
        {cut}
        bool res = {fld("b", "fh")} == {fld("b", "bh")};
        root = merge(merge(a, b), c);
        return res;
    }}
'''))
        pub.append(("rangesEqual", f'''    // O(logN) expected -- {HASH_DOC["rangesEqual"]}
    bool rangesEqual(int l1, int r1, int l2, int r2) {{ return r1 - l1 == r2 - l2 && rangeHash(l1, r1) == rangeHash(l2, r2); }}
'''))
    internal = ""
    if "insertCopiesAt" in ops:
        if ptr:
            internal = '''
    // a treap of new nodes holding vals in order: a Cartesian tree in one pass, O(len)
    static Node* build(const vector<T>& vals) {
        vector<Node*> stk, order, todo;
        for (const T& v : vals) {
            Node *x = new Node(v), *last = nullptr;
            while (!stk.empty() && stk.back()->pri < x->pri) last = stk.back(), stk.pop_back();
            x->l = last;
            if (!stk.empty()) stk.back()->r = x;
            stk.push_back(x);
        }
        Node* rt = stk.empty() ? nullptr : stk[0];
        if (rt) todo.push_back(rt);
        while (!todo.empty()) {  // pre-order; pulled in reverse, so children before parents
            Node* x = todo.back();
            todo.pop_back(), order.push_back(x);
            if (x->l) todo.push_back(x->l);
            if (x->r) todo.push_back(x->r);
        }
        for (int k = (int)order.size() - 1; k >= 0; k--) pull(order[k]);
        return rt;
    }
'''
        else:
            internal = '''
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
        while (!todo.empty()) {  // pre-order; pulled in reverse, so children before parents
            int x = todo.back();
            todo.pop_back(), order.push_back(x);
            if (L[x]) todo.push_back(L[x]);
            if (R[x]) todo.push_back(R[x]);
        }
        for (int k = (int)order.size() - 1; k >= 0; k--) pull(order[k]);
        return rt;
    }
'''
    return pub, internal


# ------------------------------------------------------------------------------------------------ Python

def python(ops, aggs):
    aggs0, H = aggs, "hash" in aggs
    aggs = tuple(a for a in aggs if a != "hash")
    A = bool(aggs) or H
    RV, AD, AS = "rangeReverse" in ops, "rangeAdd" in ops, "rangeAssign" in ops  # each tag only with its ops
    G = H and (AD or AS)  # gs: only a range add / assign moves a hash by v * (1 + B + ... + B^(size-1))
    slots = ["root", "val", "pri", "L", "R", "sz"] + (["rev"] if RV else []) + [AGG_FIELD[a] for a in aggs] + (
        [f for f in HASH_FIELDS if f != "gs" or G] if H else []) + (["add"] if AD else []) + (["asg", "hasAsg"] if AS else [])
    p = [header("#", ops, aggs0), "\n", wrap(describe(aggs0, ops), "#"), "import random\n\n\n" + (PY_HASH_CONST if H else "") + "class ImplicitTreap:\n"]
    p.append(f"    __slots__ = ({', '.join(repr(s) for s in slots)})\n\n")
    init = ["        n = len(arr)", "        self.val = [0] + list(arr)  # node 0 is the empty tree",
            "        self.pri = [0] + [random.getrandbits(62) for _ in range(n)]", "        self.L = [0] * (n + 1)",
            "        self.R = [0] * (n + 1)", "        self.sz = [0] + [1] * n"] + (["        self.rev = [0] * (n + 1)"] if RV else [])
    init += [f"        self.{AGG_FIELD[a]} = [0] + list(arr)" for a in aggs]
    if H:  # (node 0, the empty tree: hashes 0, B^0 = 1; every other node is pulled below)
        init += ["        self.fh, self.bh = [0] * (n + 1), [0] * (n + 1)",
                 "        self.pw, self.gs = [1] * (n + 1), [0] * (n + 1)" if G else "        self.pw = [1] * (n + 1)"]
    if AD:
        init.append("        self.add = [0] * (n + 1)")
    if AS:
        init += ["        self.asg = [0] * (n + 1)", "        self.hasAsg = [0] * (n + 1)"]
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
    pub.append(('append', '''    # O(logN) expected -- append v to the end (it becomes a[size()])
    def append(self, v):
        self.root = self._merge(self.root, self._newNode(v))
'''))
    pub.append(('pop', '''    # O(logN) expected -- insert v at the front (it becomes a[0]; everything else shifts right by one)
    def appendLeft(self, v):
        self.insertAt(0, v)

    # O(logN) expected -- remove a[i] and return it; everything after it shifts left by one
    def pop(self, i):
        v = self.pointGet(i)
        self.eraseRange(i, i)
        return v

    # O(logN) expected -- remove a[0] and return it
    def popLeft(self):
        return self.pop(0)
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
    if AD or AS:
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
    more, internal = py_extra_ops(ops, aggs, H, ptr=False)
    pub += more
    pub = [kv for kv in pub if kv[0] in ops]
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
    if H:  # concatenation: H(X + Y) = H(X) * B^|Y| + H(Y); the backward hash reads right to left
        pull += [("        B, P, pw, gs, fh, bh = _HB, _HP, self.pw, self.gs, self.fh, self.bh" if G else
                  "        B, P, pw, fh, bh = _HB, _HP, self.pw, self.fh, self.bh"), "        hv = (self.val[x] + _HO) % P",
                 "        pw[x] = pw[l] * B % P * pw[r] % P"] + (["        gs[x] = ((gs[l] * B + 1) * pw[r] + gs[r]) % P"] if G else []) + [
                 "        fh[x] = ((fh[l] * B + hv) * pw[r] + fh[r]) % P", "        bh[x] = ((bh[r] * B + hv) * pw[l] + bh[l]) % P"]
    new = ["        x = len(self.val)", "        self.val.append(v)", "        self.pri.append(random.getrandbits(62))",
           "        self.L.append(0)", "        self.R.append(0)", "        self.sz.append(1)"] + (["        self.rev.append(0)"] if RV else [])
    new += [f"        self.{AGG_FIELD[a]}.append(v)" for a in aggs]
    if H:
        new += ["        self.fh.append((v + _HO) % _HP)", "        self.bh.append((v + _HO) % _HP)", "        self.pw.append(_HB)"] + (
            ["        self.gs.append(1)"] if G else [])
    if AD:
        new.append("        self.add.append(0)")
    if AS:
        new += ["        self.asg.append(0)", "        self.hasAsg.append(0)"]
    p.append('''
    # ---- internals ----

    def _newNode(self, v):
''' + "\n".join(new) + '''
        return x

    # recompute x from its children
    def _pull(self, x):
''' + "\n".join(pull) + "\n")
    if RV:
        p.append('''
    def _applyRev(self, x):
        if x:
            self.L[x], self.R[x] = self.R[x], self.L[x]
            self.rev[x] ^= 1
''' + ("            self.fh[x], self.bh[x] = self.bh[x], self.fh[x]  # reversed: the hashes trade places\n" if H else ""))
    if AD or AS:
        add = ["        if not x:", "            return", "        self.val[x] += v"]
        asg = ["        if not x:", "            return", "        self.val[x] = v"]
        if "sum" in aggs:
            add.append("        self.sm[x] += v * self.sz[x]")
            asg.append("        self.sm[x] = v * self.sz[x]")
        for a in aggs:
            if a != "sum":
                add.append(f"        self.{AGG_FIELD[a]}[x] += v")
                asg.append(f"        self.{AGG_FIELD[a]}[x] = v")
        if H:  # every value gains v: each hash gains v * (1 + B + ... + B^(size-1))
            add += ["        h = v % _HP * self.gs[x] % _HP", "        self.fh[x] = (self.fh[x] + h) % _HP",
                    "        self.bh[x] = (self.bh[x] + h) % _HP"]
            asg += ["        self.fh[x] = self.bh[x] = (v + _HO) % _HP * self.gs[x] % _HP"]
        if AS:
            add += ["        if self.hasAsg[x]:  # an add on a pending assign shifts the assigned value", "            self.asg[x] += v",
                    "        else:", "            self.add[x] += v"]
            asg += ["        self.hasAsg[x] = 1", "        self.asg[x] = v"] + (["        self.add[x] = 0"] if AD else [])
        else:
            add.append("        self.add[x] += v")
        p.append(('''
    def _applyAdd(self, x, v):
''' + "\n".join(add) + "\n" if AD else "") + ('''
    def _applyAssign(self, x, v):
''' + "\n".join(asg) + "\n" if AS else ""))
    push = ['''        if self.rev[x]:
            self._applyRev(self.L[x])
            self._applyRev(self.R[x])
            self.rev[x] = 0'''] if RV else []
    if AS:
        push.append('''        if self.hasAsg[x]:
            self._applyAssign(self.L[x], self.asg[x])
            self._applyAssign(self.R[x], self.asg[x])
            self.hasAsg[x] = 0''')
    if AD:
        push.append(('''        elif''' if AS else '''        if''') + ''' self.add[x]:
            self._applyAdd(self.L[x], self.add[x])
            self._applyAdd(self.R[x], self.add[x])
            self.add[x] = 0''')
    p.append(('''
    # hand x's pending tags to its children
    def _push(self, x):
''' + "\n".join(push) + "\n" if push else "") + '''
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
    out = "".join(p) + internal
    return out if RV or AD or AS else no_push(out, "py")


# ------------------------------------------------------------------------------------------------ C++

def cpp(ops, aggs):
    aggs0, H = aggs, "hash" in aggs
    aggs = tuple(a for a in aggs if a != "hash")
    A = bool(aggs) or H
    RV, AD, AS = "rangeReverse" in ops, "rangeAdd" in ops, "rangeAssign" in ops  # each tag only with its ops
    G = H and (AD or AS)  # gs: only a range add / assign moves a hash by v * (1 + B + ... + B^(size-1))
    c = [header("//", ops, aggs0), "\n", wrap(describe(aggs0, ops), "//"), "// T: int, long long, ...;" +
         (" sums are kept in S (long long for small T).\n" if "sum" in aggs else " values are stored as T.\n")]
    c.append("template <typename T>\nstruct ImplicitTreap {\n")
    if "sum" in aggs:
        c.append("    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;\n")
    fields = ["    int root = 0;", "    vector<T> val;  // node 0 is the empty tree", "    vector<unsigned long long> pri;",
              "    vector<int> L, R, sz;"] + (["    vector<char> rev;"] if RV else [])
    if "sum" in aggs:
        fields.append("    vector<S> sm;")
    mm = [AGG_FIELD[a] for a in aggs if a != "sum"]
    if mm:
        fields.append(f"    vector<T> {', '.join(mm)};")
    if H:
        fields.append("    vector<unsigned long long> fh, bh, pw, gs;  // hashes (forward, backward), B^size, 1 + B + ... + B^(size-1)" if G
                      else "    vector<unsigned long long> fh, bh, pw;  // hashes (forward, backward), B^size")
    if AD:
        fields.append("    vector<T> add;")
    if AS:
        fields += ["    vector<T> asg;", "    vector<char> hasAsg;"]
    c.append("\n".join(fields) + "\n\n")
    if H:
        c.append(CPP_HASH_HELPERS)
    c.append('''    static unsigned long long rnd() {
        static mt19937_64 g(chrono::steady_clock::now().time_since_epoch().count());
        return g();
    }

''')
    init = ["        int n = (int)arr.size();", "        val.assign(1, T(0)), val.insert(val.end(), arr.begin(), arr.end());",
            "        pri.assign(n + 1, 0), L.assign(n + 1, 0), R.assign(n + 1, 0), sz.assign(n + 1, 1)" + (", rev.assign(n + 1, 0);" if RV else ";"),
            "        sz[0] = 0;", "        for (int x = 1; x <= n; x++) pri[x] = rnd();"]
    if "sum" in aggs:
        init.append("        sm.assign(n + 1, S(0));")
    for f in mm:
        init.append(f"        {f} = val;")
    if H:
        init.append("        fh.assign(n + 1, 0), bh.assign(n + 1, 0), pw.assign(n + 1, 1)" + (", gs.assign(n + 1, 0);" if G else ";"))
    if AD:
        init.append("        add.assign(n + 1, T(0));")
    if AS:
        init.append("        asg.assign(n + 1, T(0)), hasAsg.assign(n + 1, 0);")
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
    pub.append(("append", '''    // O(logN) expected -- append v to the end (it becomes a[size()])
    void append(T v) {
        int x = newNode(v);
        root = merge(root, x);
    }
'''))
    pub.append(('pop', '''    // O(logN) expected -- insert v at the front (it becomes a[0]; everything else shifts right by one)
    void appendLeft(T v) { insertAt(0, v); }

    // O(logN) expected -- remove a[i] and return it; everything after it shifts left by one
    T pop(int i) {
        T v = pointGet(i);
        eraseRange(i, i);
        return v;
    }

    // O(logN) expected -- remove a[0] and return it
    T popLeft() { return pop(0); }
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
    if AD or AS:
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
    more, internal = cpp_extra_ops(ops, aggs, H, ptr=False)
    pub += more
    pub = [kv for kv in pub if kv[0] in ops]
    pub.sort(key=lambda kv: ops.index(kv[0]))
    c.append("\n".join(body for _, body in pub))

    new = ["        val.push_back(v), pri.push_back(rnd()), L.push_back(0), R.push_back(0), sz.push_back(1)" + (", rev.push_back(0);" if RV else ";")]
    if "sum" in aggs:
        new.append("        sm.push_back(S(v));")
    for f in mm:
        new.append(f"        {f}.push_back(v);")
    if H:
        new.append("        fh.push_back(hval(v)), bh.push_back(hval(v)), pw.push_back(HB())" + (", gs.push_back(1);" if G else ";"))
    if AD:
        new.append("        add.push_back(T(0));")
    if AS:
        new.append("        asg.push_back(T(0)), hasAsg.push_back(0);")
    pull = ["        int l = L[x], r = R[x];", "        sz[x] = sz[l] + sz[r] + 1;"]
    if "sum" in aggs:
        pull.append("        sm[x] = sm[l] + S(val[x]) + sm[r];")
    for agg, fn in (("min", "min"), ("max", "max")):
        if agg in aggs:
            f = AGG_FIELD[agg]
            pull += [f"        {f}[x] = val[x];", f"        if (l) {f}[x] = {fn}({f}[x], {f}[l]);", f"        if (r) {f}[x] = {fn}({f}[x], {f}[r]);"]
    if H:  # concatenation: H(X + Y) = H(X) * B^|Y| + H(Y); the backward hash reads right to left
        pull += ["        unsigned long long B = HB(), hv = hval(val[x]);", "        pw[x] = hmul(hmul(pw[l], B), pw[r]);"] + (
                 ["        gs[x] = hadd(hmul(hadd(hmul(gs[l], B), 1), pw[r]), gs[r]);"] if G else []) + [
                 "        fh[x] = hadd(hmul(hadd(hmul(fh[l], B), hv), pw[r]), fh[r]);",
                 "        bh[x] = hadd(hmul(hadd(hmul(bh[r], B), hv), pw[l]), bh[l]);"]
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
''')
    if RV:
        c.append('''
    void applyRev(int x) {
        if (x) swap(L[x], R[x]), rev[x] ^= 1''' + (", swap(fh[x], bh[x]);  // reversed: the hashes trade places" if H else ";") + '''
    }
''')
    if AD or AS:
        add = ["        if (!x) return;", "        val[x] += v;"]
        asg = ["        if (!x) return;", "        val[x] = v;"]
        if "sum" in aggs:
            add.append("        sm[x] += S(v) * sz[x];")
            asg.append("        sm[x] = S(v) * sz[x];")
        for f in mm:
            add.append(f"        {f}[x] += v;")
            asg.append(f"        {f}[x] = v;")
        if H:  # every value gains v: each hash gains v * (1 + B + ... + B^(size-1))
            add.append("        unsigned long long h = hmul(hraw(v), gs[x]);\n        fh[x] = hadd(fh[x], h), bh[x] = hadd(bh[x], h);")
            asg.append("        fh[x] = bh[x] = hmul(hval(v), gs[x]);")
        add.append("        (hasAsg[x] ? asg[x] : add[x]) += v;  // an add on a pending assign shifts the assigned value" if AS else
                   "        add[x] += v;")
        asg.append("        hasAsg[x] = 1, asg[x] = v" + (", add[x] = 0;" if AD else ";"))
        c.append(('''
    void applyAdd(int x, T v) {
''' + "\n".join(add) + "\n    }\n" if AD else "") + ('''
    void applyAssign(int x, T v) {
''' + "\n".join(asg) + "\n    }\n" if AS else ""))
    push = ["        if (rev[x]) applyRev(L[x]), applyRev(R[x]), rev[x] = 0;"] if RV else []
    if AS:
        push.append("        if (hasAsg[x]) applyAssign(L[x], asg[x]), applyAssign(R[x], asg[x]), hasAsg[x] = 0;")
    if AD:
        push.append(("        else " if AS else "        ") + "if (add[x] != T(0)) applyAdd(L[x], add[x]), applyAdd(R[x], add[x]), add[x] = 0;")
    c.append(('''
    // hand x's pending tags to its children
    void push(int x) {
''' + "\n".join(push) + "\n    }\n" if push else "") + '''
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
    out = "".join(c)
    out = out[:out.rindex("};")] + internal + "};\n"
    return out if RV or AD or AS else no_push(out, "cpp")


# ------------------------------------------------------------------------------------------------ cut / paste (pointer nodes)
# cut(l, r) hands a[l..r] back as a treap of its own and paste(i, other) splices a whole treap in, both O(log N): the
# nodes move between treaps, so each is allocated on its own (C++: new / delete, freed with its treap; Python: node
# objects) instead of living in one treap's arrays. Only these variants pay for that; every other treap keeps arrays.

def header_ptr(cm, ops, aggs):
    lines = [f"@operations: {' '.join(ops)}", "@data-structure-type: treap", "@complexities:"]
    lines += [f"  {op}: {costs_of(op)}" for op in ops] + ["  build: N", "@memory:", "  layout: none"]
    node, tags = node_and_tags(ops, aggs)
    lines += [f"  node: {' '.join(f'{f}[1*N]' for f in node)}", f"  tags: {' '.join(f'{f}[1*N]' for f in tags) or 'none'}", "  other: alloc[2*N]",
              "  note: N = the values in this treap; every node is allocated on its own (alloc: the allocator's per-node "
              "overhead), so cut / paste move nodes between treaps in O(log N) and erased nodes are freed; C++: a treap "
              "frees its nodes when it goes out of scope (move-only); Python: node objects"]
    return "\n".join(f"{cm} {x}" for x in lines) + "\n"


def describe_ptr(aggs, ops=()):
    return describe(aggs, ops).replace("rotate and cut-and-paste,", "rotate, move ranges, and cut out into a treap of its own / "
                                       "paste a treap into,")


PTR_FIELDS = {"sum": "sm", "min": "mn", "max": "mx"}


def python_ptr(ops, aggs):
    aggs0, H = aggs, "hash" in aggs
    aggs = tuple(a for a in aggs if a != "hash")
    A = bool(aggs) or H
    RV, AD, AS = "rangeReverse" in ops, "rangeAdd" in ops, "rangeAssign" in ops  # each tag only with its ops
    G = H and (AD or AS)  # gs: only a range add / assign moves a hash by v * (1 + B + ... + B^(size-1))
    slots = ["val", "pri", "l", "r", "sz"] + (["rev"] if RV else []) + [AGG_FIELD[a] for a in aggs] + (
        [f for f in HASH_FIELDS if f != "gs" or G] if H else []) + (["add"] if AD else []) + (["asg", "hasAsg"] if AS else [])
    p = [header_ptr("#", ops, aggs0), "\n", wrap(describe_ptr(aggs0, ops), "#"), "import random\n\n\n" + (PY_HASH_CONST if H else "")]
    p.append("class _Node:\n    __slots__ = (" + ", ".join(repr(x) for x in slots) + ")\n\n    def __init__(self, v):\n"
             "        self.val = v\n        self.pri = random.getrandbits(62)\n        self.l = self.r = None\n        self.sz = 1\n" +
             ("        self.rev = False\n" if RV else "") + "".join(f"        self.{AGG_FIELD[a]} = v\n" for a in aggs) +
             ("        self.fh = self.bh = (v + _HO) % _HP\n" + ("        self.pw, self.gs = _HB, 1\n" if G else "        self.pw = _HB\n") if H else "") +
             ("        self.add = 0\n" if AD else "") + ("        self.asg = 0\n        self.hasAsg = False\n" if AS else "") + "\n\n")
    pull = ["    l, r = x.l, x.r", "    x.sz = 1 + (l.sz if l else 0) + (r.sz if r else 0)"]
    if "sum" in aggs:
        pull.append("    x.sm = x.val + (l.sm if l else 0) + (r.sm if r else 0)")
    for agg, cmp in (("min", "<"), ("max", ">")):
        if agg in aggs:
            f = AGG_FIELD[agg]
            pull += [f"    m = x.val", f"    if l and l.{f} {cmp} m:", f"        m = l.{f}", f"    if r and r.{f} {cmp} m:",
                     f"        m = r.{f}", f"    x.{f} = m"]
    if H:  # concatenation: H(X + Y) = H(X) * B^|Y| + H(Y); the backward hash reads right to left
        if G:
            pull += ["    B, P = _HB, _HP", "    lp, lg, lf, lb = (l.pw, l.gs, l.fh, l.bh) if l else (1, 0, 0, 0)",
                     "    rp, rg, rf, rb = (r.pw, r.gs, r.fh, r.bh) if r else (1, 0, 0, 0)", "    hv = (x.val + _HO) % P",
                     "    x.pw = lp * B % P * rp % P", "    x.gs = ((lg * B + 1) * rp + rg) % P"]
        else:
            pull += ["    B, P = _HB, _HP", "    lp, lf, lb = (l.pw, l.fh, l.bh) if l else (1, 0, 0)",
                     "    rp, rf, rb = (r.pw, r.fh, r.bh) if r else (1, 0, 0)", "    hv = (x.val + _HO) % P", "    x.pw = lp * B % P * rp % P"]
        pull += ["    x.fh = ((lf * B + hv) * rp + rf) % P", "    x.bh = ((rb * B + hv) * lp + lb) % P"]
    p.append("def _pull(x):  # recompute x from its children\n" + "\n".join(pull) + "\n\n\n")
    if RV:
        p.append('''def _applyRev(x):
    if x:
        x.l, x.r = x.r, x.l
        x.rev = not x.rev
''' + ("        x.fh, x.bh = x.bh, x.fh  # reversed: the hashes trade places\n" if H else "") + "\n\n")
    if AD or AS:
        add = ["    if not x:", "        return", "    x.val += v"] + (["    x.sm += v * x.sz"] if "sum" in aggs else []) + [
            f"    x.{AGG_FIELD[a]} += v" for a in aggs if a != "sum"] + (
            ["    h = v % _HP * x.gs % _HP", "    x.fh = (x.fh + h) % _HP", "    x.bh = (x.bh + h) % _HP"] if H else []) + (
            ["    if x.hasAsg:  # an add on a pending assign shifts the assigned value", "        x.asg += v", "    else:", "        x.add += v"]
            if AS else ["    x.add += v"])
        asg = ["    if not x:", "        return", "    x.val = v"] + (["    x.sm = v * x.sz"] if "sum" in aggs else []) + [
            f"    x.{AGG_FIELD[a]} = v" for a in aggs if a != "sum"] + (["    x.fh = x.bh = (v + _HO) % _HP * x.gs % _HP"] if H else []) + [
            "    x.hasAsg = True", "    x.asg = v"] + (["    x.add = 0"] if AD else [])
        p.append(("def _applyAdd(x, v):\n" + "\n".join(add) + "\n\n\n" if AD else "") +
                 ("def _applyAssign(x, v):\n" + "\n".join(asg) + "\n\n\n" if AS else ""))
    push = ["    if x.rev:", "        _applyRev(x.l)", "        _applyRev(x.r)", "        x.rev = False"] if RV else []
    if AS:
        push += ["    if x.hasAsg:", "        _applyAssign(x.l, x.asg)", "        _applyAssign(x.r, x.asg)", "        x.hasAsg = False"]
    if AD:
        push += ["    elif x.add:" if AS else "    if x.add:", "        _applyAdd(x.l, x.add)", "        _applyAdd(x.r, x.add)", "        x.add = 0"]
    if push:
        p.append("def _push(x):  # hand x's pending tags to its children\n" + "\n".join(push) + "\n\n\n")
    p.append('''def _split(t, k):  # (first k elements of t, the rest)
    if not t:
        return None, None
    _push(t)
    ls = t.l.sz if t.l else 0
    if ls >= k:
        a, t.l = _split(t.l, k)
        _pull(t)
        return a, t
    t.r, b = _split(t.r, k - ls - 1)
    _pull(t)
    return t, b


def _merge(a, b):  # a's elements, then b's
    if not a or not b:
        return a or b
    if a.pri > b.pri:
        _push(a)
        a.r = _merge(a.r, b)
        _pull(a)
        return a
    _push(b)
    b.l = _merge(a, b.l)
    _pull(b)
    return b


class ImplicitTreap:
    __slots__ = ("root",)

    # O(N) -- arr: the initial array (may be empty)
    def __init__(self, arr=()):
        stack = []  # Cartesian tree on (position, priority) in one pass: the stack is the current right spine
        for v in arr:
            x, last = _Node(v), None
            while stack and stack[-1].pri < x.pri:
                last = stack.pop()
            x.l = last
            if stack:
                stack[-1].r = x
            stack.append(x)
        self.root = stack[0] if stack else None
        order, todo = [], ([self.root] if self.root else [])
        while todo:  # pre-order; pulled in reverse, so children before parents
            x = todo.pop()
            order.append(x)
            if x.l:
                todo.append(x.l)
            if x.r:
                todo.append(x.r)
        for x in reversed(order):
            _pull(x)

    # O(1) -- the current length of the array
    def size(self):
        return self.root.sz if self.root else 0

''')
    pub = []
    pub.append(("cut", '''    # O(logN) expected -- remove a[l..r] and return it as a treap of its own (indices from 0 again); everything after
    # it shifts left by r - l + 1
    def cut(self, l, r):
        a, b, c = self._cut(l, r)
        self.root = _merge(a, c)
        piece = ImplicitTreap()
        piece.root = b
        return piece
'''))
    pub.append(("paste", '''    # O(logN) expected -- insert all of other so it starts at a[i] (0 <= i <= size(); i = size() appends); other is
    # left empty
    def paste(self, i, other):
        a, c = _split(self.root, i)
        self.root = _merge(_merge(a, other.root), c)
        other.root = None
'''))
    pub.append(("concat", '''    # O(logN) expected -- append all of other at the end; other is left empty
    def concat(self, other):
        self.root = _merge(self.root, other.root)
        other.root = None
'''))
    pub.append(("split", '''    # O(logN) expected -- (a[0..k-1], a[k..]) as two treaps of their own (0 <= k <= size()); this one is left empty
    def split(self, k):
        left, right = ImplicitTreap(), ImplicitTreap()
        left.root, right.root = _split(self.root, k)
        self.root = None
        return left, right
'''))
    pub.append(("trisect", '''    # O(logN) expected -- (a[0..l-1], a[l..r], a[r+1..]) as three treaps of their own; this one is left empty
    def trisect(self, l, r):
        left, mid, right = ImplicitTreap(), ImplicitTreap(), ImplicitTreap()
        left.root, mid.root, right.root = self._cut(l, r)
        self.root = None
        return left, mid, right
'''))
    pub.append(("insertAt", '''    # O(logN) expected -- insert v so it becomes a[i]; 0 <= i <= size() (i = size() appends)
    def insertAt(self, i, v):
        a, c = _split(self.root, i)
        self.root = _merge(_merge(a, _Node(v)), c)
'''))
    pub.append(("append", '''    # O(logN) expected -- append v to the end (it becomes a[size()])
    def append(self, v):
        self.root = _merge(self.root, _Node(v))
'''))
    pub.append(('pop', '''    # O(logN) expected -- insert v at the front (it becomes a[0]; everything else shifts right by one)
    def appendLeft(self, v):
        self.insertAt(0, v)

    # O(logN) expected -- remove a[i] and return it; everything after it shifts left by one
    def pop(self, i):
        v = self.pointGet(i)
        self.eraseRange(i, i)
        return v

    # O(logN) expected -- remove a[0] and return it
    def popLeft(self):
        return self.pop(0)
'''))
    pub.append(("eraseRange", '''    # O(logN) expected -- remove a[l..r]; everything after it shifts left by r - l + 1
    def eraseRange(self, l, r):
        a, _, c = self._cut(l, r)
        self.root = _merge(a, c)
'''))
    pub.append(("rangeReverse", '''    # O(logN) expected -- reverse a[l..r] in place
    def rangeReverse(self, l, r):
        a, b, c = self._cut(l, r)
        _applyRev(b)
        self.root = _merge(_merge(a, b), c)
'''))
    pub.append(("rangeRotateLeft", '''    # O(logN) expected -- cyclic shift a[l..r] left by k (a[l + k] moves to l); any integer k, negative shifts right
    def rangeRotateLeft(self, l, r, k):
        a, b, c = self._cut(l, r)
        k %= r - l + 1
        if k:
            b1, b2 = _split(b, k)
            b = _merge(b2, b1)
        self.root = _merge(_merge(a, b), c)
'''))
    pub.append(("rangeRotateRight", '''    # O(logN) expected -- cyclic shift a[l..r] right by k (a[r - k + 1..r] move to the front); any integer k,
    # negative shifts left
    def rangeRotateRight(self, l, r, k):
        self.rangeRotateLeft(l, r, -k)
'''))
    pub.append(("moveRange", '''    # O(logN) expected -- cut a[l..r] out, then paste it back so it starts at index i of the array without it
    # (0 <= i <= size() - (r - l + 1); i = 0 moves it to the front, the max moves it to the end)
    def moveRange(self, l, r, i):
        a, b, c = self._cut(l, r)
        x, y = _split(_merge(a, c), i)
        self.root = _merge(_merge(x, b), y)
'''))
    pub.append(("pointGet", '''    # O(logN) expected -- a[i]
    def pointGet(self, i):
        return self._find(i)[0].val
'''))
    for op, expr, doc in (("pointAssign", "v", "a[i] = v"), ("pointAdd", "t.val + v", "a[i] += v"),
                          ("pointChmax", "max(t.val, v)", "a[i] = max(a[i], v)"), ("pointChmin", "min(t.val, v)", "a[i] = min(a[i], v)")):
        pub.append((op, f'''    # O(logN) expected -- {doc}
    def {op}(self, i, v):
        t, path = self._find(i)
        t.val = {expr}
''' + ("        _pull(t)\n        for x in reversed(path):\n            _pull(x)\n" if A else "")))
    if AD or AS:
        for op, fn, doc in (("rangeAdd", "_applyAdd", "a[i] += v"), ("rangeAssign", "_applyAssign", "a[i] = v")):
            pub.append((op, f'''    # O(logN) expected -- {doc} for i in [l, r]
    def {op}(self, l, r, v):
        a, b, c = self._cut(l, r)
        {fn}(b, v)
        self.root = _merge(_merge(a, b), c)
'''))
    for agg, op, doc in (("sum", "rangeSum", "a[l] + ... + a[r]"), ("min", "rangeMin", "min of a[l..r]"), ("max", "rangeMax", "max of a[l..r]")):
        if agg in aggs:
            pub.append((op, f'''    # O(logN) expected -- {doc}
    def {op}(self, l, r):
        a, b, c = self._cut(l, r)
        res = b.{AGG_FIELD[agg]}
        self.root = _merge(_merge(a, b), c)
        return res
'''))
    more, internal = py_extra_ops(ops, aggs, H, ptr=True)
    pub += more
    pub = [kv for kv in pub if kv[0] in ops]
    pub.sort(key=lambda kv: ops.index(kv[0]))
    p.append("\n".join(body for _, body in pub))
    p.append('''
    # ---- internals ----

    # (a[0..l-1], a[l..r], a[r+1..]) as three trees
    def _cut(self, l, r):
        a, b = _split(self.root, l)
        b, c = _split(b, r - l + 1)
        return a, b, c

    # (node holding a[i], the nodes above it), with every tag on the way pushed
    def _find(self, i):
        t, path = self.root, []
        while True:
            _push(t)
            ls = t.l.sz if t.l else 0
            if i == ls:
                return t, path
            path.append(t)
            if i < ls:
                t = t.l
            else:
                i -= ls + 1
                t = t.r
''')
    out = "".join(p) + internal
    return out if RV or AD or AS else no_push(out, "py")


def cpp_ptr(ops, aggs):
    aggs0, H = aggs, "hash" in aggs
    aggs = tuple(a for a in aggs if a != "hash")
    A = bool(aggs) or H
    RV, AD, AS = "rangeReverse" in ops, "rangeAdd" in ops, "rangeAssign" in ops  # each tag only with its ops
    G = H and (AD or AS)  # gs: only a range add / assign moves a hash by v * (1 + B + ... + B^(size-1))
    mm = [AGG_FIELD[a] for a in aggs if a != "sum"]
    c = [header_ptr("//", ops, aggs0), "\n", wrap(describe_ptr(aggs0, ops), "//"), "// T: int, long long, ...;" +
         (" sums are kept in S (long long for small T).\n" if "sum" in aggs else " values are stored as T.\n")]
    c.append("template <typename T>\nstruct ImplicitTreap {\n")
    if "sum" in aggs:
        c.append("    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;\n")
    node = ["T val;", "unsigned long long pri;", "Node *l = nullptr, *r = nullptr;", "int sz = 1;"] + (["bool rev = false;"] if RV else [])
    if "sum" in aggs:
        node.append("S sm;")
    if mm:
        node.append(f"T {', '.join(mm)};")
    if AD:
        node.append("T add{};")
    if AS:
        node += ["T asg{};", "bool hasAsg = false;"]
    if H:
        node.append("unsigned long long fh, bh, pw, gs;  // hashes (forward, backward), B^size, 1 + B + ... + B^(size-1)" if G
                    else "unsigned long long fh, bh, pw;  // hashes (forward, backward), B^size")
    init = ["val(v)", "pri(rnd())"] + (["sm(v)"] if "sum" in aggs else []) + [f"{f}(v)" for f in mm] + (
        ["fh(hval(v))", "bh(hval(v))", "pw(HB())"] + (["gs(1)"] if G else []) if H else [])
    c.append("    struct Node {\n" + "".join(f"        {x}\n" for x in node) + f"        explicit Node(T v) : {', '.join(init)} {{}}\n    }};\n")
    if H:
        c.append(CPP_HASH_HELPERS)
    c.append('''    Node* root = nullptr;

    static unsigned long long rnd() {
        static mt19937_64 g(chrono::steady_clock::now().time_since_epoch().count());
        return g();
    }

    // O(1) -- an empty array
    ImplicitTreap() {}

    // O(N) -- arr: the initial array (may be empty)
    explicit ImplicitTreap(const vector<T>& arr) {
        vector<Node*> stk;  // Cartesian tree on (position, priority) in one pass: the stack is the current right spine
        for (const T& v : arr) {
            Node *x = new Node(v), *last = nullptr;
            while (!stk.empty() && stk.back()->pri < x->pri) last = stk.back(), stk.pop_back();
            x->l = last;
            if (!stk.empty()) stk.back()->r = x;
            stk.push_back(x);
        }
        root = stk.empty() ? nullptr : stk[0];
        vector<Node*> order, todo;
        if (root) todo.push_back(root);
        while (!todo.empty()) {  // pre-order; pulled in reverse, so children before parents
            Node* x = todo.back();
            todo.pop_back(), order.push_back(x);
            if (x->l) todo.push_back(x->l);
            if (x->r) todo.push_back(x->r);
        }
        for (int k = (int)order.size() - 1; k >= 0; k--) pull(order[k]);
    }

    // a treap owns its nodes: it can be moved (cut returns one), not copied
    ImplicitTreap(ImplicitTreap&& o) noexcept : root(o.root) { o.root = nullptr; }
    ImplicitTreap& operator=(ImplicitTreap&& o) noexcept {
        if (this != &o) destroy(root), root = o.root, o.root = nullptr;
        return *this;
    }
    ImplicitTreap(const ImplicitTreap&) = delete;
    ImplicitTreap& operator=(const ImplicitTreap&) = delete;
    ~ImplicitTreap() { destroy(root); }

    // O(1) -- the current length of the array
    int size() const { return sz(root); }

''')
    pub = []
    pub.append(("cut", '''    // O(logN) expected -- remove a[l..r] and return it as a treap of its own (indices from 0 again); everything after
    // it shifts left by r - l + 1
    ImplicitTreap cut(int l, int r) {
        Node *a, *b, *c;
        cut3(l, r, a, b, c);
        root = merge(a, c);
        ImplicitTreap piece;
        piece.root = b;
        return piece;
    }
'''))
    pub.append(("paste", '''    // O(logN) expected -- insert all of other so it starts at a[i] (0 <= i <= size(); i = size() appends); other is
    // left empty
    void paste(int i, ImplicitTreap& other) {
        Node *a, *c;
        split(root, i, a, c);
        root = merge(merge(a, other.root), c);
        other.root = nullptr;
    }
'''))
    pub.append(("concat", '''    // O(logN) expected -- append all of other at the end; other is left empty
    void concat(ImplicitTreap& other) {
        root = merge(root, other.root);
        other.root = nullptr;
    }
'''))
    pub.append(("split", '''    // O(logN) expected -- (a[0..k-1], a[k..]) as two treaps of their own (0 <= k <= size()); this one is left empty
    pair<ImplicitTreap, ImplicitTreap> split(int k) {
        pair<ImplicitTreap, ImplicitTreap> res;
        split(root, k, res.first.root, res.second.root);
        root = nullptr;
        return res;
    }
'''))
    pub.append(("trisect", '''    // O(logN) expected -- (a[0..l-1], a[l..r], a[r+1..]) as three treaps of their own; this one is left empty
    tuple<ImplicitTreap, ImplicitTreap, ImplicitTreap> trisect(int l, int r) {
        tuple<ImplicitTreap, ImplicitTreap, ImplicitTreap> res;
        cut3(l, r, get<0>(res).root, get<1>(res).root, get<2>(res).root);
        root = nullptr;
        return res;
    }
'''))
    pub.append(("insertAt", '''    // O(logN) expected -- insert v so it becomes a[i]; 0 <= i <= size() (i = size() appends)
    void insertAt(int i, T v) {
        Node *a, *c;
        split(root, i, a, c);
        root = merge(merge(a, new Node(v)), c);
    }
'''))
    pub.append(("append", '''    // O(logN) expected -- append v to the end (it becomes a[size()])
    void append(T v) { root = merge(root, new Node(v)); }
'''))
    pub.append(('pop', '''    // O(logN) expected -- insert v at the front (it becomes a[0]; everything else shifts right by one)
    void appendLeft(T v) { insertAt(0, v); }

    // O(logN) expected -- remove a[i] and return it; everything after it shifts left by one
    T pop(int i) {
        T v = pointGet(i);
        eraseRange(i, i);
        return v;
    }

    // O(logN) expected -- remove a[0] and return it
    T popLeft() { return pop(0); }
'''))
    pub.append(("eraseRange", '''    // O(logN) expected -- remove a[l..r] (its nodes are freed: O(r - l + 1) more); everything after it shifts left
    // by r - l + 1
    void eraseRange(int l, int r) {
        Node *a, *b, *c;
        cut3(l, r, a, b, c);
        destroy(b);
        root = merge(a, c);
    }
'''))
    pub.append(("rangeReverse", '''    // O(logN) expected -- reverse a[l..r] in place
    void rangeReverse(int l, int r) {
        Node *a, *b, *c;
        cut3(l, r, a, b, c);
        applyRev(b);
        root = merge(merge(a, b), c);
    }
'''))
    pub.append(("rangeRotateLeft", '''    // O(logN) expected -- cyclic shift a[l..r] left by k (a[l + k] moves to l); any integer k, negative shifts right
    void rangeRotateLeft(int l, int r, long long k) {
        Node *a, *b, *c;
        int len = r - l + 1;
        cut3(l, r, a, b, c);
        k = ((k % len) + len) % len;
        if (k) {
            Node *b1, *b2;
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
        Node *a, *b, *c, *x, *y;
        cut3(l, r, a, b, c);
        split(merge(a, c), i, x, y);
        root = merge(merge(x, b), y);
    }
'''))
    pub.append(("pointGet", '''    // O(logN) expected -- a[i]
    T pointGet(int i) { return find(i)->val; }
'''))
    for op, expr, doc in (("pointAssign", "v", "a[i] = v"), ("pointAdd", "t->val + v", "a[i] += v"),
                          ("pointChmax", "max(t->val, v)", "a[i] = max(a[i], v)"), ("pointChmin", "min(t->val, v)", "a[i] = min(a[i], v)")):
        pub.append((op, f'''    // O(logN) expected -- {doc}
    void {op}(int i, T v) {{
''' + ("        vector<Node*> path;\n        Node* t = find(i, &path);\n" if A else "        Node* t = find(i);\n") + f"        t->val = {expr};\n"
                    + ("        pull(t);\n        for (int k = (int)path.size() - 1; k >= 0; k--) pull(path[k]);\n" if A else "") + "    }\n"))
    if AD or AS:
        for op, fn, doc in (("rangeAdd", "applyAdd", "a[i] += v"), ("rangeAssign", "applyAssign", "a[i] = v")):
            pub.append((op, f'''    // O(logN) expected -- {doc} for i in [l, r]
    void {op}(int l, int r, T v) {{
        Node *a, *b, *c;
        cut3(l, r, a, b, c);
        {fn}(b, v);
        root = merge(merge(a, b), c);
    }}
'''))
    for agg, op, doc, typ in (("sum", "rangeSum", "a[l] + ... + a[r]", "S"), ("min", "rangeMin", "min of a[l..r]", "T"),
                              ("max", "rangeMax", "max of a[l..r]", "T")):
        if agg in aggs:
            pub.append((op, f'''    // O(logN) expected -- {doc}
    {typ} {op}(int l, int r) {{
        Node *a, *b, *c;
        cut3(l, r, a, b, c);
        {typ} res = b->{AGG_FIELD[agg]};
        root = merge(merge(a, b), c);
        return res;
    }}
'''))
    more, internal = cpp_extra_ops(ops, aggs, H, ptr=True)
    pub += more
    pub = [kv for kv in pub if kv[0] in ops]
    pub.sort(key=lambda kv: ops.index(kv[0]))
    c.append("\n".join(body for _, body in pub))
    pull = ["        Node *l = x->l, *r = x->r;", "        x->sz = 1 + sz(l) + sz(r);"]
    if "sum" in aggs:
        pull.append("        x->sm = S(x->val) + (l ? l->sm : S(0)) + (r ? r->sm : S(0));")
    for agg, fn in (("min", "min"), ("max", "max")):
        if agg in aggs:
            f = AGG_FIELD[agg]
            pull += [f"        x->{f} = x->val;", f"        if (l) x->{f} = {fn}(x->{f}, l->{f});", f"        if (r) x->{f} = {fn}(x->{f}, r->{f});"]
    if H:  # concatenation: H(X + Y) = H(X) * B^|Y| + H(Y); the backward hash reads right to left
        pull += ["        unsigned long long B = HB(), hv = hval(x->val), lp = l ? l->pw : 1, rp = r ? r->pw : 1;",
                 "        x->pw = hmul(hmul(lp, B), rp);"] + (["        x->gs = hadd(hmul(hadd(hmul(l ? l->gs : 0, B), 1), rp), r ? r->gs : 0);"] if G else []) + [
                 "        x->fh = hadd(hmul(hadd(hmul(l ? l->fh : 0, B), hv), rp), r ? r->fh : 0);",
                 "        x->bh = hadd(hmul(hadd(hmul(r ? r->bh : 0, B), hv), lp), l ? l->bh : 0);"]
    c.append('''
    // ---- internals ----

    static int sz(Node* x) { return x ? x->sz : 0; }

    static void destroy(Node* x) {  // free a whole subtree (iteratively: a long one would overflow the stack)
        vector<Node*> st;
        if (x) st.push_back(x);
        while (!st.empty()) {
            Node* y = st.back();
            st.pop_back();
            if (y->l) st.push_back(y->l);
            if (y->r) st.push_back(y->r);
            delete y;
        }
    }

    // recompute x from its children
    static void pull(Node* x) {
''' + "\n".join(pull) + '''
    }
''')
    if RV:
        c.append('''
    static void applyRev(Node* x) {
        if (x) swap(x->l, x->r), x->rev = !x->rev''' + (", swap(x->fh, x->bh);  // reversed: the hashes trade places" if H else ";") + '''
    }
''')
    if AD or AS:
        add = ["        if (!x) return;", "        x->val += v;"] + (["        x->sm += S(v) * x->sz;"] if "sum" in aggs else []) + [
            f"        x->{f} += v;" for f in mm] + (
            ["        unsigned long long h = hmul(hraw(v), x->gs);", "        x->fh = hadd(x->fh, h), x->bh = hadd(x->bh, h);"] if H else []) + [
            "        (x->hasAsg ? x->asg : x->add) += v;  // an add on a pending assign shifts the assigned value" if AS else "        x->add += v;"]
        asg = ["        if (!x) return;", "        x->val = v;"] + (["        x->sm = S(v) * x->sz;"] if "sum" in aggs else []) + [
            f"        x->{f} = v;" for f in mm] + (["        x->fh = x->bh = hmul(hval(v), x->gs);"] if H else []) + [
            "        x->hasAsg = true, x->asg = v" + (", x->add = T(0);" if AD else ";")]
        c.append(("\n    static void applyAdd(Node* x, T v) {\n" + "\n".join(add) + "\n    }\n" if AD else "") +
                 ("\n    static void applyAssign(Node* x, T v) {\n" + "\n".join(asg) + "\n    }\n" if AS else ""))
    push = ["        if (x->rev) applyRev(x->l), applyRev(x->r), x->rev = false;"] if RV else []
    if AS:
        push.append("        if (x->hasAsg) applyAssign(x->l, x->asg), applyAssign(x->r, x->asg), x->hasAsg = false;")
    if AD:
        push.append(("        else " if AS else "        ") + "if (x->add != T(0)) applyAdd(x->l, x->add), applyAdd(x->r, x->add), x->add = T(0);")
    c.append(('''
    // hand x's pending tags to its children
    static void push(Node* x) {
''' + "\n".join(push) + "\n    }\n" if push else "") + '''
    // a = first k elements of t, b = the rest
    static void split(Node* t, int k, Node*& a, Node*& b) {
        if (!t) { a = b = nullptr; return; }
        push(t);
        if (sz(t->l) >= k) split(t->l, k, a, t->l), b = t;
        else split(t->r, k - sz(t->l) - 1, t->r, b), a = t;
        pull(t);
    }

    // a's elements, then b's
    static Node* merge(Node* a, Node* b) {
        if (!a || !b) return a ? a : b;
        if (a->pri > b->pri) {
            push(a);
            a->r = merge(a->r, b);
            pull(a);
            return a;
        }
        push(b);
        b->l = merge(a, b->l);
        pull(b);
        return b;
    }

    // a = a[0..l-1], b = a[l..r], c = a[r+1..] as three trees; put them back with merge(merge(a, b), c)
    void cut3(int l, int r, Node*& a, Node*& b, Node*& c) {
        split(root, l, a, b);
        split(b, r - l + 1, b, c);
    }

    // the node holding a[i], with every tag on the way pushed; path (if given) gets the nodes above it
    Node* find(int i, vector<Node*>* path = nullptr) {
        Node* t = root;
        while (true) {
            push(t);
            int ls = sz(t->l);
            if (i == ls) return t;
            if (path) path->push_back(t);
            if (i < ls) t = t->l;
            else i -= ls + 1, t = t->r;
        }
    }
};
''')
    out = "".join(c)
    out = out[:out.rindex("};")] + internal + "};\n"
    return out if RV or AD or AS else no_push(out, "cpp")


def folder_for(ops, vals, H, upd, rev, ptr):
    """Named by the op list (the site's rule) unless it's too long for a folder name: then by structure."""
    name = folder_name(ops)
    if len(name) <= 180:
        return name
    return ("treap" + "".join("-" + v for v in vals) + ("-hash" if H else "") + (f"-{upd}" if upd else "") + ("-rev" if rev else "") +
            ("-pointers" if ptr else ""))


def main():
    """Superseded: gen_treap_algebra.py writes every one of these treaps (and their mixes with more aggregates). Kept for
    the shared helpers above (wrap, no_push, the hash text) and as the reference for the pointer-node layout."""
    raise SystemExit("gen_treap.py's treaps are written by gen_treap_algebra.py now; run that instead")


def _old_main():
    for d in os.listdir(DIR):  # this generator's treap folders are regenerated (names follow the op lists)
        t = os.path.join(DIR, d, "template.py")
        if os.path.exists(t):
            text = open(t).read()
            if "@data-structure-type: treap" in text and "plus point ops" in text:  # (gen_treap_more's treaps say otherwise)
                shutil.rmtree(os.path.join(DIR, d))
    count = 0
    for k in range(4):
        # every treap has getAll, insertCopiesAt and the searches its min / max allow; aggregates, hashes, range add /
        # assign (their tags) and reverse (its tag) are each kept only in the variants that ask for them
        for vals, H, upd, rev in itertools.product(itertools.combinations(("sum", "min", "max"), k), (False, True), UPDATES, (False, True)):
            aggs = vals + (("hash",) if H else ())
            ops = sorted(SEQ + POINT + ["getAll", "insertCopiesAt"] + [AGG_OPS[a] for a in vals] + UPDATES[upd] +
                         (["rangeReverse"] if rev else []) +
                         [op for op, (_, cmp) in SEARCH.items() if {"mx": "max", "mn": "min"}[search_field(cmp)] in vals] +
                         (HASH_OPS if H else []))
            for ptr in (False, True):  # pointer nodes: the same, plus cut / paste / split / trisect / concat between treaps
                count += 1
                o = sorted(ops + ["concat", "cut", "paste", "split", "trisect"]) if ptr else ops
                folder = os.path.join(DIR, folder_for(o, vals, H, upd, rev, ptr))
                os.makedirs(folder, exist_ok=True)
                write_template(os.path.join(folder, "template.py"), (python_ptr if ptr else python)(o, aggs))
                write_template(os.path.join(folder, "template.cpp"), (cpp_ptr if ptr else cpp)(o, aggs))
    print("wrote", count, "treaps")


if __name__ == "__main__":
    main()
