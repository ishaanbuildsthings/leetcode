"""copy(l, r) (a[l..r] as a treap of its own in O(log N), sharing nodes; the original is unchanged) with the composable
aggregates and updates of gen_treap_algebra.py.

    python3 gen_persistent_algebra.py

A persistent implicit treap: no node changes after another tree can see it. split and merge clone every node they
touch before changing it, and a push clones the children it hands tags to, so a copy (which shares every node) and its
original never affect each other. (A push on a node in place, on the read-only walks, is harmless: the node's own
values already count its tags, and its new children hold the same values as the old ones.) With nodes shared, fixed
random priorities would no longer be independent, so merge picks its root at random weighted by size: O(log N)
expected depth, N the length. Lengths and indices are long long (copies pasted into themselves double). Queries cut
the range out and read it without putting anything back: the root doesn't change.

Every algebra treap's aggregate / update set except the range mod / floor div / floor sqrt ones (their amortized bound
counts each value's drops, and copies would reset it) and find (copies repeat values).
"""
import os
import re
import shutil

import gen_treap_algebra as A
from gen_treap import CPP_HASH_HELPERS, PY_HASH_CONST, no_push, wrap
from gen_treap_algebra import (SEARCH, SHRINK_COST, Spec, cpp_internals, cpp_public, gcd_costs, py_internals,
                               py_public)
from aos import aosify
from note_lang import folder_name, write_template

DIR = A.DIR
DTYPE = "persistent-treap"
CLS = "PersistentTreap"
MARK = "Persistent implicit treap"
QUERY_OPS = {"rangeSum", "rangeMin", "rangeMax", "maxPrefixSum", "maxSuffixSum", "maxSubarraySum", "rangeXorQuery",
             "rangeAndQuery", "rangeOrQuery", "rangeGcd", "longestEqualRun", "maxAltSubseqSum", "rangeHash",
             "rangeHashReversed", "isPalindrome", "leftmostPrefixSumGteX", "leftmostPrefixSumGtX", "rightmostSuffixSumGteX",
             "rightmostSuffixSumGtX"} | set(SEARCH)


class PSpec(Spec):
    def __init__(self, mods, fam, ups, rev):
        super().__init__(mods, fam, ups, rev)
        self.ops = sorted(set(self.ops) | {"copy"})

    def name(self):
        return "persistent-" + super().name()


def variants():
    return [PSpec(s.mods, s.fam, s.ups, s.rev) for s in A.variants() if not s.find and not s.shrink]


def header(cm, s):
    fields, tags = s.fields(), s.tags()
    lines = [f"@operations: {' '.join(s.ops)}", f"@data-structure-type: {DTYPE}", "@complexities:"]
    g = s.has("gcd")
    lines += [f"  {op}: {'N' if op == 'getAll' else 'log(N)*log(U) expected ?' if g and op != 'pointGet' else 'log(N) expected'}"
              for op in s.ops] + [f"  build: {'N*log(U) ?' if g else 'N'}", "@memory:", "  layout: none"]
    lines += ["  node: " + " ".join(f"{f}[1*N*log(N)]" for f in ["val", "sz", "L", "R"] + [f[0] for f in fields]),
              "  tags: " + (" ".join(f"{t[0]}[1*N*log(N)]" for t in tags) or "none"), "  other: none",
              "  note: nodes are never freed: each op copies the O(log N) nodes on its paths (N here counts ops too), and "
              "copies share every node they don't change; log(N) is of the length, which can be huge (long long)"]
    return "\n".join(f"{cm} {x}" for x in lines) + "\n"


def describe(s):
    keeps = ", ".join(A.DESC[m] for m in s.mods)
    ups = ", ".join(A.UOP[u] for u in sorted(s.ups))
    return (f"{MARK} with composable aggregates: an array you can insert into anywhere, " + ("reverse, " if s.rev else "") +
            "rotate, cut pieces out of (that is how to erase), paste them back and copy (copy(l, r): a[l..r] as a treap of "
            "its own in O(logN) however long, since the copy shares the same nodes; this one is unchanged)" +
            (f", with {ups}" if ups else "") + (f"; each node keeps {keeps} over its subtree" if keeps else "") +
            ". No node changes once another tree can see it: an op copies the nodes on its paths, so a copy and its original "
            "never affect each other. Lengths and indices are long long. All indices 0-based, ranges inclusive [l, r], an "
            "index always the position in the CURRENT array; searches return -1 when nothing qualifies." +
            (" Lazy tags mean \"already applied to this node, not yet to its children\"" +
             ("; a pending assign comes before a pending add." if s.asgTag and (s.addTag or s.ap or s.xorf) else ".")
             if s.tags() else ""))


