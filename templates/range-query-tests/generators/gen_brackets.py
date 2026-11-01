"""Bracket sequences: isRBS(l, r) -- is s[l..r] a regular (balanced) bracket sequence?

    python3 gen_brackets.py

With '(' as +1 and every other character (')') as -1, s[l..r] is regular exactly when its total is 0 and no prefix of
it goes below 0 (its minimum prefix sum is >= 0). Templates, each the best at something:
  - static: prefix sums P plus a sparse table of P's minimums, O(1) a query, N log N memory
  - point updates: a seg tree of (sum, min prefix sum) per node, O(log N) a query or an update, 2N memory
  - range assign / range flip (open <-> close): a recursive lazy tree, one per subset; a flip negates, so the flip ones
    keep the max prefix sum too (the implicit treaps with isRBS are gen_treap_more.py's "brackets")
The values are the characters themselves (Python: a list of characters, or a str; C++: vector<char>), and openChar
(default "(") says which one opens.
"""
import os

from gen_treap import wrap
from note_lang import write_template

DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "range-queries")


def header(cm, ops, dtype, comp, build, node, other, note, layout="none"):
    lines = [f"@operations: {' '.join(ops)}", f"@data-structure-type: {dtype}", "@complexities:"]
    lines += [f"  {op}: {comp[op]}" for op in ops] + [f"  build: {build}", "@memory:", f"  layout: {layout}", f"  node: {node}",
              "  tags: none", f"  other: {other}", f"  note: {note}"]
    return "\n".join(f"{cm} {x}" for x in lines) + "\n"


STATIC_OPS = ["isRBS", "pointGet"]
DYN_OPS = ["getAll", "isRBS", "pointAssign", "pointGet"]

STATIC_DOC = '''{c} Static bracket sequence: isRBS(l, r) asks whether s[l..r] is a regular (balanced) bracket sequence, in O(1).
{c} With open = +1 and anything else = -1, s[l..r] is regular iff its total is 0 and no prefix of it dips below 0. With
{c} prefix sums P (P[0] = 0, P[i + 1] = P[i] + s[i]) that is P[r + 1] == P[l] and min(P[l + 1..r + 1]) >= P[l]: a sparse
{c} table answers the min in O(1). All indices 0-based, ranges inclusive. The values are the characters themselves.
'''

DYN_DOC = '''{c} Bracket sequence with point writes: isRBS(l, r) asks whether s[l..r] is a regular (balanced) bracket sequence.
{c} With open = +1 and anything else = -1, s[l..r] is regular iff its total is 0 and no prefix of it dips below 0. Each
{c} seg tree node keeps (sum, min prefix sum) of its range; two halves combine as
{c}   sum = L.sum + R.sum,   minPre = min(L.minPre, L.sum + R.minPre)
{c} and a query folds the covering nodes left to right. Iterative over 2 * size slots (size = next power of two >= n).
{c} All indices 0-based, ranges inclusive. The values are the characters themselves.
'''

PY_STATIC = STATIC_DOC.format(c="#") + '''

class StaticBrackets:
    # O(N log N) -- brackets: the sequence, a list of characters like ["(", ")", "("] (a str like "()(" works too);
    # openChar: the character that opens ("(" unless you pass e.g. "["); every other character closes
    def __init__(self, brackets, openChar="("):
        self.s = s = list(brackets)
        n = len(s)
        P = [0] * (n + 1)
        for i, ch in enumerate(s):
            P[i + 1] = P[i] + (1 if ch == openChar else -1)
        self.P = P
        self.table = [P]  # table[k][i] = min(P[i .. i + 2^k - 1])
        k = 1
        while 2 * k <= n + 1:
            prev = self.table[-1]
            self.table.append([a if a < b else b for a, b in zip(prev, prev[k:])])
            k *= 2

    # O(1) -- brackets[i]
    def pointGet(self, i):
        return self.s[i]

    # O(1) -- is brackets[l..r] a regular bracket sequence (balanced, never closing more than it opened)?
    def isRBS(self, l, r):
        P = self.P
        if P[r + 1] != P[l]:
            return False
        lo, hi = l + 1, r + 1
        k = (hi - lo + 1).bit_length() - 1
        row = self.table[k]
        a, b = row[lo], row[hi - (1 << k) + 1]
        return (a if a < b else b) >= P[l]
'''

