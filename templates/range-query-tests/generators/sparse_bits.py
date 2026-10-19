"""Sparse (dynamic) versions of the Fenwick-tree templates: sparse.py + sparse.cpp per folder.

    python3 sparse_bits.py

Every position of [lo, hi] starts at 0. Each template keeps a few arrays of point changes (differences, or the
coefficients of a prefix-sum polynomial) and only ever needs their prefix sums.
  Python: a Fenwick tree in a dict (only touched indices exist); several arrays share one dict of lists.
  C++:    a dynamic prefix-sum tree in one pool shared by every tree of the type (resetPool() between test cases);
          a point change adds to the O(logU) nodes on its root path, a prefix sum walks one root path. Unsigned
          arithmetic wraps mod 2^64, so results are exact whenever they fit in long long, even when an
          intermediate (like x^2 for an index x near 10^12) does not.
Formulas run on offsets x = i - lo in [0, n), n = hi - lo + 1, exactly like the dense templates on 0-based indices.
"""
import sys

sys.dont_write_bytecode = True
from sparse_bits_lib import MOD_POINT, PLAIN, cpp_struct, point_ops, py_class, write  # noqa: E402

# ---------------------------------------------------------------- range add, point get

pp, cp = point_ops("rangeAdd")
write(PLAIN + ["rangeAdd"], ("d[2*log(U)]", "links[4*log(U)]"), "a range add changes two differences",
      py_class("SparseRangeAddBIT", "Range add, point get: prefix sums of the difference array d[i] = a[i] - a[i - 1].",
               ["d"], "add", '''
    # O(logU) -- a[i] += v for i in [l, r]
    def rangeAdd(self, l, r, v):
        if l > r:
            return
        self._add(l - self.lo, v)
        if r < self.hi:
            self._add(r + 1 - self.lo, -v)

    # O(logU) -- a[i]
    def pointGet(self, i):
        return self._prefix(i - self.lo)
''' + pp),
      cpp_struct("SparseRangeAddBIT", "Range add, point get: prefix sums of the difference array d[i] = a[i] - a[i - 1].",
                 1, "add", '''
    // O(logU) -- a[i] += v for i in [l, r]
    void rangeAdd(long long l, long long r, T v) {
        if (l > r) return;
        add(l - lo, F{W(v)});
        if (r < hi) add(r + 1 - lo, F{W(0) - W(v)});
    }

    // O(logU) -- a[i]
    T pointGet(long long i) const { return T(prefix(i - lo)[0]); }
''' + cp))

# ---------------------------------------------------------------- range xor, point get

write(PLAIN + ["rangeXorApply"], ("d[2*log(U)]", "links[4*log(U)]"), "a range xor changes two xor-differences",
      py_class("SparseRangeXorBIT", "Range xor, point get: prefix xors of the xor-difference array d[i] = a[i] ^ a[i - 1].",
               ["d"], "xor", '''
    # O(logU) -- a[i] ^= x for i in [l, r]
    def rangeXorApply(self, l, r, x):
        if l > r:
            return
        self._add(l - self.lo, x)
        if r < self.hi:
            self._add(r + 1 - self.lo, x)

    # O(logU) -- a[i]
    def pointGet(self, i):
        return self._prefix(i - self.lo)

    # O(logU) -- a[i] = val
    def pointAssign(self, i, val):
        d = self.pointGet(i) ^ val
        if d:
            self.rangeXorApply(i, i, d)

    # O(logU) -- a[i] += delta
    def pointAdd(self, i, delta):
        self.pointAssign(i, self.pointGet(i) + delta)

    # O(logU) -- a[i] = max(a[i], val)
    def pointChmax(self, i, val):
        cur = self.pointGet(i)
        if val > cur:
            self.rangeXorApply(i, i, cur ^ val)

    # O(logU) -- a[i] = min(a[i], val)
    def pointChmin(self, i, val):
        cur = self.pointGet(i)
        if val < cur:
            self.rangeXorApply(i, i, cur ^ val)
'''),
      cpp_struct("SparseRangeXorBIT", "Range xor, point get: prefix xors of the xor-difference array d[i] = a[i] ^ a[i - 1].",
                 1, "xor", '''
    // O(logU) -- a[i] ^= x for i in [l, r]
    void rangeXorApply(long long l, long long r, T x) {
        if (l > r) return;
        add(l - lo, F{x});
        if (r < hi) add(r + 1 - lo, F{x});
    }

    // O(logU) -- a[i]
    T pointGet(long long i) const { return prefix(i - lo)[0]; }

    // O(logU) -- a[i] = v
    void pointAssign(long long i, T v) {
        T d = pointGet(i) ^ v;
        if (d) rangeXorApply(i, i, d);
    }

    // O(logU) -- a[i] += delta
    void pointAdd(long long i, T delta) { pointAssign(i, pointGet(i) + delta); }

    // O(logU) -- a[i] = max(a[i], v)
    void pointChmax(long long i, T v) { T cur = pointGet(i); if (v > cur) rangeXorApply(i, i, cur ^ v); }

    // O(logU) -- a[i] = min(a[i], v)
    void pointChmin(long long i, T v) { T cur = pointGet(i); if (v < cur) rangeXorApply(i, i, cur ^ v); }
'''))