def pending(push_body, lang):
    """the push's conditions, or-ed: is any tag pending at x"""
    if lang == "py":
        conds = re.findall(r"^        (?:el)?if (.+):$", push_body, re.M)
        return " or ".join(f"({c})" if " or " in c else c for c in conds)
    conds = re.findall(r"^        if \((.+?)\) (?:\{|apply)", push_body, re.M)
    return " || ".join(f"({c})" if "||" in c else c for c in conds)


# ================================================================================================ Python

def py(s):
    F, TG = s.fields(), s.tags()
    names = ["val", "L", "R", "sz"] + [f[0] for f in F] + [t[0] for t in TG]
    out = [header("#", s), "\n", wrap(describe(s), "#"), "import random\n" + ("from math import gcd\n" if s.has("gcd") else "") + "\n\n"]
    if s.has("hash"):
        out.append(PY_HASH_CONST)
    if s.clamp or s.has("alt"):
        out.append('INF, NEG = float("inf"), float("-inf")\n\n\n')
    if s.has("alt"):
        out.append('''def _altJoin(A, B):  # A's part, then B's: (++, +-, -+, --) = best by (start sign, end sign)
    a0, a1, a2, a3 = A
    b0, b1, b2, b3 = B
    return (max(a0, b0, a0 + b2, a1 + b0), max(a1, b1, a0 + b3, a1 + b1),
            max(a2, b2, a2 + b2, a3 + b0), max(a3, b3, a2 + b3, a3 + b1))


''')
    out.append(f"class {CLS}:\n" + wrap(A.POOL_NOTE.format(cls=CLS).replace(
        "Nodes are never freed (memory = every value ever inserted, over the whole run)",
        "Nodes are never freed (memory = O(log N) per op, over the whole run)"), "    #") +
        "".join(f"    {n} = [{v}]\n" for n, v in [("val", "0"), ("L", "0"), ("R", "0"), ("sz", "0")] + [(f[0], f[2]) for f in F] + [(t[0], t[2]) for t in TG]) + f'''    __slots__ = ("root",)

    # O(N) -- arr: the initial array (a list; leave it out to start empty)
    def __init__(self, arr=()):
        self.root = self._build(list(arr))

    def _empty(self):  # a new, empty {CLS} (on the same pool, like every one)
        return {CLS}()

    # O(1) -- the current length of the array
    def size(self):
        return self.sz[self.root]

''')
    pub = py_public(s)
    for op in QUERY_OPS & set(pub):  # (a query reads the cut-out range and puts nothing back: the root is unchanged)
        pub[op] = pub[op].replace("        self._join(a, b, c)\n", "")
    for op, expr, doc in (("pointAssign", "v", "a[i] = v"), ("pointAdd", "self.val[b] + v", "a[i] += v"),
                          ("pointChmax", "max(self.val[b], v)", "a[i] = max(a[i], v)"), ("pointChmin", "min(self.val[b], v)", "a[i] = min(a[i], v)")):
        pub[op] = f'''    # O(logN) expected -- {doc}
    def {op}(self, i, v):
        a, b, c = self._cut(i, i)  # (b: a fresh copy of a[i]'s node, alone)
        self.val[b] = {expr}
        self._pull(b)
        self._join(a, b, c)
'''
    pub["copy"] = f'''    # O(logN) expected -- a[l..r] (leave out l and r: the whole array, O(1)) as a {CLS} of its own; this one
    # is unchanged. The copy shares this one's nodes, so it costs O(logN) however long it is; needs
    # 0 <= l <= r < size(), else IndexError
    def copy(self, l=0, r=None):
        n = self.size()
        if r is None:
            r = n - 1
        whole = l == 0 and r == n - 1  # (an empty treap's whole copy too)
        if not whole and not 0 <= l <= r < n:
            raise IndexError(f"copy: needs 0 <= l <= r < size(), got l = {{l}}, r = {{r}}, n = {{n}}")
        piece = self._empty()
        piece.root = self.root if whole else self._cut(l, r)[1]
        return piece
'''
    out.append("\n".join(pub[op].replace("ImplicitTreap", CLS) for op in s.ops if op in pub))
    out.append(py_persist(py_internals(s), s, names))
    text = A.fit_comments(gcd_costs(s, "".join(out))).rstrip("\n") + "\n" + A.piece_example("py", f"{CLS}([1, 2, 3, 4, 5])", list("12345"))
    return text if TG else no_push(text, "py")