CPP_STATIC = STATIC_DOC.format(c="//") + '''// T: char (or any type: openChar is the one that opens).
template <typename T>
struct StaticBrackets {
    vector<T> s;
    vector<int> P;              // prefix sums of +-1
    vector<vector<int>> table;  // table[k][i] = min(P[i .. i + 2^k - 1])

    // O(N log N) -- brackets: the sequence, e.g. vector<char>(str.begin(), str.end()); openChar: the character that
    // opens ('(' unless you pass e.g. '['); every other character closes
    explicit StaticBrackets(const vector<T>& brackets, T openChar = T('(')) : s(brackets), P(brackets.size() + 1, 0) {
        int n = (int)brackets.size();
        for (int i = 0; i < n; i++) P[i + 1] = P[i] + (brackets[i] == openChar ? 1 : -1);
        table.push_back(P);
        for (int k = 1; 2 * k <= n + 1; k *= 2) {
            const vector<int>& prev = table.back();
            vector<int> cur(prev.size() - k);
            for (size_t i = 0; i < cur.size(); i++) cur[i] = min(prev[i], prev[i + k]);
            table.push_back(std::move(cur));
        }
    }

    // O(1) -- brackets[i]
    T pointGet(int i) const { return s[i]; }

    // O(1) -- is brackets[l..r] a regular bracket sequence (balanced, never closing more than it opened)?
    bool isRBS(int l, int r) const {
        if (P[r + 1] != P[l]) return false;
        int lo = l + 1, hi = r + 1, k = 31 - __builtin_clz(hi - lo + 1);
        return min(table[k][lo], table[k][hi - (1 << k) + 1]) >= P[l];
    }
};
'''

PY_DYN = DYN_DOC.format(c="#") + '''

class BracketTree:
    __slots__ = ("n", "size", "openChar", "s", "sm", "mp")

    # O(N) -- brackets: the sequence, a list of characters like ["(", ")", "("] (a str like "()(" works too);
    # openChar: the character that opens ("(" unless you pass e.g. "["); every other character closes
    def __init__(self, brackets, openChar="("):
        self.s = s = list(brackets)
        self.openChar = openChar
        n = self.n = len(s)
        size = self.size = 1 << max(0, (n - 1).bit_length())
        sm = self.sm = [0] * (2 * size)  # sum of the node's +-1s
        mp = self.mp = [0] * (2 * size)  # its min prefix sum (0 for the empty prefix of padding)
        for i, ch in enumerate(s):
            v = 1 if ch == openChar else -1
            sm[size + i] = v
            mp[size + i] = v if v < 0 else 0
        for x in range(size - 1, 0, -1):
            l, r = 2 * x, 2 * x + 1
            sm[x] = sm[l] + sm[r]
            m = sm[l] + mp[r]
            mp[x] = mp[l] if mp[l] < m else m

    # O(N) -- the whole sequence
    def getAll(self):
        return self.s[:]

    # O(1) -- brackets[i]
    def pointGet(self, i):
        return self.s[i]

    # O(logN) -- brackets[i] = ch
    def pointAssign(self, i, ch):
        self.s[i] = ch
        sm, mp = self.sm, self.mp
        x = i + self.size
        v = 1 if ch == self.openChar else -1
        sm[x] = v
        mp[x] = v if v < 0 else 0
        x >>= 1
        while x:
            l, r = 2 * x, 2 * x + 1
            sm[x] = sm[l] + sm[r]
            m = sm[l] + mp[r]
            mp[x] = mp[l] if mp[l] < m else m
            x >>= 1

    # O(logN) -- is brackets[l..r] a regular bracket sequence (balanced, never closing more than it opened)?
    def isRBS(self, l, r):
        sm, mp = self.sm, self.mp
        ls = lm = 0  # (sum, min prefix) of the left part folded so far
        rights = []  # the right side's nodes, folded in afterwards right to left
        l += self.size
        r += self.size + 1
        while l < r:
            if l & 1:
                m = ls + mp[l]
                if m < lm:
                    lm = m
                ls += sm[l]
                l += 1
            if r & 1:
                r -= 1
                rights.append(r)
            l >>= 1
            r >>= 1
        for x in reversed(rights):
            m = ls + mp[x]
            if m < lm:
                lm = m
            ls += sm[x]
        return ls == 0 and lm >= 0
'''