# ---------------------------------------------------------------- range add + range sum: P(x) = A(x) + B(x) * x

ADDSUM_DESC = ("Range add + range sum: adding v on [l, r] changes the prefix sum P(x) = a[lo] + ... + a[x] by\n"
               "{c}   v * (x - l + 1) for x in [l, r], and the whole v * (r - l + 1) past r,\n"
               "{c} so P(x) = A(x) + B(x) * x with A, B prefix sums of two arrays of point changes.")
for mod in (False, True):
    sfx = "Mod" if mod else ""
    name = f"SparseRangeAddSumBIT{sfx}"
    ops = (MOD_POINT + ["rangeAddMod", "rangeSumMod"]) if mod else (PLAIN + ["rangeAdd", "rangeSum"])
    pp, cp = point_ops(f"rangeAdd{sfx}", chm=not mod)
    py_body = f'''
    # O(logU) -- a[i] += v{" (mod p)" if mod else ""} for i in [l, r]
    def rangeAdd{sfx}(self, l, r, v):
        if l > r:
            return
        l -= self.lo
        r -= self.lo
        a = v * (1 - l)
        self._add(l, a, v)
        if r + 1 < self.n:
            self._add(r + 1, v * (r - l + 1) - a, -v)

    # O(logU) -- a[lo] + ... + a[lo + x]{" mod p" if mod else ""} (0 for x = -1)
    def _sum(self, x):
        sa, sb = self._prefix(x)
        return {"(sa + sb * x) % self.mod" if mod else "sa + sb * x"}

    # O(logU) -- a[l] + ... + a[r]{" mod p" if mod else ""}
    def rangeSum{sfx}(self, l, r):
        if l > r:
            return 0
        return {"(self._sum(r - self.lo) - self._sum(l - 1 - self.lo)) % self.mod" if mod else "self._sum(r - self.lo) - self._sum(l - 1 - self.lo)"}

    # O(logU) -- a[i]{", in [0, mod)" if mod else ""}
    def pointGet(self, i):
        return self.rangeSum{sfx}(i, i)
''' + pp
    if mod:
        cpp_body = '''
    T norm(W x) const { return T((x % mod + mod) % mod); }

    // O(logU) -- a[i] += v (mod p) for i in [l, r]
    void rangeAddMod(long long l, long long r, T v) {
        if (l > r) return;
        l -= lo, r -= lo;
        T c = norm(v), a = norm(W(c) * norm(1 - l));
        add(l, F{a, c});
        if (r + 1 < n) add(r + 1, F{norm(W(c) * norm(r - l + 1) - a), norm(-W(c))});
    }

    // O(logU) -- (a[lo] + ... + a[lo + x]) mod p (0 for x = -1)
    T sum(long long x) const {
        F s = prefix(x);
        return norm(s[0] + W(s[1]) * norm(x));
    }

    // O(logU) -- (a[l] + ... + a[r]) mod p
    T rangeSumMod(long long l, long long r) const { return l <= r ? norm(W(sum(r - lo)) - sum(l - 1 - lo)) : T(0); }

    // O(logU) -- a[i], in [0, mod)
    T pointGet(long long i) const { return rangeSumMod(i, i); }
''' + cp
    else:
        cpp_body = '''
    // O(logU) -- a[i] += v for i in [l, r]
    void rangeAdd(long long l, long long r, T v) {
        if (l > r) return;
        l -= lo, r -= lo;
        W c = W(v), a = c * W(1 - l);
        add(l, F{a, c});
        if (r + 1 < n) add(r + 1, F{c * W(r - l + 1) - a, W(0) - c});
    }

    // O(logU) -- a[lo] + ... + a[lo + x] (0 for x = -1)
    W sum(long long x) const {
        F s = prefix(x);
        return s[0] + s[1] * W(x);
    }

    // O(logU) -- a[l] + ... + a[r]
    long long rangeSum(long long l, long long r) const { return l <= r ? (long long)(sum(r - lo) - sum(l - 1 - lo)) : 0; }

    // O(logU) -- a[i]
    T pointGet(long long i) const { return T(rangeSum(i, i)); }
''' + cp
    write(ops, ("A[2*log(U)] B[2*log(U)]", "links[4*log(U)]"), "a range add changes two points of A and B",
          py_class(name, ADDSUM_DESC.format(c="#") + (" All mod p." if mod else ""), ["A", "B"], "mod" if mod else "add",
                   py_body),
          cpp_struct(name, ADDSUM_DESC.format(c="//") + (" All mod p." if mod else ""), 2, "mod" if mod else "add",
                     cpp_body))

