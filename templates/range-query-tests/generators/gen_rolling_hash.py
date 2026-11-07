"""Rolling-hash deques: the sliding-window hashing templates (templates/strings/) as range-query templates, O(1) per op.

    python3 gen_rolling_hash.py      # then gen_fast.py, then npm run gen:range-queries in site/

The window is two lists, a front half stored reversed and a back half in order (a[i] is one O(1) lookup in either), so
both ends grow and shrink in O(1); when one half runs out, half of the other is moved over (amortized O(1)).

  rolling-hash-window         hash of the whole window only; both ends, point assign, all O(1)
  rolling-hash-two-stacks     range hashes (prefix hashes on the back half, suffix-anchored ones on the front), both
                              ends; pops amortized O(1); no point assign (it would invalidate every prefix hash)
  rolling-hash-palindrome     range hashes read both ways (isPalindrome), right end only, O(1) worst case
  rolling-hash-two-stacks-palindrome   both of the above: both ends, both readings, pops amortized

Hashing: polynomial mod a prime (2^61 - 1 by default), with a base drawn at random once per run and shared by
every structure of the run (so hashes compare across structures); a base and mod passed to the constructor are that one's own. Values can
be numbers or single characters (the very same file: @letters: same).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from note_lang import write_template  # noqa: E402

DIR = os.environ.get("RANGE_DIR") or os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "range-queries")
URL = "https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries"
POINT = ["pointAdd", "pointAssign", "pointChmax", "pointChmin", "pointGet"]


# ------------------------------------------------------------------------------------------------ header

def header(cm, ops, costs, memory, note):
    lines = [f"@operations: {' '.join(sorted(ops))}", "@data-structure-type: rolling-hash", "@letters: same", "@complexities:"]
    lines += [f"  {op}: {costs[op]}" for op in sorted(ops)] + [f"  build: {costs['build']}", "@memory:", "  layout: none"]
    lines += [f"  {k}: {memory[k]}" for k in ("node", "tags", "other")] + [f"  note: {note}"]
    return "\n".join(f"{cm} {x}" for x in lines) + "\n"


# ------------------------------------------------------------------------------------------------ Python

PY_CONST = '''import random


_HP = (1 << 61) - 1  # the default mod: a prime
# the run's random base, drawn once when the program starts: no test can be built against it, and every structure in the
# run hashes with it, so their hashes compare (two of these templates pasted into one file share this one variable)
_HB = random.randrange(1 << 40, _HP - 1)
'''


def py_class(left, ranges, rev, point):
    """left: both ends; ranges: prefix hashes (rangeHash); rev: reversed hashes too; point: point assign (window only)"""
    name = "RollingHashWindow" if not ranges else "RollingHashDeque" if not rev else "RollingHashPalindromeDeque" if left else "RollingHashPalindrome"
    s = f"class {name}:\n"
    s += "    # O(N) -- arr: the initial array (a list of ints, negatives included, or a string / list of single characters), or\n"
    s += "    # left out to start empty. Hashing just works with the defaults: any 64-bit values, negatives and characters, with\n"
    s += "    # the run's random base (shared by every structure of the run, so their hashes compare) and the prime mod 2^61 - 1.\n"
    s += "    # Set hashBase / hashMod only to match something else: then every value must be below the mod (a value v hashes as\n"
    s += "    # v + 1, so a 0 is not nothing), the mod a prime, and the base in [2, mod - 2]\n"
    s += "    def __init__(self, arr=(), hashBase=None, hashMod=None):\n"
    s += "        self.mod = _HP if hashMod is None else hashMod\n"
    s += "        self.base = (_HB if hashBase is None else hashBase) % self.mod\n"
    s += "        self.inv = pow(self.base, self.mod - 2, self.mod)\n"
    s += "        self.pw, self.pwi = [1], [1]  # pw[k] = base^k, pwi[k] = base^-k, grown as the window grows (amortized O(1))\n"
    s += "        vals = list(arr)\n"
    s += "        self._code = ord if vals and isinstance(vals[0], str) else int  # (characters hash by their code)\n"
    s += "        self.back = []\n"
    if left:
        s += "        self.front = []  # the first values, stored last to first\n"
    if ranges:
        s += "        self.P = []  # P[k]: hash of back[0..k] read left to right\n"
        if left:
            s += "        self.G = []  # G[j]: hash of front[j], front[j-1], ..., front[0] (a[0..j] when the front holds a[0..j]), times nothing: see _frontHash\n"
        if rev:
            s += "        self.RB = []  # RB[k]: sum of hval(back[k]) * base^k: the back half read backwards\n"
            if left:
                s += "        self.Q = []  # Q[j]: hash of front[0..j] in storage order (the front read backwards)\n"
    else:
        s += "        self.h = 0  # the hash of the whole window\n"
    s += "        for v in vals:\n            self.append(v)\n\n"
    s += "    # O(1) -- the current length of the window\n    def size(self):\n"
    s += "        return len(self.front) + len(self.back)\n\n" if left else "        return len(self.back)\n\n"
    s += "    # O(N) -- the whole window as a list\n    def getAll(self):\n"
    s += "        return self.front[::-1] + self.back\n\n" if left else "        return list(self.back)\n\n"
    get = "        f = len(self.front)\n        return self.front[f - 1 - i] if i < f else self.back[i - f]\n" if left else "        return self.back[i]\n"
    s += '    # O(1) -- a[i]; needs 0 <= i < size(), else raises IndexError\n    def pointGet(self, i):\n        if not 0 <= i < self.size():\n            raise IndexError(f"pointGet: needs 0 <= i < size(), got i = {i}, n = {self.size()}")\n' + get + "\n"
    # ---- appends and pops
    if ranges:
        s += '''    # O(1) -- append v at the right end
    def append(self, v):
        hv = (self._code(v) + 1) % self.mod
        k = len(self.back)
        self.P.append((self.P[-1] * self.base + hv) % self.mod if k else hv)
'''
        if rev:
            s += "        pw = self._powers(k)[0]\n        self.RB.append(((self.RB[-1] if k else 0) + hv * pw[k]) % self.mod)\n"
        s += "        self.back.append(v)\n\n"
        if left:
            s += '''    # O(1) -- insert v at the left end (it becomes a[0]; every index shifts up by 1)
    def appendLeft(self, v):
        hv = (self._code(v) + 1) % self.mod
        j = len(self.front)
        pw = self._powers(j)[0]
        self.G.append(((self.G[-1] if j else 0) + hv * pw[j]) % self.mod)
'''
            if rev:
                s += "        self.Q.append((self.Q[-1] * self.base + hv) % self.mod if j else hv)\n"
            s += "        self.front.append(v)\n\n"
        pops_cost = "1 amortized" if left else "1"
        s += f'''    # O({pops_cost}) -- remove a[size()-1] and return it; needs size() >= 1, else raises IndexError
    def pop(self):
        if self.size() < 1:
            raise IndexError("pop: needs size() >= 1")
'''
        if left:
            s += "        if not self.back:\n            self._moveToBack()\n"
        s += "        self.P.pop()\n" + ("        self.RB.pop()\n" if rev else "") + "        return self.back.pop()\n\n"
        if left:
            s += '''    # O(1 amortized) -- remove a[0] and return it (every index shifts down by 1); needs size() >= 1, else raises IndexError
    def popLeft(self):
        if self.size() < 1:
            raise IndexError("popLeft: needs size() >= 1")
        if not self.front:
            self._moveToFront()
        self.G.pop()
''' + ("        self.Q.pop()\n" if rev else "") + "        return self.front.pop()\n\n"
    else:  # the window hash: both ends and point assign, all O(1)
        s += '''    # O(1) -- append v at the right end
    def append(self, v):
        self.h = (self.h * self.base + self._code(v) + 1) % self.mod
        self.back.append(v)

    # O(1) -- insert v at the left end (it becomes a[0]; every index shifts up by 1)
    def appendLeft(self, v):
        n = self.size()
        self.h = (self.h + (self._code(v) + 1) * self._powers(n)[0][n]) % self.mod
        self.front.append(v)

    # O(1 amortized) -- remove a[size()-1] and return it; needs size() >= 1, else raises IndexError
    def pop(self):
        if self.size() < 1:
            raise IndexError("pop: needs size() >= 1")
        if not self.back:
            self._moveToBack()
        v = self.back.pop()
        self.h = (self.h - self._code(v) - 1) * self._powers(1)[1][1] % self.mod
        return v

    # O(1 amortized) -- remove a[0] and return it (every index shifts down by 1); needs size() >= 1, else raises IndexError
    def popLeft(self):
        if self.size() < 1:
            raise IndexError("popLeft: needs size() >= 1")
        if not self.front:
            self._moveToFront()
        v = self.front.pop()
        n = self.size()
        self.h = (self.h - (self._code(v) + 1) * self._powers(n)[0][n]) % self.mod
        return v

    # O(1) -- a[i] = v (overwrite); needs 0 <= i < size(), else raises IndexError
    def pointAssign(self, i, v):
        n = self.size()
        if not 0 <= i < n:
            raise IndexError(f"pointAssign: needs 0 <= i < size(), got i = {i}, n = {n}")
        f = len(self.front)
        old = self.front[f - 1 - i] if i < f else self.back[i - f]
        self.h = (self.h + (self._code(v) - self._code(old)) * self._powers(n)[0][n - 1 - i]) % self.mod
        if i < f:
            self.front[f - 1 - i] = v
        else:
            self.back[i - f] = v

    # O(1) -- a[i] += v; needs 0 <= i < size(), else raises IndexError
    def pointAdd(self, i, v):
        if not 0 <= i < self.size():
            raise IndexError(f"pointAdd: needs 0 <= i < size(), got i = {i}, n = {self.size()}")
        self.pointAssign(i, self.pointGet(i) + v)

    # O(1) -- a[i] = max(a[i], v); needs 0 <= i < size(), else raises IndexError
    def pointChmax(self, i, v):
        if not 0 <= i < self.size():
            raise IndexError(f"pointChmax: needs 0 <= i < size(), got i = {i}, n = {self.size()}")
        self.pointAssign(i, max(self.pointGet(i), v))

    # O(1) -- a[i] = min(a[i], v); needs 0 <= i < size(), else raises IndexError
    def pointChmin(self, i, v):
        if not 0 <= i < self.size():
            raise IndexError(f"pointChmin: needs 0 <= i < size(), got i = {i}, n = {self.size()}")
        self.pointAssign(i, min(self.pointGet(i), v))

    # O(1) -- hash of the whole window a[0..size()-1] (left to right, the same base and mod as every structure this run
    # unless you passed your own, so it compares with their hashes); needs size() >= 1, else raises IndexError
    def hashAll(self):
        if self.size() < 1:
            raise IndexError("hashAll: needs size() >= 1")
        return self.h

'''
    # ---- range hashes
    if ranges:
        s += '''    # O(1) -- hash of a[l..r] read left to right (mod 2^61 - 1, random base): equal ranges hash equal; needs
    # 0 <= l <= r < size(), else raises IndexError
    def rangeHash(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeHash: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        return self._hash(l, r)

'''
        if rev:
            s += '''    # O(1) -- hash of a[l..r] read right to left (what rangeHash gives for the reversed range); needs
    # 0 <= l <= r < size(), else raises IndexError
    def rangeHashReversed(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeHashReversed: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        return self._hashRev(l, r)

    # O(1) -- is a[l..r] a palindrome (its two readings hash equal); needs 0 <= l <= r < size(), else raises IndexError
    def isPalindrome(self, l, r):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"isPalindrome: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        return self._hash(l, r) == self._hashRev(l, r)

'''
        s += '''    # O(1) -- are a[l1..r1] and a[l2..r2] equal (same length and hash); needs 0 <= l1 <= r1 < size() and
    # 0 <= l2 <= r2 < size(), else raises IndexError
    def rangesEqual(self, l1, r1, l2, r2):
        if not (0 <= l1 <= r1 < self.size() and 0 <= l2 <= r2 < self.size()):
            raise IndexError(f"rangesEqual: needs 0 <= l1 <= r1 < size() and 0 <= l2 <= r2 < size(), got "
                             f"l1 = {l1}, r1 = {r1}, l2 = {l2}, r2 = {r2}, n = {self.size()}")
        return r1 - l1 == r2 - l2 and self._hash(l1, r1) == self._hash(l2, r2)

    # ---- internals ----

'''
        # the hash helpers
        back_hash = "        P, pw = self.P, self._powers(y - x + 1)[0]\n        return (P[y] - (P[x - 1] * pw[y - x + 1] if x else 0)) % self.mod\n"
        if left:
            s += '''    def _backHash(self, x, y):  # hash of back[x..y] left to right
''' + back_hash + '''
    def _frontHash(self, jl, jr):  # hash of front[jl], front[jl-1], ..., front[jr] (jr <= jl): a[f-1-jl .. f-1-jr]
        G, pwi = self.G, self._powers(jr)[1]
        return (G[jl] - (G[jr - 1] if jr else 0)) * pwi[jr] % self.mod

    def _hash(self, l, r):
        f = len(self.front)
        if l >= f:
            return self._backHash(l - f, r - f)
        if r < f:
            return self._frontHash(f - 1 - l, f - 1 - r)
        pw = self._powers(r - f + 1)[0]
        return (self._frontHash(f - 1 - l, 0) * pw[r - f + 1] + self._backHash(0, r - f)) % self.mod
'''
            if rev:
                s += '''
    def _backHashRev(self, x, y):  # hash of back[y], back[y-1], ..., back[x]
        RB, pwi = self.RB, self._powers(x)[1]
        return (RB[y] - (RB[x - 1] if x else 0)) * pwi[x] % self.mod

    def _frontHashRev(self, jr, jl):  # hash of front[jr], front[jr+1], ..., front[jl] (jr <= jl): a[f-1-jl .. f-1-jr] backwards
        Q, pw = self.Q, self._powers(jl - jr + 1)[0]
        return (Q[jl] - (Q[jr - 1] * pw[jl - jr + 1] if jr else 0)) % self.mod

    def _hashRev(self, l, r):
        f = len(self.front)
        if l >= f:
            return self._backHashRev(l - f, r - f)
        if r < f:
            return self._frontHashRev(f - 1 - r, f - 1 - l)
        pw = self._powers(f - l)[0]
        return (self._backHashRev(0, r - f) * pw[f - l] + self._frontHashRev(0, f - 1 - l)) % self.mod
'''
        else:
            s += "    def _hash(self, x, y):  # hash of a[x..y] left to right\n" + back_hash
            if rev:
                s += '''
    def _hashRev(self, x, y):  # hash of a[y], a[y-1], ..., a[x]
        RB, pwi = self.RB, self._powers(x)[1]
        return (RB[y] - (RB[x - 1] if x else 0)) * pwi[x] % self.mod
'''
    else:
        s += "    # ---- internals ----\n\n"
    s += '''    def _powers(self, k):  # pw and pwi with at least k + 1 entries
        pw, pwi = self.pw, self.pwi
        if len(pw) <= k:
            base, inv, mod = self.base, self.inv, self.mod
            while len(pw) <= k:
                pw.append(pw[-1] * base % mod)
                pwi.append(pwi[-1] * inv % mod)
        return pw, pwi
'''
    if left:
        # moving half of one side to the other: O(moved), each value moves at most once per half-emptying (amortized O(1))
        s += '''
    def _moveToFront(self):  # the back half's first half becomes the front (the front is empty)
        k = (len(self.back) + 1) // 2
        moved = self.back[:k]
        self.back = self.back[k:]
        self.front = moved[::-1]
'''
        if ranges:
            s += "        self._rebuild()\n"
        s += '''
    def _moveToBack(self):  # the front half's last-stored half (its first values... no: its values nearest the middle) becomes the back
        k = (len(self.front) + 1) // 2
        moved = self.front[:k]  # (the values nearest the middle are stored first)
        self.front = self.front[k:]
        self.back = moved[::-1]
'''
        if ranges:
            s += "        self._rebuild()\n"
        if ranges:
            s += '''
    def _rebuild(self):  # every prefix hash of both halves, O(size())
        code = self._code
        P, h = [], 0
        for v in self.back:
            h = (h * self.base + code(v) + 1) % self.mod
            P.append(h)
        self.P = P
        pw = self._powers(max(len(self.front), len(self.back)))[0]
        G, h = [], 0
        for j, v in enumerate(self.front):
            h = (h + (code(v) + 1) * pw[j]) % self.mod
            G.append(h)
        self.G = G
'''
            if rev:
                s += '''        RB, h = [], 0
        for k, v in enumerate(self.back):
            h = (h + (code(v) + 1) * pw[k]) % self.mod
            RB.append(h)
        self.RB = RB
        Q, h = [], 0
        for v in self.front:
            h = (h * self.base + code(v) + 1) % self.mod
            Q.append(h)
        self.Q = Q
'''
    return s.rstrip() + "\n"


# ------------------------------------------------------------------------------------------------ C++

CPP_CONST = '''// The run's random base, shared by every rolling-hash structure built without one (so their hashes compare): no test
// can be built against it. Two rolling-hash templates in one file share this one copy.
#ifndef LEETGOAT_ROLLING_HASH_SHARED
#define LEETGOAT_ROLLING_HASH_SHARED
struct RollingHashShared {
    static constexpr unsigned long long HP = (1ULL << 61) - 1;  // the default mod: a prime
    static inline unsigned long long base = 0;
    static unsigned long long rnd() {
        static mt19937_64 g(chrono::steady_clock::now().time_since_epoch().count());
        return g();
    }
    static void init() {  // (the random base, the first time anything is built)
        if (!base) base = (1ULL << 40) + rnd() % (HP - (1ULL << 41));
    }
};
#endif

'''


def cpp_class(left, ranges, rev, point):
    name = "RollingHashWindow" if not ranges else "RollingHashDeque" if not rev else "RollingHashPalindromeDeque" if left else "RollingHashPalindrome"
    H = "RollingHashShared"
    s = f"template <typename T>\nstruct {name} {{\n    using U64 = unsigned long long;\n    using R = {H};\n"
    s += "    vector<T> back;\n"
    if left:
        s += "    vector<T> front;  // the first values, stored last to first\n"
    if ranges:
        s += "    vector<U64> P;  // P[k]: hash of back[0..k] read left to right\n"
        if left:
            s += "    vector<U64> G;  // G[j]: sum of hval(front[j']) * base^j' over j' <= j: front[j..0] read in window order, times base^0\n"
        if rev:
            s += "    vector<U64> RB;  // RB[k]: sum of hval(back[k']) * base^k' over k' <= k: the back half read backwards\n"
            if left:
                s += "    vector<U64> Q;  // Q[j]: hash of front[0..j] in storage order (the front read backwards)\n"
    else:
        s += "    U64 h = 0;  // the hash of the whole window\n"
    s += "    U64 mod, base, baseInv;\n    vector<U64> pw{1}, pwi{1};  // pw[k] = base^k, pwi[k] = base^-k, grown as the window grows (amortized O(1))\n"
    s += "\n    // O(N) -- arr: the initial array (a vector of ints, long longs or chars; negatives are fine), or left out to start\n"
    s += "    // empty. Hashing just works with the defaults: any 64-bit values, negatives and characters, with the run's random base\n"
    s += "    // (shared by every structure of the run, so their hashes compare) and the prime mod 2^61 - 1 (the fast one: its\n"
    s += "    // reduction is two shifts). Set hashBase / hashMod only to match something else: then every value must be below the\n"
    s += "    // mod, the mod a prime below 2^63, and the base in [2, mod - 2]\n"
    s += f"    explicit {name}(const vector<T>& arr = {{}}, optional<U64> hashBase = nullopt, optional<U64> hashMod = nullopt) {{\n"
    s += "        R::init();\n        mod = hashMod ? *hashMod : R::HP;\n        base = (hashBase ? *hashBase : R::base) % mod;\n"
    s += "        baseInv = power(base, mod - 2);\n        for (const T& v : arr) append(v);\n    }\n\n"
    s += "    // O(1) -- the current length of the window\n    int size() const { return " + ("(int)(front.size() + back.size())" if left else "(int)back.size()") + "; }\n\n"
    s += "    // O(N) -- the whole window\n    vector<T> getAll() const {\n"
    s += "        vector<T> out(front.rbegin(), front.rend());\n        out.insert(out.end(), back.begin(), back.end());\n        return out;\n    }\n\n" if left else "        return back;\n    }\n\n"
    get = "        int f = (int)front.size();\n        return i < f ? front[f - 1 - i] : back[i - f];\n" if left else "        return back[i];\n"
    s += '    // O(1) -- a[i]; needs 0 <= i < size(), else throws out_of_range\n    T pointGet(int i) const {\n        if (i < 0 || i >= size()) throw out_of_range("pointGet: needs 0 <= i < size()");\n' + get + "    }\n\n"
    if ranges:
        s += '''    // O(1) -- append v at the right end
    void append(T v) {
        U64 hv = hval(v);
        size_t k = back.size();
        P.push_back(k ? add(mul(P.back(), base), hv) : hv);
'''
        if rev:
            s += "        powers(k);\n        RB.push_back(add(k ? RB.back() : 0, mul(hv, pw[k])));\n"
        s += "        back.push_back(v);\n    }\n\n"
        if left:
            s += '''    // O(1) -- insert v at the left end (it becomes a[0]; every index shifts up by 1)
    void appendLeft(T v) {
        U64 hv = hval(v);
        size_t j = front.size();
        powers(j);
        G.push_back(add(j ? G.back() : 0, mul(hv, pw[j])));
'''
            if rev:
                s += "        Q.push_back(j ? add(mul(Q.back(), base), hv) : hv);\n"
            s += "        front.push_back(v);\n    }\n\n"
        s += f'''    // O({"1 amortized" if left else "1"}) -- remove a[size()-1] and return it; needs size() >= 1, else throws out_of_range
    T pop() {{
        if (size() < 1) throw out_of_range("pop: needs size() >= 1");
'''
        if left:
            s += "        if (back.empty()) moveToBack();\n"
        s += "        P.pop_back();\n" + ("        RB.pop_back();\n" if rev else "") + "        T v = back.back();\n        back.pop_back();\n        return v;\n    }\n\n"
        if left:
            s += '''    // O(1 amortized) -- remove a[0] and return it (every index shifts down by 1); needs size() >= 1, else throws out_of_range
    T popLeft() {
        if (size() < 1) throw out_of_range("popLeft: needs size() >= 1");
        if (front.empty()) moveToFront();
        G.pop_back();
''' + ("        Q.pop_back();\n" if rev else "") + "        T v = front.back();\n        front.pop_back();\n        return v;\n    }\n\n"
    else:
        s += '''    // O(1) -- append v at the right end
    void append(T v) {
        h = add(mul(h, base), hval(v));
        back.push_back(v);
    }

    // O(1) -- insert v at the left end (it becomes a[0]; every index shifts up by 1)
    void appendLeft(T v) {
        size_t n = size();
        powers(n);
        h = add(h, mul(hval(v), pw[n]));
        front.push_back(v);
    }

    // O(1 amortized) -- remove a[size()-1] and return it; needs size() >= 1, else throws out_of_range
    T pop() {
        if (size() < 1) throw out_of_range("pop: needs size() >= 1");
        if (back.empty()) moveToBack();
        T v = back.back();
        back.pop_back();
        h = mul(sub(h, hval(v)), baseInv);
        return v;
    }

    // O(1 amortized) -- remove a[0] and return it (every index shifts down by 1); needs size() >= 1, else throws out_of_range
    T popLeft() {
        if (size() < 1) throw out_of_range("popLeft: needs size() >= 1");
        if (front.empty()) moveToFront();
        T v = front.back();
        front.pop_back();
        size_t n = size();
        powers(n);
        h = sub(h, mul(hval(v), pw[n]));
        return v;
    }

    // O(1) -- a[i] = v (overwrite); needs 0 <= i < size(), else throws out_of_range
    void pointAssign(int i, T v) {
        int n = size();
        if (i < 0 || i >= n) throw out_of_range("pointAssign: needs 0 <= i < size()");
        int f = (int)front.size();
        T& slot = i < f ? front[f - 1 - i] : back[i - f];
        powers(n - 1 - i);
        h = add(h, mul(sub(hval(v), hval(slot)), pw[n - 1 - i]));
        slot = v;
    }

    // O(1) -- a[i] += v; needs 0 <= i < size(), else throws out_of_range
    void pointAdd(int i, T v) {
        if (i < 0 || i >= size()) throw out_of_range("pointAdd: needs 0 <= i < size()");
        pointAssign(i, T(pointGet(i) + v));
    }

    // O(1) -- a[i] = max(a[i], v); needs 0 <= i < size(), else throws out_of_range
    void pointChmax(int i, T v) {
        if (i < 0 || i >= size()) throw out_of_range("pointChmax: needs 0 <= i < size()");
        pointAssign(i, max(pointGet(i), v));
    }

    // O(1) -- a[i] = min(a[i], v); needs 0 <= i < size(), else throws out_of_range
    void pointChmin(int i, T v) {
        if (i < 0 || i >= size()) throw out_of_range("pointChmin: needs 0 <= i < size()");
        pointAssign(i, min(pointGet(i), v));
    }

    // O(1) -- hash of the whole window a[0..size()-1] (left to right, the same base and mod as every structure this run
    // unless you passed your own, so it compares with their hashes); needs size() >= 1, else throws out_of_range
    U64 hashAll() const {
        if (size() < 1) throw out_of_range("hashAll: needs size() >= 1");
        return h;
    }

'''
    if ranges:
        s += '''    // O(1) -- hash of a[l..r] read left to right (mod 2^61 - 1, random base): equal ranges hash equal; needs
    // 0 <= l <= r < size(), else throws out_of_range
    U64 rangeHash(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeHash: needs 0 <= l <= r < size()");
        return hash(l, r);
    }

'''
        if rev:
            s += '''    // O(1) -- hash of a[l..r] read right to left (what rangeHash gives for the reversed range); needs
    // 0 <= l <= r < size(), else throws out_of_range
    U64 rangeHashReversed(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rangeHashReversed: needs 0 <= l <= r < size()");
        return hashRev(l, r);
    }

    // O(1) -- is a[l..r] a palindrome (its two readings hash equal); needs 0 <= l <= r < size(), else throws out_of_range
    bool isPalindrome(int l, int r) {
        if (l < 0 || l > r || r >= size()) throw out_of_range("isPalindrome: needs 0 <= l <= r < size()");
        return hash(l, r) == hashRev(l, r);
    }

'''
        s += '''    // O(1) -- are a[l1..r1] and a[l2..r2] equal (same length and hash); needs 0 <= l1 <= r1 < size() and
    // 0 <= l2 <= r2 < size(), else throws out_of_range
    bool rangesEqual(int l1, int r1, int l2, int r2) {
        if (l1 < 0 || l1 > r1 || r1 >= size() || l2 < 0 || l2 > r2 || r2 >= size())
            throw out_of_range("rangesEqual: needs 0 <= l1 <= r1 < size() and 0 <= l2 <= r2 < size()");
        return r1 - l1 == r2 - l2 && hash(l1, r1) == hash(l2, r2);
    }

    // ---- internals ----

'''
        back_hash = "        powers(y - x + 1);\n        return sub(P[y], x ? mul(P[x - 1], pw[y - x + 1]) : 0);\n"
        if left:
            s += "    U64 backHash(int x, int y) {  // hash of back[x..y] left to right\n" + back_hash + "    }\n\n"
            s += '''    U64 frontHash(int jl, int jr) {  // hash of front[jl], front[jl-1], ..., front[jr] (jr <= jl): a[f-1-jl .. f-1-jr]
        powers(jr);
        return mul(sub(G[jl], jr ? G[jr - 1] : 0), pwi[jr]);
    }

    U64 hash(int l, int r) {
        int f = (int)front.size();
        if (l >= f) return backHash(l - f, r - f);
        if (r < f) return frontHash(f - 1 - l, f - 1 - r);
        powers(r - f + 1);
        return add(mul(frontHash(f - 1 - l, 0), pw[r - f + 1]), backHash(0, r - f));
    }

'''
            if rev:
                s += '''    U64 backHashRev(int x, int y) {  // hash of back[y], back[y-1], ..., back[x]
        powers(x);
        return mul(sub(RB[y], x ? RB[x - 1] : 0), pwi[x]);
    }

    U64 frontHashRev(int jr, int jl) {  // hash of front[jr], ..., front[jl] (jr <= jl): a[f-1-jl .. f-1-jr] backwards
        powers(jl - jr + 1);
        return sub(Q[jl], jr ? mul(Q[jr - 1], pw[jl - jr + 1]) : 0);
    }

    U64 hashRev(int l, int r) {
        int f = (int)front.size();
        if (l >= f) return backHashRev(l - f, r - f);
        if (r < f) return frontHashRev(f - 1 - r, f - 1 - l);
        powers(f - l);
        return add(mul(backHashRev(0, r - f), pw[f - l]), frontHashRev(0, f - 1 - l));
    }

'''
        else:
            s += "    U64 hash(int x, int y) {  // hash of a[x..y] left to right\n" + back_hash + "    }\n\n"
            if rev:
                s += '''    U64 hashRev(int x, int y) {  // hash of a[y], a[y-1], ..., a[x]
        powers(x);
        return mul(sub(RB[y], x ? RB[x - 1] : 0), pwi[x]);
    }

'''
    else:
        s += "    // ---- internals ----\n\n"
    s += '''    U64 mul(U64 a, U64 b) const {
        __uint128_t c = (__uint128_t)a * b;
        if (mod != R::HP) return (U64)(c % mod);
        U64 r = (U64)(c & mod) + (U64)(c >> 61);  // (2^61 - 1: two shifts instead of a division)
        r = (r & mod) + (r >> 61);
        return r >= mod ? r - mod : r;
    }
    U64 add(U64 a, U64 b) const { return a + b >= mod ? a + b - mod : a + b; }
    U64 sub(U64 a, U64 b) const { return a >= b ? a - b : a + mod - b; }
    U64 power(U64 a, U64 e) const {
        U64 r = 1;
        for (; e; e >>= 1, a = mul(a, a)) if (e & 1) r = mul(r, a);
        return r;
    }
    void powers(size_t k) {  // pw and pwi with at least k + 1 entries
        while (pw.size() <= k) pw.push_back(mul(pw.back(), base)), pwi.push_back(mul(pwi.back(), baseInv));
    }

    U64 hval(T v) const {  // the hash of value v: v + 1, so a 0 is not nothing (a 0 in front would vanish)
        long long r = (long long)v % (long long)mod;
        return add(r < 0 ? (U64)(r + (long long)mod) : (U64)r, 1);
    }

'''
    if left:
        s += '''    void moveToFront() {  // the first half of the back becomes the front (the front is empty)
        size_t k = (back.size() + 1) / 2;
        front.assign(back.rend() - k, back.rend());
        back.erase(back.begin(), back.begin() + k);
''' + ("        rebuild();\n" if ranges else "") + '''    }

    void moveToBack() {  // the half of the front nearest the middle (stored first) becomes the back (the back is empty)
        size_t k = (front.size() + 1) / 2;
        back.assign(front.rend() - k, front.rend());
        front.erase(front.begin(), front.begin() + k);
''' + ("        rebuild();\n" if ranges else "") + '''    }
'''
        if ranges:
            s += '''
    void rebuild() {  // every prefix hash of both halves, O(size()): each value moves at most once per half-emptying
        powers(max(front.size(), back.size()));
        P.clear();
        for (const T& v : back) P.push_back(P.empty() ? hval(v) : add(mul(P.back(), base), hval(v)));
        G.clear();
        for (size_t j = 0; j < front.size(); j++) G.push_back(add(j ? G.back() : 0, mul(hval(front[j]), pw[j])));
'''
            if rev:
                s += '''        RB.clear();
        for (size_t k = 0; k < back.size(); k++) RB.push_back(add(k ? RB.back() : 0, mul(hval(back[k]), pw[k])));
        Q.clear();
        for (const T& v : front) Q.push_back(Q.empty() ? hval(v) : add(mul(Q.back(), base), hval(v)));
'''
            s += "    }\n"
    return s.rstrip() + "\n};\n"


# ------------------------------------------------------------------------------------------------ assembling

def build(folder, left, ranges, rev, point):
    ops = ["append", "pop", "pointGet", "getAll", "size"] + (["appendLeft", "popLeft"] if left else [])
    if ranges:
        ops += ["rangeHash", "rangesEqual"] + (["rangeHashReversed", "isPalindrome"] if rev else [])
    else:
        ops += POINT[:-1] + ["hashAll"]
    costs = {op: "1" for op in ops}
    costs["getAll"] = "N"
    costs["build"] = "N"
    if left and ranges:
        costs["pop"] = costs["popLeft"] = "1 amortized"
    if left and not ranges:
        costs["pop"] = costs["popLeft"] = "1 amortized"
    node = ["back[1*N]"] + (["front[1*N]"] if left else [])
    if ranges:
        node += ["P[1*N]"] + (["G[1*N]"] if left else []) + (["RB[1*N]"] if rev else []) + (["Q[1*N]"] if rev and left else [])
    memory = {"node": " ".join(node), "tags": "none", "other": "pw[1*N] pwi[1*N]"}
    notes = {
        "window": "two lists (a front half stored reversed, a back half in order), the hash of the whole window kept up to date; nothing per range, so only hashAll",
        "two-stacks": "prefix hashes on the back half, suffix-anchored ones on the front, so any range is O(1); a pop that empties a half moves half of the other over and rebuilds its hashes (amortized O(1)); no point assign (it would invalidate every prefix hash)",
        "palindrome": "prefix hashes read both ways; the right end only, so every op is O(1) worst case",
        "two-stacks-palindrome": "prefix hashes read both ways on both halves; a pop that empties a half moves half of the other over and rebuilds (amortized O(1)); no point assign",
    }
    key = folder[len("rolling-hash-"):]
    about = {
        "window": ["Rolling hash of a window that grows and shrinks at both ends in O(1): the hash of the whole window (hashAll), point",
                   "assign, and O(1) a[i]. The window is a front half stored reversed plus a back half in order."],
        "two-stacks": ["Rolling hashes of any range of a window that grows and shrinks at both ends (sliding windows, deques): the back half",
                       "keeps prefix hashes, the front half (stored reversed) suffix-anchored ones, so a range in either half or across the",
                       "middle is O(1). No point assign: that would change every prefix hash after it (a seg tree does that in log N)."],
        "palindrome": ["Rolling hashes read both ways over a window that grows and shrinks at the right end: range hashes, reversed range",
                       "hashes and palindrome checks in O(1) worst case (the longest palindrome around a centre by binary search)."],
        "two-stacks-palindrome": ["Rolling hashes read both ways over a window that grows and shrinks at both ends: range hashes, reversed range",
                                  "hashes and palindrome checks in O(1) (pops amortized), the longest palindrome around a centre by binary search."],
    }[key] + ["Values are numbers or single characters (then they hash by their code). All indices 0-based, ranges inclusive.",
              "Hashes: polynomial, mod a prime (2^61 - 1 unless you pass one) with a base drawn at random once per run and shared by",
              "every structure in it, so hashes compare across structures; a base and mod passed to the constructor are that",
              "structure's own. The base needs no relation to the alphabet: with a 61-bit prime mod and a random base, collisions",
              "are chance (about 2^-61 per comparison), not structure."]
    path = os.path.join(DIR, folder)
    os.makedirs(path, exist_ok=True)
    top = lambda c, name: f"{c} Template by https://github.com/ishaanbuildsthings\n{c} {URL}/{folder}/{name}\n"  # noqa: E731
    name = "RollingHashWindow" if not ranges else "RollingHashDeque" if not rev else "RollingHashPalindromeDeque" if left else "RollingHashPalindrome"
    query = "hashAll()" if not ranges else "rangeHash(l, r)"
    same = "hashAll() == {name}([3, 1, 4, 1, 5]).hashAll()" if not ranges else "rangeHash(0, 2) == {name}([3, 1, 4]).rangeHash(0, 2)"
    same_cpp = "hashAll() == {name}<long long>({{3, 1, 4, 1, 5}}).hashAll()" if not ranges else "rangeHash(0, 2) == {name}<long long>({{3, 1, 4}}).rangeHash(0, 2)"
    rows = [("arr = [3, 1, 4, 1, 5]", ""),
            ("base, mod = 911, 10**9 + 7", "set these only to match something else (unset, they are shared between structures, so hashes compare)"),
            (f"t1 = {name}(arr)", "the defaults: hashing just works for negatives, large numbers, chars, with the run's random base"),
            (f"t0 = {name}()", "or start empty"),
            (f"t2 = {name}(arr, hashBase=base)", "your base, mod 2^61 - 1"),
            (f"t3 = {name}(arr, hashMod=mod)", "the run's random base, your mod"),
            (f"t4 = {name}(arr, hashBase=base, hashMod=mod)", "both"),
            (f's = {name}("abacaba")', "a string works too (values are its characters)"),
            (f"t1.{same.format(name=name)}", "True: the same values, base and mod (the run's)")]
    width = max(len(code) for code, _ in rows) + 2
    py_usage = "#\n# Usage:\n" + "".join(f"#     {code.ljust(width)}# {note}\n" if note else f"#     {code}\n" for code, note in rows)
    rows = [("vector<long long> arr = {3, 1, 4, 1, 5};", ""),
            ("unsigned long long base = 911, mod = 1000000007;", "set these only to match something else (unset, they are shared between structures, so hashes compare)"),
            (f"{name}<long long> t1(arr);", "the defaults: hashing just works for negatives, large numbers, chars, with the run's random base"),
            (f"{name}<long long> t0;", "or start empty"),
            (f"{name}<int> ti(vector<int>{{3, 1, 4}});", "ints work too (T = int), and negatives"),
            (f"{name}<long long> t2(arr, base);", "your base, mod 2^61 - 1"),
            (f"{name}<long long> t3(arr, nullopt, mod);", "the run's random base, your mod"),
            (f"{name}<long long> t4(arr, base, mod);", "both"),
            (f"{name}<char> s(vector<char>(str.begin(), str.end()));", "characters: T = char"),
            (f"t1.{same_cpp.format(name=name)};", "true: the same values, base and mod (the run's)")]
    width = max(len(code) for code, _ in rows) + 2
    cpp_usage = "//\n// Usage:\n" + "".join(f"//     {code.ljust(width)}// {note}\n" if note else f"//     {code}\n" for code, note in rows)
    py = top("#", "template.py") + header("#", ops, costs, memory, notes[key]) + "\n" + "".join(f"# {x}\n" for x in about) + py_usage + PY_CONST + "\n\n" + py_class(left, ranges, rev, point)
    cpp = (top("//", "template.cpp") + "#include <bits/stdc++.h>\nusing namespace std;\nusing ll = long long;\n\n" +
           header("//", ops, costs, memory, notes[key]) + "\n" + "".join(f"// {x}\n" for x in about) + cpp_usage + CPP_CONST + cpp_class(left, ranges, rev, point))
    write_template(os.path.join(path, "template.py"), py)
    write_template(os.path.join(path, "template.cpp"), cpp)


def main():
    build("rolling-hash-window", True, False, False, True)
    build("rolling-hash-two-stacks", True, True, False, False)
    build("rolling-hash-palindrome", False, True, True, False)
    build("rolling-hash-two-stacks-palindrome", True, True, True, False)
    print(f"4 rolling-hash templates in {DIR}")


if __name__ == "__main__":
    main()