def arrays_tuple(names):  # "self.val, self.L, ..." wrapped under the for line at 120 columns
    parts, lines = [f"self.{n}" for n in names], [""]
    for p in parts:
        if lines[-1] and len(lines[-1]) + len(p) + 24 > 118:
            lines[-1] += ","
            lines.append("")
        lines[-1] += (", " if lines[-1] and not lines[-1].endswith(",") else "") + p
    return "\n                    ".join(lines)


def py_persist(text, s, names):
    text = text.replace("        self.pri.append(random.getrandbits(62))\n", "")
    a = text.index("    # a treap of new nodes holding vals in order: a Cartesian tree in one pass, O(len)\n")
    b = text.index("        return root\n", a) + len("        return root\n")
    text = text[:a] + '''    # a balanced tree of new nodes holding vals in order, O(len)
    def _build(self, vals, lo=0, hi=None):
        if hi is None:
            hi = len(vals)
        if lo >= hi:
            return 0
        mid = (lo + hi) // 2
        x = self._newNode(vals[mid])
        self.L[x] = self._build(vals, lo, mid)
        self.R[x] = self._build(vals, mid + 1, hi)
        self._pull(x)
        return x

    def _clone(self, x):  # a new copy of node x (sharing its children)
        y = len(self.val)
        for arr in (''' + arrays_tuple(names) + '''):
            arr.append(arr[x])
        return y
''' + text[b:]
    if "    def _push(self, x):" in text:
        a = text.index("    def _push(self, x):")
        b = text.find("\n    def ", a + 10)
        body = text[a:b]
        cond = pending(body, "py")
        head = "    def _push(self, x):  # hand x's pending tags to its children\n"
        assert body.startswith(head)
        body = (head + f"        if not ({cond}):\n            return\n" +
                "        L, R = self.L, self.R  # (the children get tags: fresh copies of them, since other trees may share them)\n"
                "        if L[x]:\n            L[x] = self._clone(L[x])\n        if R[x]:\n            R[x] = self._clone(R[x])\n" + body[len(head):])
        text = text[:a] + body + text[b:]
    a = text.index("    def _split(self, t, k):")
    b = text.index("    def _cut(self, l, r):")
    text = text[:a] + '''    def _split(self, t, k):  # (first k of t, the rest), as new nodes (t's are left as they were)
        if not t:
            return 0, 0
        t = self._clone(t)
        self._push(t)
        L, R = self.L, self.R
        if self.sz[L[t]] >= k:
            a, L[t] = self._split(L[t], k)
            self._pull(t)
            return a, t
        R[t], b = self._split(R[t], k - self.sz[L[t]] - 1)
        self._pull(t)
        return t, b

    def _merge(self, a, b):  # a's elements, then b's, as new nodes; the root is a with probability |a| / (|a| + |b|)
        if not a or not b:
            return a or b
        if random.randrange(self.sz[a] + self.sz[b]) < self.sz[a]:
            a = self._clone(a)
            self._push(a)
            self.R[a] = self._merge(self.R[a], b)
            self._pull(a)
            return a
        b = self._clone(b)
        self._push(b)
        self.L[b] = self._merge(a, self.L[b])
        self._pull(b)
        return b

''' + text[b:]
    return text


# ================================================================================================ C++