# ---------------------------------------------------------------- arithmetic-sequence add, point get: a[x] = C(x) + x * S(x)

AP_DESC = ("Range add of an arithmetic sequence (and plain range add), point get{m}. Adding start + (i - l) * step on\n"
           "{c} [l, r] is adding the line c0 + c1 * x (x = i - lo), so a[x] = C(x) + x * S(x) with C, S prefix sums of\n"
           "{c} two difference arrays.")
for mod in (False, True):
    sfx = "Mod" if mod else ""
    name = f"SparseArithSeqBIT{sfx}"
    ops = (MOD_POINT + ["rangeAddArithSeqMod", "rangeAddMod"]) if mod else (PLAIN + ["rangeAdd", "rangeAddArithSeq"])
    pp, cp = point_ops(f"rangeAdd{sfx}", chm=not mod)
    py_body = f'''
    # O(logU) -- a[l + j] += start + j * step{" (mod p)" if mod else ""} for j in [0, r - l]
    def rangeAddArithSeq{sfx}(self, l, r, start, step):
        if l > r:
            return
        l -= self.lo
        r -= self.lo
        c0 = start - step * l
        self._add(l, c0, step)
        if r + 1 < self.n:
            self._add(r + 1, -c0, -step)

    # O(logU) -- a[i] += v{" (mod p)" if mod else ""} for i in [l, r]
    def rangeAdd{sfx}(self, l, r, v):
        self.rangeAddArithSeq{sfx}(l, r, v, 0)

    # O(logU) -- a[i]{", in [0, mod)" if mod else ""}
    def pointGet(self, i):
        x = i - self.lo
        c, s = self._prefix(x)
        return {"(c + s * x) % self.mod" if mod else "c + s * x"}
''' + pp
    if mod:
        cpp_body = '''
    T norm(W x) const { return T((x % mod + mod) % mod); }

    // O(logU) -- a[l + j] += start + j * step (mod p) for j in [0, r - l]
    void rangeAddArithSeqMod(long long l, long long r, T start, T step) {
        if (l > r) return;
        l -= lo, r -= lo;
        T c1 = norm(step), c0 = norm(W(start) - W(c1) * norm(l));
        add(l, F{c0, c1});
        if (r + 1 < n) add(r + 1, F{norm(-W(c0)), norm(-W(c1))});
    }

    // O(logU) -- a[i] += v (mod p) for i in [l, r]
    void rangeAddMod(long long l, long long r, T v) { rangeAddArithSeqMod(l, r, v, 0); }

    // O(logU) -- a[i], in [0, mod)
    T pointGet(long long i) const {
        F s = prefix(i - lo);
        return norm(s[0] + W(s[1]) * norm(i - lo));
    }
''' + cp
    else:
        cpp_body = '''
    // O(logU) -- a[l + j] += start + j * step for j in [0, r - l]
    void rangeAddArithSeq(long long l, long long r, T start, T step) {
        if (l > r) return;
        l -= lo, r -= lo;
        W c1 = W(step), c0 = W(start) - c1 * W(l);
        add(l, F{c0, c1});
        if (r + 1 < n) add(r + 1, F{W(0) - c0, W(0) - c1});
    }

    // O(logU) -- a[i] += v for i in [l, r]
    void rangeAdd(long long l, long long r, T v) { rangeAddArithSeq(l, r, v, 0); }

    // O(logU) -- a[i]
    T pointGet(long long i) const {
        F s = prefix(i - lo);
        return T(s[0] + s[1] * W(i - lo));
    }
''' + cp
    write(ops, ("c[2*log(U)] s[2*log(U)]", "links[4*log(U)]"), "an arithmetic-sequence add changes two points of c and s",
          py_class(name, AP_DESC.format(c="#", m=", all mod p" if mod else ""), ["c", "s"], "mod" if mod else "add", py_body),
          cpp_struct(name, AP_DESC.format(c="//", m=", all mod p" if mod else ""), 2, "mod" if mod else "add", cpp_body))