CPP_DYN = DYN_DOC.format(c="//") + '''// T: char (or any type: openChar is the one that opens).
template <typename T>
struct BracketTree {
    int n, size;
    T openChar;
    vector<T> s;
    vector<int> sm, mp;  // per node: sum of its +-1s, min prefix sum (0 for the empty prefix)

    // O(N) -- brackets: the sequence, e.g. vector<char>(str.begin(), str.end()); openChar: the character that opens
    // ('(' unless you pass e.g. '['); every other character closes
    explicit BracketTree(const vector<T>& brackets, T openChar_ = T('('))
        : n((int)brackets.size()), size(1), openChar(openChar_), s(brackets) {
        while (size < n) size <<= 1;
        sm.assign(2 * size, 0), mp.assign(2 * size, 0);
        for (int i = 0; i < n; i++) setLeaf(i);
        for (int x = size - 1; x > 0; x--) pull(x);
    }

    // O(N) -- the whole sequence
    vector<T> getAll() const { return s; }

    // O(1) -- brackets[i]
    T pointGet(int i) const { return s[i]; }

    // O(logN) -- brackets[i] = ch
    void pointAssign(int i, T ch) {
        s[i] = ch;
        setLeaf(i);
        for (int x = (i + size) >> 1; x; x >>= 1) pull(x);
    }

    // O(logN) -- is brackets[l..r] a regular bracket sequence (balanced, never closing more than it opened)?
    bool isRBS(int l, int r) const {
        int ls = 0, lm = 0;  // (sum, min prefix) of the left part folded so far
        int rights[64], k = 0;  // the right side's nodes, folded in afterwards right to left
        for (l += size, r += size + 1; l < r; l >>= 1, r >>= 1) {
            if (l & 1) lm = min(lm, ls + mp[l]), ls += sm[l], l++;
            if (r & 1) rights[k++] = --r;
        }
        while (k--) lm = min(lm, ls + mp[rights[k]]), ls += sm[rights[k]];
        return ls == 0 && lm >= 0;
    }

    void setLeaf(int i) {
        int v = s[i] == openChar ? 1 : -1;
        sm[i + size] = v, mp[i + size] = min(v, 0);
    }

    void pull(int x) {
        sm[x] = sm[2 * x] + sm[2 * x + 1];
        mp[x] = min(mp[2 * x], sm[2 * x] + mp[2 * x + 1]);
    }
};
'''


# ------------------------------------------------------------------------------------------------ range assign / flip

def lazy_doc(c, A, FL):
    what = " / ".join((["RANGE ASSIGN"] if A else []) + (["RANGE FLIP (every open becomes a close and vice versa)"] if FL else []))
    text = (f"Bracket sequence with {what}: isRBS(l, r) asks whether s[l..r] is a regular (balanced) bracket sequence. "
            "With open = +1 and close = -1, s[l..r] is regular iff its total is 0 and no prefix of it dips below 0. Each node "
            "keeps (sum, min prefix sum" + (", max prefix sum" if FL else "") + ") of its range, prefixes including the empty "
            "one; two halves combine as sum = L.sum + R.sum, minPre = min(L.minPre, L.sum + R.minPre)" +
            (", maxPre likewise" if FL else "") + "." + (" An assigned node of k slots is all +k or all -k." if A else "") +
            (" A flip negates every value: sum -> -sum, and min / max prefix swap and change sign" +
             ("; a pending assign then flip is kept as exactly that (an assign clears the flip)." if A else ".") if FL else "") +
            " Recursive lazy tree over 4N slots; the characters themselves are not stored (a +1 reads back as openChar, a -1 "
            "as closeChar). All indices 0-based, ranges inclusive.")
    return wrap(text, c)