def cpp(s):
    F, TG = s.fields(), s.tags()
    S_ = s.has("sum") or bool(s.ms) or s.has("alt")
    out = [header("//", s), "\n", wrap(describe(s), "//"),
           "// T: int, long long, ..." + ("; sums are kept in S (long long for small T)." if S_ else ""), f"\ntemplate <typename T>\nstruct {CLS} {{\n"]
    if S_:
        out.append("    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;\n")
    if s.has("hash"):
        out.append("    using U64 = unsigned long long;\n")
    if s.clamp:
        out.append("    static constexpr T INF = numeric_limits<T>::max(), NEG = numeric_limits<T>::lowest();\n")
    if s.has("alt"):
        out.append("    static constexpr S NEG = numeric_limits<S>::lowest() / 4;  // (no alternating subsequence of that shape)\n")
    arrays = [("T", "val", "T(0)"), ("int", "L", "0"), ("int", "R", "0"), ("long long", "sz", "0")]
    arrays += [("long long" if f[0] in ("pr", "sr", "br") else f[1], f[0], f[3]) for f in F] + [(t[1], t[0], t[3]) for t in TG]
    out.append(wrap(A.POOL_NOTE.format(cls=CLS + "<T>").replace(
        "Nodes are never freed (memory = every value ever inserted, over the whole run)",
        "Nodes are never freed (memory = O(log N) per op, over the whole run)"), "    //") +
        "".join(f"    static inline vector<{t}> {n}{{{v}}};\n" for t, n, v in arrays) + f"""    int root = 0;

    // O(N) -- arr: the initial array (leave it out to start empty)
    explicit {CLS}(const vector<T>& arr = {{}}) {{ root = build(arr); }}

    {CLS} makeEmpty() const {{ return {CLS}(); }}  // (a new, empty one)
""")
    out.append('''
    static unsigned long long rnd() {
        static mt19937_64 g(chrono::steady_clock::now().time_since_epoch().count());
        return g();
    }
''' + (CPP_HASH_HELPERS.replace(
        "    static unsigned long long hadd(unsigned long long a, unsigned long long b) { return a + b >= HP ? a + b - HP : a + b; }",
        "    static unsigned long long hadd(unsigned long long a, unsigned long long b) {\n        return a + b >= HP ? a + b - HP : a + b;\n    }")
        if s.has("hash") else "") + '''
    // O(1) -- the current length of the array
    long long size() const { return sz[root]; }

''')
    pub = cpp_public(s)
    for op in QUERY_OPS & set(pub):
        pub[op] = pub[op].replace("        root = merge(merge(a, b), c);\n", "")
    for op, expr, doc in (("pointAssign", "v", "a[i] = v"), ("pointAdd", "T(val[b] + v)", "a[i] += v"),
                          ("pointChmax", "max(val[b], v)", "a[i] = max(a[i], v)"), ("pointChmin", "min(val[b], v)", "a[i] = min(a[i], v)")):
        pub[op] = f'''    // O(logN) expected -- {doc}
    void {op}(long long i, T v) {{
        int a, b, c;
        cut(i, i, a, b, c);  // (b: a fresh copy of a[i]'s node, alone)
        val[b] = {expr};
        pull(b);
        root = merge(merge(a, b), c);
    }}
'''
    pub["pointGet"] = "    // O(logN) expected -- a[i]\n    T pointGet(long long i) { return val[locate(i)]; }\n"
    pub["copy"] = f'''    // O(1) -- the whole array as a {CLS} of its own; this one is unchanged (they share nodes)
    {CLS} copy() const {{ return *this; }}

    // O(logN) expected -- a[l..r] as a {CLS} of its own; this one is unchanged. The copy
    // shares this one's nodes, so it costs O(logN) however long it is
    {CLS} copy(long long l, long long r) {{
        int a, b, c;
        cut(l, r, a, b, c);
        {CLS} piece = makeEmpty();
        piece.root = b;
        return piece;
    }}
'''
    pub["paste"] = pub["paste"].replace("ImplicitTreap", CLS) + f"    void paste(long long i, {CLS}&& other) {{ paste(i, other); }}  // (a temporary: paste(i, t.copy(l, r)))\n"
    pub["merge"] = pub["merge"].replace("ImplicitTreap", CLS) + f"    void merge({CLS}&& other) {{ merge(other); }}  // (a temporary: merge(t.copy()))\n"
    out.append("\n".join(pub[op].replace("ImplicitTreap", CLS) for op in s.ops if op in pub))
    out.append(cpp_persist(cpp_internals(s), s, arrays))
    text = A.fit_comments(gcd_costs(s, "".join(out))) + A.piece_example("cpp", f"{CLS}<int> t({{1, 2, 3, 4, 5}})", list("12345"))
    text = wide(text)
    return text if TG else no_push(text, "cpp")