# ---------------------------------------------------------------- arithmetic-sequence add + range sum: P(x) = A + B x + C tri(x)

APSUM_DESC = ("Range add of an arithmetic sequence (and plain range add) + range sum{m}. Adding c0 + c1 * x (x = i - lo)\n"
              "{c} on [l, r] changes the prefix sum P(x) = a[lo] + ... + a[lo + x] by c0 * (x - l + 1) + c1 * (tri(x) - tri(l - 1))\n"
              "{c} for x in [l, r] (tri(k) = k(k+1)/2), and by the whole added total past r. So P(x) = A(x) + B(x) * x +\n"
              "{c} C(x) * tri(x) with A, B, C prefix sums of point changes; tri keeps every coefficient an integer.")
for mod in (False, True):
    sfx = "Mod" if mod else ""
    name = f"SparseArithSeqSumBIT{sfx}"
    ops = (MOD_POINT + ["rangeAddArithSeqMod", "rangeAddMod", "rangeSumMod"]) if mod else (
        PLAIN + ["rangeAdd", "rangeAddArithSeq", "rangeSum"])
    pp, cp = point_ops(f"rangeAdd{sfx}", chm=not mod)
    py_body = f'''
    # O(logU) -- a[l + j] += start + j * step{" (mod p)" if mod else ""} for j in [0, r - l]
    def rangeAddArithSeq{sfx}(self, l, r, start, step):
        if l > r:
            return
        l -= self.lo
        r -= self.lo
        c0, c1 = start - step * l, step  # adding c0 + c1 * x at offset x
        a = c0 * (1 - l) - c1 * _tri(l - 1)
        self._add(l, a, c0, c1)
        if r + 1 < self.n:
            total = c0 * (r - l + 1) + c1 * (_tri(r) - _tri(l - 1))
            self._add(r + 1, total - a, -c0, -c1)

    # O(logU) -- a[i] += v{" (mod p)" if mod else ""} for i in [l, r]
    def rangeAdd{sfx}(self, l, r, v):
        self.rangeAddArithSeq{sfx}(l, r, v, 0)

    # O(logU) -- a[lo] + ... + a[lo + x]{" mod p" if mod else ""} (0 for x = -1)
    def _sum(self, x):
        sa, sb, sc = self._prefix(x)
        return {"(sa + sb * x + sc * _tri(x)) % self.mod" if mod else "sa + sb * x + sc * _tri(x)"}

    # O(logU) -- a[l] + ... + a[r]{" mod p" if mod else ""}
    def rangeSum{sfx}(self, l, r):
        if l > r:
            return 0
        return {"(self._sum(r - self.lo) - self._sum(l - 1 - self.lo)) % self.mod" if mod else "self._sum(r - self.lo) - self._sum(l - 1 - self.lo)"}

    # O(logU) -- a[i]{", in [0, mod)" if mod else ""}
    def pointGet(self, i):
        return self.rangeSum{sfx}(i, i)
''' + pp
    if mod:
        cpp_body = '''
    T norm(W x) const { return T((x % mod + mod) % mod); }
    T tri(long long k) const { return norm(W((__int128)k * (k + 1) / 2 % mod)); }

    // O(logU) -- a[l + j] += start + j * step (mod p) for j in [0, r - l]
    void rangeAddArithSeqMod(long long l, long long r, T start, T step) {
        if (l > r) return;
        l -= lo, r -= lo;
        T c1 = norm(step), c0 = norm(W(start) - W(c1) * norm(l));  // adding c0 + c1 * x at offset x
        T a = norm(W(c0) * norm(1 - l) - W(c1) * tri(l - 1));
        add(l, F{a, c0, c1});
        if (r + 1 < n) {
            T total = norm(W(c0) * norm(r - l + 1) + W(c1) * norm(W(tri(r)) - tri(l - 1)));
            add(r + 1, F{norm(W(total) - a), norm(-W(c0)), norm(-W(c1))});
        }
    }

    // O(logU) -- a[i] += v (mod p) for i in [l, r]
    void rangeAddMod(long long l, long long r, T v) { rangeAddArithSeqMod(l, r, v, 0); }

    // O(logU) -- (a[lo] + ... + a[lo + x]) mod p (0 for x = -1)
    T sum(long long x) const {
        F s = prefix(x);
        return norm(s[0] + W(s[1]) * norm(x) % mod + W(s[2]) * tri(x) % mod);
    }

    // O(logU) -- (a[l] + ... + a[r]) mod p
    T rangeSumMod(long long l, long long r) const { return l <= r ? norm(W(sum(r - lo)) - sum(l - 1 - lo)) : T(0); }

    // O(logU) -- a[i], in [0, mod)
    T pointGet(long long i) const { return rangeSumMod(i, i); }
''' + cp
    else:
        cpp_body = '''
    // k(k+1)/2 mod 2^64, exact (halve the even factor first); tri(-1) = 0
    static W tri(long long k) {
        W a = W(k), b = W(k + 1);
        return a % 2 == 0 ? (a / 2) * b : a * (b / 2);
    }

    // O(logU) -- a[l + j] += start + j * step for j in [0, r - l]
    void rangeAddArithSeq(long long l, long long r, T start, T step) {
        if (l > r) return;
        l -= lo, r -= lo;
        W c1 = W(step), c0 = W(start) - c1 * W(l);  // adding c0 + c1 * x at offset x
        W a = c0 * W(1 - l) - c1 * tri(l - 1);
        add(l, F{a, c0, c1});
        if (r + 1 < n) {
            W total = c0 * W(r - l + 1) + c1 * (tri(r) - tri(l - 1));
            add(r + 1, F{total - a, W(0) - c0, W(0) - c1});
        }
    }

    // O(logU) -- a[i] += v for i in [l, r]
    void rangeAdd(long long l, long long r, T v) { rangeAddArithSeq(l, r, v, 0); }

    // O(logU) -- a[lo] + ... + a[lo + x] (0 for x = -1)
    W sum(long long x) const {
        F s = prefix(x);
        return s[0] + s[1] * W(x) + s[2] * tri(x);
    }

    // O(logU) -- a[l] + ... + a[r]
    long long rangeSum(long long l, long long r) const { return l <= r ? (long long)(sum(r - lo) - sum(l - 1 - lo)) : 0; }

    // O(logU) -- a[i]
    T pointGet(long long i) const { return T(rangeSum(i, i)); }
''' + cp
    write(ops, ("A[2*log(U)] B[2*log(U)] C[2*log(U)]", "links[4*log(U)]"),
          "an arithmetic-sequence add changes two points of A, B and C",
          "\n\ndef _tri(k):\n    return k * (k + 1) // 2\n" +
          py_class(name, APSUM_DESC.format(c="#", m=", all mod p" if mod else ""), ["A", "B", "C"], "mod" if mod else "add",
                   py_body),
          cpp_struct(name, APSUM_DESC.format(c="//", m=", all mod p" if mod else ""), 3, "mod" if mod else "add", cpp_body))