def py_lazy(A, FL):
    slots = ["n", "oc", "cc", "sm", "mn"] + (["mx"] if FL else []) + (["asg"] if A else []) + (["flp"] if FL else [])
    leaf = "\n            ".join(["self.sm[x] = v", "self.mn[x] = v if v < 0 else 0"] + (["self.mx[x] = v if v > 0 else 0"] if FL else []))
    pull = ("        sm, mn = self.sm, self.mn\n        l, r = 2 * x, 2 * x + 1\n        sm[x] = sm[l] + sm[r]\n"
            "        m = sm[l] + mn[r]\n        mn[x] = mn[l] if mn[l] < m else m\n" +
            ("        mx = self.mx\n        m = sm[l] + mx[r]\n        mx[x] = mx[l] if mx[l] > m else m\n" if FL else ""))
    apply = ""
    push = ""
    if A:
        apply += '''
    def _assign(self, x, k, v):  # node x (k slots) becomes all v (+1 or -1)
        t = v * k
        self.sm[x] = t
        self.mn[x] = t if t < 0 else 0
''' + ("        self.mx[x] = t if t > 0 else 0\n" if FL else "") + "        self.asg[x] = v\n" + ("        self.flp[x] = 0\n" if FL else "")
        push += '''        v = self.asg[x]
        if v:
            self._assign(2 * x, mid - lo + 1, v)
            self._assign(2 * x + 1, hi - mid, v)
            self.asg[x] = 0
'''
    if FL:
        apply += '''
    def _flip(self, x):  # every value of node x negated
        self.sm[x] = -self.sm[x]
        self.mn[x], self.mx[x] = -self.mx[x], -self.mn[x]
        self.flp[x] ^= 1
'''
        push += '''        if self.flp[x]:  # (after the assign: assign, then flip)
            self._flip(2 * x)
            self._flip(2 * x + 1)
            self.flp[x] = 0
'''
    upd_pub = ""
    if A:
        upd_pub += '''
    # O(logN) -- brackets[i] = ch for i in [l, r]
    def rangeAssign(self, l, r, ch):
        self._update(1, 0, self.n - 1, l, r, 1 if ch == self.oc else -1)
'''
    if FL:
        upd_pub += '''
    # O(logN) -- every open in brackets[l..r] becomes a close and vice versa
    def rangeFlip(self, l, r):
        self._update(1, 0, self.n - 1, l, r, 0)
'''
    do = ("(self._assign(x, hi - lo + 1, v) if v else self._flip(x))" if A and FL else
          "self._assign(x, hi - lo + 1, v)" if A else "self._flip(x)")
    return lazy_doc("#", A, FL) + f'''

class LazyBracketTree:
    __slots__ = ({", ".join(repr(x) for x in slots)})

    # O(N) -- brackets: the sequence, a list of characters like ["(", ")", "("] (a str like "()(" works too);
    # openChar / closeChar: the characters that open / close ("(" / ")" unless you pass e.g. "[" / "]"); a character
    # that isn't openChar counts as (and reads back as) closeChar
    def __init__(self, brackets, openChar="(", closeChar=")"):
        s = list(brackets)
        n = self.n = len(s)
        self.oc, self.cc = openChar, closeChar
        size = 4 * max(1, n)
        self.sm = [0] * size  # sum of the node's +-1s
        self.mn = [0] * size  # its min prefix sum (the empty prefix counts: <= 0)
''' + ("        self.mx = [0] * size  # its max prefix sum (>= 0)\n" if FL else "") + (
        "        self.asg = [0] * size  # pending assign: +1 / -1, 0 for none\n" if A else "") + (
        "        self.flp = [0] * size  # pending flip\n" if FL else "") + '''        if n:
            self._build(1, 0, n - 1, s)

    # O(N) -- the whole sequence, as characters
    def getAll(self):
        out = []
        if self.n:
            self._collect(1, 0, self.n - 1, out)
        return out

    # O(logN) -- is brackets[l..r] a regular bracket sequence (balanced, never closing more than it opened)?
    def isRBS(self, l, r):
        s, m = self._fold(1, 0, self.n - 1, l, r, 0, 0)
        return s == 0 and m >= 0

    # O(logN) -- brackets[i] = ch
    def pointAssign(self, i, ch):
        self._set(1, 0, self.n - 1, i, 1 if ch == self.oc else -1)

    # O(logN) -- brackets[i]
    def pointGet(self, i):
        x, lo, hi = 1, 0, self.n - 1
        while lo < hi:
            mid = (lo + hi) // 2
            self._push(x, lo, mid, hi)
            if i <= mid:
                x, hi = 2 * x, mid
            else:
                x, lo = 2 * x + 1, mid + 1
        return self.oc if self.sm[x] > 0 else self.cc
''' + upd_pub + f'''
    # ---- internals ----

    def _build(self, x, lo, hi, s):
        if lo == hi:
            v = 1 if s[lo] == self.oc else -1
            {leaf}
            return
        mid = (lo + hi) // 2
        self._build(2 * x, lo, mid, s)
        self._build(2 * x + 1, mid + 1, hi, s)
        self._pull(x)

    def _pull(self, x):
{pull}''' + apply + f'''
    def _push(self, x, lo, mid, hi):  # hand x's pending tags to its children
{push}
    def _update(self, x, lo, hi, l, r, v):  # v: assign +-1, or 0 for a flip
        if l <= lo and hi <= r:
            {do}
            return
        mid = (lo + hi) // 2
        self._push(x, lo, mid, hi)
        if l <= mid:
            self._update(2 * x, lo, mid, l, r, v)
        if r > mid:
            self._update(2 * x + 1, mid + 1, hi, l, r, v)
        self._pull(x)

    def _set(self, x, lo, hi, i, v):
        if lo == hi:
            {leaf}
            return
        mid = (lo + hi) // 2
        self._push(x, lo, mid, hi)
        if i <= mid:
            self._set(2 * x, lo, mid, i, v)
        else:
            self._set(2 * x + 1, mid + 1, hi, i, v)
        self._pull(x)

    # (s, m): sum and min prefix of everything left of this part; returns them with this part folded in
    def _fold(self, x, lo, hi, l, r, s, m):
        if l <= lo and hi <= r:
            t = s + self.mn[x]
            return s + self.sm[x], (t if t < m else m)
        mid = (lo + hi) // 2
        self._push(x, lo, mid, hi)
        if l <= mid:
            s, m = self._fold(2 * x, lo, mid, l, r, s, m)
        if r > mid:
            s, m = self._fold(2 * x + 1, mid + 1, hi, l, r, s, m)
        return s, m

    def _collect(self, x, lo, hi, out):
        if lo == hi:
            out.append(self.oc if self.sm[x] > 0 else self.cc)
            return
        mid = (lo + hi) // 2
        self._push(x, lo, mid, hi)
        self._collect(2 * x, lo, mid, out)
        self._collect(2 * x + 1, mid + 1, hi, out)
'''