def cpp_persist(text, s, arrays):
    text = text.replace("val.push_back(v), pri.push_back(rnd()), L.push_back(0)", "val.push_back(v), L.push_back(0)")
    assert A.CPP_BUILD in text
    text = text.replace(A.CPP_BUILD, '''
    int build(const vector<T>& vals) { return build(vals, 0, (int)vals.size()); }

    int build(const vector<T>& vals, int lo, int hi) {  // a balanced tree of new nodes holding vals[lo, hi), O(len)
        if (lo >= hi) return 0;
        int mid = (lo + hi) / 2, x = newNode(vals[mid]);
        int l = build(vals, lo, mid), r = build(vals, mid + 1, hi);
        L[x] = l, R[x] = r;
        pull(x);
        return x;
    }

    int clone(int x) {  // a new copy of node x (sharing its children)
''' + "".join(f"        {n}.push_back({n}[x]);\n" for _, n, _ in arrays) + '''        return (int)val.size() - 1;
    }
''')
    if "    void push(int x) {" in text:
        a = text.index("    void push(int x) {")
        b = text.index("\n    }\n", a) + len("\n    }\n")
        body = text[a:b]
        cond = pending(body, "cpp")
        head = "    void push(int x) {  // hand x's pending tags to its children\n"
        assert body.startswith(head), body[:80]
        body = (head + f"        if (!({cond})) return;\n" +
                "        // (the children get tags: fresh copies of them, since other trees may share them)\n"
                "        if (L[x]) L[x] = clone(L[x]);\n"
                "        if (R[x]) R[x] = clone(R[x]);\n" + body[len(head):])
        text = text[:a] + body + text[b:]
    a = text.index("    void split(int t, int k, int& a, int& b) {")
    b = text.index("    void cut(int l, int r, int& a, int& b, int& c) {")
    text = text[:a] + '''    void split(int t, long long k, int& a, int& b) {  // a = first k of t, b = the rest (as new nodes)
        if (!t) { a = b = 0; return; }
        t = clone(t);
        push(t);
        int x, y;  // (not straight into L[t] / R[t]: the clones below may move those arrays)
        if (sz[L[t]] >= k) split(L[t], k, x, y), L[t] = y, a = x, b = t;
        else split(R[t], k - sz[L[t]] - 1, x, y), R[t] = x, a = t, b = y;
        pull(t);
    }

    int merge(int a, int b) {  // a's elements, then b's, as new nodes; the root is a with probability |a| / (|a| + |b|)
        if (!a || !b) return a | b;
        if (rnd() % (unsigned long long)(sz[a] + sz[b]) < (unsigned long long)sz[a]) {
            a = clone(a);
            push(a);
            R[a] = merge(R[a], b);
            pull(a);
            return a;
        }
        b = clone(b);
        push(b);
        L[b] = merge(a, L[b]);
        pull(b);
        return b;
    }

''' + text[b:]
    a = text.index("    int locate(int i, vector<int>* path = nullptr) {")
    b = text.index("\n    }\n", a) + len("\n    }\n")
    text = text[:a] + '''    int locate(long long i) {  // the node holding a[i], every tag on the way pushed (harmless in place: see the top)
        int t = root;
        while (true) {
            push(t);
            long long ls = sz[L[t]];
            if (i == ls) return t;
            if (i < ls) t = L[t];
            else i -= ls + 1, t = R[t];
        }
    }
''' + text[b:]
    return text


def wide(text):
    """the public indices, the lengths and the walks' positions as long long"""
    for a, b in ((r"\(int l, int r\b", "(long long l, long long r"), (r"\(int l1, int r1, int l2, int r2\)", "(long long l1, long long r1, long long l2, long long r2)"),
                 (r"\(int i, ", "(long long i, "), (r"split\(int k\)", "split(long long k)"),
                 (r"void cut\(int l, int r, int& a", "void cut(long long l, long long r, int& a"),
                 (r"int a, b, c, len = r - l \+ 1;", "int a, b, c;\n        long long len = r - l + 1;"), (r"split\(b, \(int\)k, b1, b2\)", "split(b, k, b1, b2)"),
                 (r"int t = b, i = 0, res = -1;", "int t = b;\n        long long i = 0, res = -1;"),
                 (r"^    int ((?:leftmost|rightmost)\w+)\(", r"    long long \1("), (r"^    int longestEqualRun\(", "    long long longestEqualRun("),
                 (r"int n = sz\[x\];", "long long n = sz[x];"), (r"int rp = 1, rq = 1, bb = 1;", "long long rp = 1, rq = 1, bb = 1;"),
                 (r"int lt = L\[t\], ls = sz\[lt\];", "int lt = L[t];\n        long long ls = sz[lt];")):
        text = re.sub(a, b, text, flags=re.M)
    return text


def main():
    for d in os.listdir(DIR):
        t = os.path.join(DIR, d, "template.py")
        if os.path.exists(t) and f"@data-structure-type: {DTYPE}" in open(t).read():
            shutil.rmtree(os.path.join(DIR, d))
    seen = {}
    for s in variants():
        name = folder_name(s.ops)
        folder = name if len(name) <= 180 else s.name()
        assert folder not in seen, (folder, seen.get(folder))
        seen[folder] = s.name()
        os.makedirs(os.path.join(DIR, folder), exist_ok=True)
        write_template(os.path.join(DIR, folder, "template.py"), py(s))
        write_template(os.path.join(DIR, folder, "template.cpp"), aosify(cpp(s)))
    print("wrote", len(seen), "persistent treaps")


if __name__ == "__main__":
    main()