# ---------------------------------------------------------------- point add + range sum + prefix-sum searches

write(["leftmostPrefixSumGtX", "leftmostPrefixSumGteX", "pointAdd", "pointAssign", "pointChmax", "pointChmin", "pointGet",
       "rangeSum"], ("tree[1*log(U)]", "links[2*log(U)]"),
      "the prefix-sum searches need every a[i] >= 0; they return lo - 1 (-1 when lo = 0) when nothing qualifies",
      py_class("SparseBIT", "Point add, range sum, and the first index where a running sum from l reaches x.",
               ["tree"], "add", '''
    # O(logU) -- a[i] += delta
    def pointAdd(self, i, delta):
        self._add(i - self.lo, delta)

    # O(logU) -- a[l] + ... + a[r]
    def rangeSum(self, l, r):
        if l > r:
            return 0
        return self._prefix(r - self.lo) - self._prefix(l - 1 - self.lo)

    # O(logU) -- a[i]
    def pointGet(self, i):
        return self.rangeSum(i, i)

    # O(logU) -- a[i] = val
    def pointAssign(self, i, val):
        self._add(i - self.lo, val - self.pointGet(i))

    # O(logU) -- a[i] = max(a[i], val)
    def pointChmax(self, i, val):
        cur = self.pointGet(i)
        if val > cur:
            self._add(i - self.lo, val - cur)

    # O(logU) -- a[i] = min(a[i], val)
    def pointChmin(self, i, val):
        cur = self.pointGet(i)
        if val < cur:
            self._add(i - self.lo, val - cur)

    # O(logU) -- smallest offset x with prefix(x) >= target (> target if strict), or n. Binary lifting over the
    # Fenwick tree; needs every a[i] >= 0.
    def _lowerBound(self, target, strict):
        d, n = self.d, self.n
        pos = acc = 0
        step = 1 << (n.bit_length() - 1)
        while step:
            nxt = pos + step
            if nxt <= n:
                v = acc + d.get(nxt, 0)
                if v < target or (strict and v == target):
                    pos, acc = nxt, v
            step >>= 1
        return pos

    # O(logU) -- first i in [l, r] with a[l] + ... + a[i] >= x, or lo - 1. Needs every a[i] >= 0.
    def leftmostPrefixSumGteX(self, l, r, x):
        i = max(l, self.lo + self._lowerBound(self._prefix(l - 1 - self.lo) + x, False))
        return i if i <= r else self.lo - 1

    # O(logU) -- first i in [l, r] with a[l] + ... + a[i] > x, or lo - 1. Needs every a[i] >= 0.
    def leftmostPrefixSumGtX(self, l, r, x):
        i = max(l, self.lo + self._lowerBound(self._prefix(l - 1 - self.lo) + x, True))
        return i if i <= r else self.lo - 1
'''),
      cpp_struct("SparseBIT", "Point add, range sum, and the first index where a running sum from l reaches x.", 1, "sum", '''
    // O(logU) -- a[i] += delta
    void pointAdd(long long i, T delta) { add(i - lo, F{S(delta)}); }

    // O(logU) -- a[l] + ... + a[r]
    S rangeSum(long long l, long long r) const { return l <= r ? prefix(r - lo)[0] - prefix(l - 1 - lo)[0] : S(0); }

    // O(logU) -- a[i]
    T pointGet(long long i) const { return T(rangeSum(i, i)); }

    // O(logU) -- a[i] = v
    void pointAssign(long long i, T v) { pointAdd(i, v - pointGet(i)); }

    // O(logU) -- a[i] = max(a[i], v)
    void pointChmax(long long i, T v) { T cur = pointGet(i); if (v > cur) pointAdd(i, v - cur); }

    // O(logU) -- a[i] = min(a[i], v)
    void pointChmin(long long i, T v) { T cur = pointGet(i); if (v < cur) pointAdd(i, v - cur); }

    // O(logU) -- smallest offset x with prefix(x) >= target (> target if strict), or n. Needs every a[i] >= 0.
    long long lowerBound(S target, bool strict) const {
        auto reached = [&](S v) { return strict ? v > target : v >= target; };
        if (!reached(pool[root].f[0])) return n;
        int y = root;
        long long a = 0, b = n - 1;
        S acc = 0;
        while (a < b) {  // node 0 is a block of zeros: the answer is its first position
            long long m = a + (b - a) / 2;
            S left = acc + pool[pool[y].l].f[0];
            if (reached(left)) y = pool[y].l, b = m;
            else acc = left, y = pool[y].r, a = m + 1;
        }
        return a;
    }

    // O(logU) -- first i in [l, r] with a[l] + ... + a[i] >= x, or lo - 1. Needs every a[i] >= 0.
    long long leftmostPrefixSumGteX(long long l, long long r, T x) const {
        long long i = max(l, lo + lowerBound(prefix(l - 1 - lo)[0] + x, false));
        return i <= r ? i : lo - 1;
    }

    // O(logU) -- first i in [l, r] with a[l] + ... + a[i] > x, or lo - 1. Needs every a[i] >= 0.
    long long leftmostPrefixSumGtX(long long l, long long r, T x) const {
        long long i = max(l, lo + lowerBound(prefix(l - 1 - lo)[0] + x, true));
        return i <= r ? i : lo - 1;
    }
'''))