def cpp_lazy(A, FL):
    fields = "sm, mn" + (", mx" if FL else "")
    leaf = "sm[x] = v, mn[x] = min(v, 0)" + (", mx[x] = max(v, 0)" if FL else "")
    apply, push = "", ""
    if A:
        apply += '''
    void assign(int x, int k, int v) {  // node x (k slots) becomes all v (+1 or -1)
        int t = v * k;
        sm[x] = t, mn[x] = min(t, 0)''' + (", mx[x] = max(t, 0)" if FL else "") + ", asg[x] = v" + (", flp[x] = 0" if FL else "") + ''';
    }
'''
        push += "        if (asg[x]) assign(2 * x, mid - lo + 1, asg[x]), assign(2 * x + 1, hi - mid, asg[x]), asg[x] = 0;\n"
    if FL:
        apply += '''
    void flip(int x) {  // every value of node x negated
        sm[x] = -sm[x];
        swap(mn[x], mx[x]), mn[x] = -mn[x], mx[x] = -mx[x];
        flp[x] ^= 1;
    }
'''
        push += "        if (flp[x]) flip(2 * x), flip(2 * x + 1), flp[x] = 0;  // (after the assign: assign, then flip)\n"
    upd_pub = ""
    if A:
        upd_pub += '''
    // O(logN) -- brackets[i] = ch for i in [l, r]
    void rangeAssign(int l, int r, T ch) { update(1, 0, n - 1, l, r, ch == oc ? 1 : -1); }
'''
    if FL:
        upd_pub += '''
    // O(logN) -- every open in brackets[l..r] becomes a close and vice versa
    void rangeFlip(int l, int r) { update(1, 0, n - 1, l, r, 0); }
'''
    do = ("v ? assign(x, hi - lo + 1, v) : flip(x)" if A and FL else "assign(x, hi - lo + 1, v)" if A else "flip(x)")
    tags = (["vector<signed char> asg;  // pending assign: +1 / -1, 0 for none"] if A else []) + (["vector<char> flp;  // pending flip"] if FL else [])
    inits = "".join(f"        {f}.assign(4 * max(1, n), 0);\n" for f in ["sm", "mn"] + (["mx"] if FL else []) + (["asg"] if A else []) + (["flp"] if FL else []))
    return lazy_doc("//", A, FL) + '''// T: char (or any type: openChar / closeChar are the ones that open / close).
template <typename T>
struct LazyBracketTree {
    int n;
    T oc, cc;
    vector<int> ''' + fields + ";  // per node: sum of its +-1s, min" + (" / max" if FL else "") + " prefix sum (the empty prefix counts)\n" + "".join(
        f"    {t}\n" for t in tags) + '''
    // O(N) -- brackets: the sequence, e.g. vector<char>(str.begin(), str.end()); openChar / closeChar: the characters
    // that open / close ('(' / ')' unless you pass e.g. '[' / ']'); a character that isn't openChar counts as (and
    // reads back as) closeChar
    explicit LazyBracketTree(const vector<T>& brackets, T openChar = T('('), T closeChar = T(')'))
        : n((int)brackets.size()), oc(openChar), cc(closeChar) {
''' + inits + '''        if (n) build(1, 0, n - 1, brackets);
    }

    // O(N) -- the whole sequence, as characters
    vector<T> getAll() {
        vector<T> out;
        out.reserve(n);
        if (n) collect(1, 0, n - 1, out);
        return out;
    }

    // O(logN) -- is brackets[l..r] a regular bracket sequence (balanced, never closing more than it opened)?
    bool isRBS(int l, int r) {
        int s = 0, m = 0;
        fold(1, 0, n - 1, l, r, s, m);
        return s == 0 && m >= 0;
    }

    // O(logN) -- brackets[i] = ch
    void pointAssign(int i, T ch) { set(1, 0, n - 1, i, ch == oc ? 1 : -1); }

    // O(logN) -- brackets[i]
    T pointGet(int i) {
        int x = 1, lo = 0, hi = n - 1;
        while (lo < hi) {
            int mid = (lo + hi) / 2;
            push(x, lo, mid, hi);
            if (i <= mid) x = 2 * x, hi = mid;
            else x = 2 * x + 1, lo = mid + 1;
        }
        return sm[x] > 0 ? oc : cc;
    }
''' + upd_pub + f'''
    // ---- internals ----

    void build(int x, int lo, int hi, const vector<T>& s) {{
        if (lo == hi) {{
            int v = s[lo] == oc ? 1 : -1;
            {leaf};
            return;
        }}
        int mid = (lo + hi) / 2;
        build(2 * x, lo, mid, s), build(2 * x + 1, mid + 1, hi, s);
        pull(x);
    }}

    void pull(int x) {{
        int l = 2 * x, r = 2 * x + 1;
        sm[x] = sm[l] + sm[r], mn[x] = min(mn[l], sm[l] + mn[r]){", mx[x] = max(mx[l], sm[l] + mx[r])" if FL else ""};
    }}
''' + apply + f'''
    void push(int x, int lo, int mid, int hi) {{  // hand x's pending tags to its children
{push}    }}

    void update(int x, int lo, int hi, int l, int r, int v) {{  // v: assign +-1, or 0 for a flip
        if (l <= lo && hi <= r) {{
            {do};
            return;
        }}
        int mid = (lo + hi) / 2;
        push(x, lo, mid, hi);
        if (l <= mid) update(2 * x, lo, mid, l, r, v);
        if (r > mid) update(2 * x + 1, mid + 1, hi, l, r, v);
        pull(x);
    }}

    void set(int x, int lo, int hi, int i, int v) {{
        if (lo == hi) {{
            {leaf};
            return;
        }}
        int mid = (lo + hi) / 2;
        push(x, lo, mid, hi);
        if (i <= mid) set(2 * x, lo, mid, i, v);
        else set(2 * x + 1, mid + 1, hi, i, v);
        pull(x);
    }}

    // s, m: sum and min prefix of everything left of this part; this part gets folded in
    void fold(int x, int lo, int hi, int l, int r, int& s, int& m) {{
        if (l <= lo && hi <= r) {{
            m = min(m, s + mn[x]), s += sm[x];
            return;
        }}
        int mid = (lo + hi) / 2;
        push(x, lo, mid, hi);
        if (l <= mid) fold(2 * x, lo, mid, l, r, s, m);
        if (r > mid) fold(2 * x + 1, mid + 1, hi, l, r, s, m);
    }}

    void collect(int x, int lo, int hi, vector<T>& out) {{
        if (lo == hi) {{
            out.push_back(sm[x] > 0 ? oc : cc);
            return;
        }}
        int mid = (lo + hi) / 2;
        push(x, lo, mid, hi);
        collect(2 * x, lo, mid, out), collect(2 * x + 1, mid + 1, hi, out);
    }}
}};
'''


def main():
    for A, FL in ((True, False), (False, True), (True, True)):
        ops = sorted(["getAll", "isRBS", "pointAssign", "pointGet"] + (["rangeAssign"] if A else []) + (["rangeFlip"] if FL else []))
        comp = {op: "N" if op == "getAll" else "log(N)" for op in ops}
        node = " ".join(f"{f}[4*N]" for f in ["sm", "mn"] + (["mx"] if FL else []))
        tags = " ".join((["asg[4*N]"] if A else []) + (["flp[4*N]"] if FL else []))
        folder = os.path.join(DIR, "-".join(o for o in ops if o != "getAll"))
        os.makedirs(folder, exist_ok=True)
        for ext, cm, body in (("py", "#", py_lazy(A, FL)), ("cpp", "//", cpp_lazy(A, FL))):
            head = header(cm, ops, "lazy-seg-tree", comp, "N", node, "none", "the characters aren't stored: a node's +-1s say them",
                          "4n-recursive").replace(f"{cm}   tags: none", f"{cm}   tags: {tags}")
            write_template(os.path.join(folder, f"template.{ext}"), head + "\n" + body)
        print("wrote", os.path.basename(folder))
    static_note = "P: prefix sums; the table holds P's minimums over every power-of-two window"
    dyn_note = "one (sum, min prefix sum) pair per node over 2 * size slots (size = next power of two >= n); s: the characters"
    for ops, dtype, comp, build, node, other, note, layout, py, cpp in (
            (STATIC_OPS, "sparse-table", {"isRBS": "1", "pointGet": "1"}, "N*log(N)", "table[1*N*log(N)]", "P[1*N] s[1*N]",
             static_note, "none", PY_STATIC, CPP_STATIC),
            (DYN_OPS, "seg-tree", {"getAll": "N", "isRBS": "log(N)", "pointAssign": "log(N)", "pointGet": "1"}, "N", "sm[4*N] mp[4*N]", "s[1*N]",
             dyn_note, "pow2-iterative", PY_DYN, CPP_DYN)):
        folder = os.path.join(DIR, "-".join(o for o in ops if o != "getAll"))
        os.makedirs(folder, exist_ok=True)
        write_template(os.path.join(folder, "template.py"), header("#", ops, dtype, comp, build, node, other, note, layout) + "\n" + py)
        write_template(os.path.join(folder, "template.cpp"), header("//", ops, dtype, comp, build, node, other, note, layout) + "\n" + cpp)
        print("wrote", os.path.basename(folder))


if __name__ == "__main__":
    main()
