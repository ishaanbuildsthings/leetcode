"""Rectangle add with rectangle sums (true area sums), from corner marks:

    python3 gen_area.py     # writes range-queries-2d/online-rect-add-rect-sum and points-rect-add-rect-sum

A rect add of v on x1..x2 by y1..y2 is four point marks: +v at (x1, y1), -v at (x2 + 1, y1), -v at (x1, y2 + 1), +v at
(x2 + 1, y2 + 1). The sum of the cells with x <= X and y <= Y is then, over the marks (x, y, d) with x <= X and y <= Y,
d * (X - x + 1) * (Y - y + 1) = (X + 1)(Y + 1) * sum d - (Y + 1) * sum d*x - (X + 1) * sum d*y + sum d*x*y, so four
dominance sums answer it. The online version keeps them in a dynamic tree of trees over the range; the points version
in a Fenwick tree over the marks' x's whose every node is a Fenwick tree over just its own y's (the update rectangles
are listed up front, so the marks are known).
"""
from lib2d import header, wrap_comment, write

SUM_FORMULA = "(X + 1) * (Y + 1) * a - (Y + 1) * b - (X + 1) * c + e"

# ------------------------------------------------------------------------------------------------ online
ONLINE_DOC = ("Rectangle add and rectangle sum over a huge coordinate range, nothing known up front: O(log^2 U) per "
              "operation, and up to about 4 log^2 U new nodes per rectAdd. A rect add is four point marks at its corners "
              "(+v, -v, -v, +v), and the sum of the cells with x <= X and y <= Y comes from four sums over the marks below "
              "and left of (X, Y): of d, d * x, d * y and d * x * y, which a dynamic tree over x whose every node owns a "
              "dynamic tree over y keeps (coordinates are counted from xLo and yLo). Every cell starts at 0, and sums are "
              "true area sums: a rect add of v on a 3 by 4 rectangle adds 12 * v.")

ONLINE_PY = '''
# @DOC@
class OnlineRectAddRectSum2D:
    __slots__ = ("xLo", "xHi", "yLo", "yHi", "W", "H", "xLeft", "xRight", "xTree", "yLeft", "yRight", "s0", "sx", "sy", "sxy", "total")

    # O(1) -- every cell of [xLo, xHi] by [yLo, yHi] starts at 0; needs xLo <= xHi and yLo <= yHi, else ValueError
    def __init__(self, xLo, xHi, yLo, yHi):
        if xLo > xHi or yLo > yHi:
            raise ValueError(f"OnlineRectAddRectSum2D: needs xLo <= xHi and yLo <= yHi, got xLo = {xLo}, xHi = {xHi}, "
                             f"yLo = {yLo}, yHi = {yHi}")
        self.xLo, self.xHi, self.yLo, self.yHi = xLo, xHi, yLo, yHi
        self.W = xHi - xLo  # (marks sit at 0..W by 0..H, counted from xLo and yLo)
        self.H = yHi - yLo
        self.xLeft = [0, 0]  # x-node 0 = nothing there, x-node 1 = the root
        self.xRight = [0, 0]
        self.xTree = [0, 0]  # an x-node's own y-tree (its root, 0 = none yet)
        self.yLeft = [0]  # y-node 0 = nothing there
        self.yRight = [0]
        self.s0 = [0]  # per y-node: the sums of d, d * x, d * y, d * x * y over the marks below it
        self.sx = [0]
        self.sy = [0]
        self.sxy = [0]
        self.total = 0

    def _newY(self):
        self.yLeft.append(0)
        self.yRight.append(0)
        self.s0.append(0)
        self.sx.append(0)
        self.sy.append(0)
        self.sxy.append(0)
        return len(self.s0) - 1

    # a mark of d at (x, y), counted from (xLo, yLo)
    def _mark(self, x, y, d):
        xLeft, xRight, xTree = self.xLeft, self.xRight, self.xTree
        yLeft, yRight, s0, sx, sy, sxy = self.yLeft, self.yRight, self.s0, self.sx, self.sy, self.sxy
        dx = d * x
        dy = d * y
        dxy = dx * y
        p, lo, hi = 1, 0, self.W
        while True:
            if not xTree[p]:
                xTree[p] = self._newY()
            q, ylo, yhi = xTree[p], 0, self.H
            while True:
                s0[q] += d
                sx[q] += dx
                sy[q] += dy
                sxy[q] += dxy
                if ylo == yhi:
                    break
                mid = (ylo + yhi) >> 1
                if y <= mid:
                    if not yLeft[q]:
                        yLeft[q] = self._newY()
                    q, yhi = yLeft[q], mid
                else:
                    if not yRight[q]:
                        yRight[q] = self._newY()
                    q, ylo = yRight[q], mid + 1
            if lo == hi:
                break
            mid = (lo + hi) >> 1
            side = xLeft if x <= mid else xRight
            if not side[p]:
                side[p] = len(xTree)
                xLeft.append(0)
                xRight.append(0)
                xTree.append(0)
            if x <= mid:
                p, hi = side[p], mid
            else:
                p, lo = side[p], mid + 1

    # the sum of the cells with x <= X and y <= Y, counted from (xLo, yLo) (X, Y in -1..W, -1..H)
    def _prefix(self, X, Y):
        if X < 0 or Y < 0:
            return 0
        xLeft, xRight, xTree = self.xLeft, self.xRight, self.xTree
        yLeft, yRight, s0, sx, sy, sxy = self.yLeft, self.yRight, self.s0, self.sx, self.sy, self.sxy
        a = b = c = e = 0
        whole = []  # the x-nodes that make up 0..X
        p, lo, hi = 1, 0, self.W
        while p:
            if hi <= X:
                whole.append(p)
                break
            mid = (lo + hi) >> 1
            if X <= mid:
                p, hi = xLeft[p], mid
            else:
                if xLeft[p]:
                    whole.append(xLeft[p])
                p, lo = xRight[p], mid + 1
        for p in whole:
            q, ylo, yhi = xTree[p], 0, self.H
            while q:
                if yhi <= Y:
                    a += s0[q]
                    b += sx[q]
                    c += sy[q]
                    e += sxy[q]
                    break
                mid = (ylo + yhi) >> 1
                if Y <= mid:
                    q, yhi = yLeft[q], mid
                else:
                    k = yLeft[q]
                    if k:
                        a += s0[k]
                        b += sx[k]
                        c += sy[k]
                        e += sxy[k]
                    q, ylo = yRight[q], mid + 1
        return @FORMULA@

    def _add(self, x1, y1, x2, y2, v):
        self.total += v * (x2 - x1 + 1) * (y2 - y1 + 1)
        a, b = x1 - self.xLo, x2 - self.xLo + 1
        c, e = y1 - self.yLo, y2 - self.yLo + 1
        self._mark(a, c, v)
        if b <= self.W:  # (a mark past the range never reaches a query)
            self._mark(b, c, -v)
        if e <= self.H:
            self._mark(a, e, -v)
        if b <= self.W and e <= self.H:
            self._mark(b, e, v)

    def _sum(self, x1, y1, x2, y2):
        a, b = x1 - self.xLo - 1, x2 - self.xLo
        c, e = y1 - self.yLo - 1, y2 - self.yLo
        return self._prefix(b, e) - self._prefix(a, e) - self._prefix(b, c) + self._prefix(a, c)

    # O(log^2 U) -- adds v to every cell with x1 <= x <= x2 and y1 <= y <= y2; @RECT_RULE@
    def rectAdd(self, x1, y1, x2, y2, v):
@RECT_CHECK_rectAdd@
        self._add(x1, y1, x2, y2, v)

    # O(log^2 U) -- adds v to the cell (x, y); @POINT_RULE@
    def pointAdd(self, x, y, v):
@POINT_CHECK_pointAdd@
        self._add(x, y, x, y, v)

    # O(log^2 U) -- the value at (x, y); @POINT_RULE@
    def pointGet(self, x, y):
@POINT_CHECK_pointGet@
        return self._sum(x, y, x, y)

    # O(log^2 U) -- sum of the cells with x1 <= x <= x2 and y1 <= y <= y2; @RECT_RULE@
    def rectSum(self, x1, y1, x2, y2):
@RECT_CHECK_rectSum@
        return self._sum(x1, y1, x2, y2)

    # O(1) -- sum of every cell
    def sumAll(self):
        return self.total
@CORNERS@'''

ONLINE_CPP = '''
// @DOC@
// T is any integer type (int, long long, ...); the four sums are kept in __int128, so coordinates up to about 10^9 apart
// and values up to about 10^9 are fine, as long as every answer fits in T. Coordinates are long long.
template <typename T>
struct OnlineRectAddRectSum2D {
    using ll = long long;
    using L = __int128;
    ll xLo, xHi, yLo, yHi, W, H;  // (marks sit at 0..W by 0..H, counted from xLo and yLo)
    int xUsed = 2, yUsed = 1;  // how many x-nodes / y-nodes exist (the arrays are longer: they double when full)
    vector<int> xLeft, xRight, xTree;  // x-node 0 = nothing there, 1 = the root; xTree = its own y-tree's root (0 = none)
    vector<int> yLeft, yRight;  // y-node 0 = nothing there
    vector<array<L, 4>> s;  // per y-node: the sums of d, d * x, d * y, d * x * y over the marks below it
    L total = 0;

    // O(1) -- every cell of [xLo, xHi] by [yLo, yHi] starts at 0; needs xLo <= xHi and yLo <= yHi, else throws
    // invalid_argument
    OnlineRectAddRectSum2D(ll xLo, ll xHi, ll yLo, ll yHi)
        : xLo(xLo), xHi(xHi), yLo(yLo), yHi(yHi), W(xHi - xLo), H(yHi - yLo),
          xLeft(64, 0), xRight(64, 0), xTree(64, 0) {
        if (xLo > xHi || yLo > yHi) throw invalid_argument("OnlineRectAddRectSum2D: needs xLo <= xHi and yLo <= yHi");
        yLeft.assign(64, 0), yRight.assign(64, 0), s.assign(64, array<L, 4>{0, 0, 0, 0});
    }

    // a new node is the next unused slot (already blank); a full array doubles
    int newX() {
        if (xUsed == (int)xLeft.size())
            xLeft.resize(2 * xUsed, 0), xRight.resize(2 * xUsed, 0), xTree.resize(2 * xUsed, 0);
        return xUsed++;
    }

    int newY() {
        if (yUsed == (int)yLeft.size()) {
            size_t n = 2 * (size_t)yUsed;
            yLeft.resize(n, 0), yRight.resize(n, 0), s.resize(n, array<L, 4>{0, 0, 0, 0});
        }
        return yUsed++;
    }

    // a mark of d at (x, y), counted from (xLo, yLo)
    void mark(ll x, ll y, L d) {
        L dx = d * x, dy = d * y, dxy = dx * y;
        int p = 1;
        for (ll lo = 0, hi = W;;) {
            if (!xTree[p]) { int made = newY(); xTree[p] = made; }
            int q = xTree[p];
            for (ll ylo = 0, yhi = H;;) {
                s[q][0] += d, s[q][1] += dx, s[q][2] += dy, s[q][3] += dxy;
                if (ylo == yhi) break;
                ll mid = ylo + (yhi - ylo) / 2;
                if (y <= mid) {
                    if (!yLeft[q]) { int made = newY(); yLeft[q] = made; }
                    q = yLeft[q], yhi = mid;
                } else {
                    if (!yRight[q]) { int made = newY(); yRight[q] = made; }
                    q = yRight[q], ylo = mid + 1;
                }
            }
            if (lo == hi) break;
            ll mid = lo + (hi - lo) / 2;
            if (x <= mid) {
                if (!xLeft[p]) { int made = newX(); xLeft[p] = made; }
                p = xLeft[p], hi = mid;
            } else {
                if (!xRight[p]) { int made = newX(); xRight[p] = made; }
                p = xRight[p], lo = mid + 1;
            }
        }
    }

    // the y-tree rooted at q: adds its sums over y <= Y to acc
    void colsPrefix(int q, ll Y, array<L, 4>& acc) const {
        for (ll ylo = 0, yhi = H; q;) {
            if (yhi <= Y) {
                for (int i = 0; i < 4; i++) acc[i] += s[q][i];
                return;
            }
            ll mid = ylo + (yhi - ylo) / 2;
            if (Y <= mid) q = yLeft[q], yhi = mid;
            else {
                if (yLeft[q])
                    for (int i = 0; i < 4; i++) acc[i] += s[yLeft[q]][i];
                q = yRight[q], ylo = mid + 1;
            }
        }
    }

    // the sum of the cells with x <= X and y <= Y, counted from (xLo, yLo) (X, Y in -1..W, -1..H)
    L prefix(ll X, ll Y) const {
        if (X < 0 || Y < 0) return 0;
        array<L, 4> acc{0, 0, 0, 0};
        int p = 1;
        for (ll lo = 0, hi = W; p;) {
            if (hi <= X) {
                colsPrefix(xTree[p], Y, acc);
                break;
            }
            ll mid = lo + (hi - lo) / 2;
            if (X <= mid) p = xLeft[p], hi = mid;
            else {
                if (xLeft[p]) colsPrefix(xTree[xLeft[p]], Y, acc);
                p = xRight[p], lo = mid + 1;
            }
        }
        L a = acc[0], b = acc[1], c = acc[2], e = acc[3];
        return (L)(X + 1) * (Y + 1) * a - (L)(Y + 1) * b - (L)(X + 1) * c + e;
    }

    void add(ll x1, ll y1, ll x2, ll y2, T v) {
        total += (L)v * (x2 - x1 + 1) * (y2 - y1 + 1);
        ll a = x1 - xLo, b = x2 - xLo + 1, c = y1 - yLo, e = y2 - yLo + 1;
        mark(a, c, v);
        if (b <= W) mark(b, c, -(L)v);  // (a mark past the range never reaches a query)
        if (e <= H) mark(a, e, -(L)v);
        if (b <= W && e <= H) mark(b, e, v);
    }

    L sumOf(ll x1, ll y1, ll x2, ll y2) const {
        ll a = x1 - xLo - 1, b = x2 - xLo, c = y1 - yLo - 1, e = y2 - yLo;
        return prefix(b, e) - prefix(a, e) - prefix(b, c) + prefix(a, c);
    }

    // O(log^2 U) -- adds v to every cell with x1 <= x <= x2 and y1 <= y <= y2; @RECT_RULE@
    void rectAdd(ll x1, ll y1, ll x2, ll y2, T v) {
@RECT_CHECK_rectAdd@
        add(x1, y1, x2, y2, v);
    }

    // O(log^2 U) -- adds v to the cell (x, y); @POINT_RULE@
    void pointAdd(ll x, ll y, T v) {
@POINT_CHECK_pointAdd@
        add(x, y, x, y, v);
    }

    // O(log^2 U) -- the value at (x, y); @POINT_RULE@
    T pointGet(ll x, ll y) const {
@POINT_CHECK_pointGet@
        return (T)sumOf(x, y, x, y);
    }

    // O(log^2 U) -- sum of the cells with x1 <= x <= x2 and y1 <= y <= y2; @RECT_RULE@
    T rectSum(ll x1, ll y1, ll x2, ll y2) const {
@RECT_CHECK_rectSum@
        return (T)sumOf(x1, y1, x2, y2);
    }

    // O(1) -- sum of every cell
    T sumAll() const { return (T)total; }
@CORNERS@};
'''

ONLINE_CORNERS_PY = {  # (offsets: x' = x - xLo, y' = y - yLo)
    "LteLte": "self._prefix(x, y)",
    "LteGte": "self._prefix(x, self.H) - self._prefix(x, y - 1)",
    "GteLte": "self._prefix(self.W, y) - self._prefix(x - 1, y)",
    "GteGte": "self.total - self._prefix(x - 1, self.H) - self._prefix(self.W, y - 1) + self._prefix(x - 1, y - 1)",
}
ONLINE_CORNERS_CPP = {
    "LteLte": "prefix(x, y)",
    "LteGte": "prefix(x, H) - prefix(x, y - 1)",
    "GteLte": "prefix(W, y) - prefix(x - 1, y)",
    "GteGte": "total - prefix(x - 1, H) - prefix(W, y - 1) + prefix(x - 1, y - 1)",
}

# ------------------------------------------------------------------------------------------------ points
POINTS_DOC = ("Rectangle add and rectangle sum where the update rectangles are listed up front, any integers (negative is "
              "fine): O(log^2 N) per operation with N log N memory, N = how many rectangles. A rect add is four point "
              "marks at its corners (+v, -v, -v, +v), and the sum of the cells with x <= X and y <= Y comes from four "
              "sums over the marks below and left of (X, Y): of d, d * x, d * y and d * x * y. Those are point updates at "
              "known places, so a Fenwick tree over the marks' x's whose every node is a Fenwick tree over just its own "
              "y's keeps them. The constructor takes every rectangle a rectAdd will use (a pointAdd is the rectangle "
              "(x, y, x, y)); queries take any integers, never listed. Every cell starts at 0, and sums are true area "
              "sums: a rect add of v on a 3 by 4 rectangle adds 12 * v.")

POINTS_PY = '''
from bisect import bisect_left, bisect_right


# @DOC@
class PointsRectAddRectSum2D:
    __slots__ = ("rects", "xs", "ys", "off", "cnt", "s0", "sx", "sy", "sxy", "maxX", "maxY", "total")

    # O(N log N) -- rects: every (x1, y1, x2, y2) a rectAdd will use, x1 <= x2 and y1 <= y2 (a pointAdd at (x, y) needs
    # (x, y, x, y)); repeats are fine; queries are never listed. Needs at least one, else ValueError
    def __init__(self, rects):
        rects = self.rects = set(map(tuple, rects))
        if not rects:
            raise ValueError("PointsRectAddRectSum2D: needs at least one rectangle")
        if any(x1 > x2 or y1 > y2 for x1, y1, x2, y2 in rects):
            raise ValueError("PointsRectAddRectSum2D: needs x1 <= x2 and y1 <= y2 in every rectangle")
        marks = set()
        for x1, y1, x2, y2 in rects:
            marks.update(((x1, y1), (x2 + 1, y1), (x1, y2 + 1), (x2 + 1, y2 + 1)))
        xs = self.xs = sorted({x for x, _ in marks})
        n = len(xs)
        self.maxX = xs[-1]  # (past the last mark, a prefix sum stops changing)
        self.maxY = max(y for _, y in marks)
        lists = [[] for _ in range(n + 1)]  # per Fenwick x-node: the distinct y's it covers, ascending
        for x, y in sorted(marks, key=lambda m: m[1]):
            i = bisect_left(xs, x) + 1
            while i <= n:
                lst = lists[i]
                if not lst or lst[-1] != y:
                    lst.append(y)
                i += i & -i
        off = self.off = [0] * (n + 1)
        cnt = self.cnt = [0] * (n + 1)
        ys = self.ys = []
        for i in range(1, n + 1):
            off[i] = len(ys)
            cnt[i] = len(lists[i])
            ys += lists[i]
        self.s0 = [0] * len(ys)  # the sums of d, d * x, d * y, d * x * y, Fenwick-style per x-node
        self.sx = [0] * len(ys)
        self.sy = [0] * len(ys)
        self.sxy = [0] * len(ys)
        self.total = 0

    def _mark(self, x, y, d):
        xs, ys, off, cnt = self.xs, self.ys, self.off, self.cnt
        s0, sx, sy, sxy = self.s0, self.sx, self.sy, self.sxy
        dx = d * x
        dy = d * y
        dxy = dx * y
        n = len(xs)
        i = bisect_left(xs, x) + 1
        while i <= n:
            o = off[i]
            c = cnt[i]
            k = bisect_left(ys, y, o, o + c) - o + 1
            o -= 1
            while k <= c:
                s0[o + k] += d
                sx[o + k] += dx
                sy[o + k] += dy
                sxy[o + k] += dxy
                k += k & -k
            i += i & -i

    # the sum of the cells with x <= X and y <= Y (any integers)
    def _prefix(self, X, Y):
        if X > self.maxX:
            X = self.maxX
        if Y > self.maxY:
            Y = self.maxY
        xs, ys, off, cnt = self.xs, self.ys, self.off, self.cnt
        s0, sx, sy, sxy = self.s0, self.sx, self.sy, self.sxy
        a = b = c = e = 0
        i = bisect_right(xs, X)
        while i > 0:
            o = off[i]
            k = bisect_right(ys, Y, o, o + cnt[i]) - o
            o -= 1
            while k > 0:
                a += s0[o + k]
                b += sx[o + k]
                c += sy[o + k]
                e += sxy[o + k]
                k &= k - 1
            i &= i - 1
        return @FORMULA@

    def _add(self, x1, y1, x2, y2, v, name):
        if (x1, y1, x2, y2) not in self.rects:
            raise IndexError(f"{name}: ({x1}, {y1}, {x2}, {y2}) is not one of the rectangles given to the constructor")
        self.total += v * (x2 - x1 + 1) * (y2 - y1 + 1)
        self._mark(x1, y1, v)
        self._mark(x2 + 1, y1, -v)
        self._mark(x1, y2 + 1, -v)
        self._mark(x2 + 1, y2 + 1, v)

    def _sum(self, x1, y1, x2, y2):
        return self._prefix(x2, y2) - self._prefix(x1 - 1, y2) - self._prefix(x2, y1 - 1) + self._prefix(x1 - 1, y1 - 1)

    # O(log^2 N) -- adds v to every cell with x1 <= x <= x2 and y1 <= y <= y2; needs (x1, y1, x2, y2) to be one of the
    # rectangles given, else IndexError
    def rectAdd(self, x1, y1, x2, y2, v):
        self._add(x1, y1, x2, y2, v, "rectAdd")

    # O(log^2 N) -- adds v to the cell (x, y); needs (x, y, x, y) to be one of the rectangles given, else IndexError
    def pointAdd(self, x, y, v):
        self._add(x, y, x, y, v, "pointAdd")

    # O(log^2 N) -- the value at (x, y); any integers
    def pointGet(self, x, y):
        return self._sum(x, y, x, y)

    # O(log^2 N) -- sum of the cells with x1 <= x <= x2 and y1 <= y <= y2; any integers, needs x1 <= x2 and y1 <= y2,
    # else IndexError
    def rectSum(self, x1, y1, x2, y2):
        if x1 > x2 or y1 > y2:
            raise IndexError(f"rectSum: needs x1 <= x2 and y1 <= y2, got x1 = {x1}, y1 = {y1}, x2 = {x2}, y2 = {y2}")
        return self._sum(x1, y1, x2, y2)

    # O(1) -- sum of every cell
    def sumAll(self):
        return self.total
@CORNERS@'''

POINTS_CPP = '''
// @DOC@
// T is any integer type (int, long long, ...); the four sums are kept in __int128, so coordinates up to about 10^9 and
// values up to about 10^9 are fine, as long as every answer fits in T. Coordinates are long long.
template <typename T>
struct PointsRectAddRectSum2D {
    using ll = long long;
    using L = __int128;
    vector<array<ll, 4>> rects;  // the rectangles given, sorted, each once
    vector<ll> xs, ys;  // the marks' distinct x's; per Fenwick x-node, the distinct y's it covers (off / cnt locate them)
    vector<int> off, cnt;
    vector<array<L, 4>> s;  // the sums of d, d * x, d * y, d * x * y, Fenwick-style per x-node
    ll maxX, maxY;  // (past the last mark, a prefix sum stops changing)
    L total = 0;

    // O(N log N) -- rects: every {x1, y1, x2, y2} a rectAdd will use, x1 <= x2 and y1 <= y2 (a pointAdd at (x, y) needs
    // {x, y, x, y}); repeats are fine; queries are never listed. Needs at least one, else throws invalid_argument
    explicit PointsRectAddRectSum2D(vector<array<ll, 4>> rs) : rects(std::move(rs)) {
        if (rects.empty()) throw invalid_argument("PointsRectAddRectSum2D: needs at least one rectangle");
        sort(rects.begin(), rects.end());
        rects.erase(unique(rects.begin(), rects.end()), rects.end());
        vector<pair<ll, ll>> marks;  // (y, x), to visit them by y
        for (auto& r : rects) {
            if (r[0] > r[2] || r[1] > r[3]) throw invalid_argument("PointsRectAddRectSum2D: needs x1 <= x2 and y1 <= y2");
            marks.push_back({r[1], r[0]}), marks.push_back({r[1], r[2] + 1});
            marks.push_back({r[3] + 1, r[0]}), marks.push_back({r[3] + 1, r[2] + 1});
        }
        sort(marks.begin(), marks.end());
        marks.erase(unique(marks.begin(), marks.end()), marks.end());
        for (auto& m : marks) xs.push_back(m.second);
        sort(xs.begin(), xs.end());
        xs.erase(unique(xs.begin(), xs.end()), xs.end());
        maxX = xs.back(), maxY = marks.back().first;
        int n = (int)xs.size();
        vector<vector<ll>> lists(n + 1);
        for (auto& [y, x] : marks)
            for (int i = int(lower_bound(xs.begin(), xs.end(), x) - xs.begin()) + 1; i <= n; i += i & -i)
                if (lists[i].empty() || lists[i].back() != y) lists[i].push_back(y);
        off.assign(n + 1, 0), cnt.assign(n + 1, 0);
        for (int i = 1; i <= n; i++) {
            off[i] = (int)ys.size(), cnt[i] = (int)lists[i].size();
            ys.insert(ys.end(), lists[i].begin(), lists[i].end());
        }
        s.assign(ys.size(), array<L, 4>{0, 0, 0, 0});
    }

    void mark(ll x, ll y, L d) {
        L dx = d * x, dy = d * y, dxy = dx * y;
        int n = (int)xs.size();
        for (int i = int(lower_bound(xs.begin(), xs.end(), x) - xs.begin()) + 1; i <= n; i += i & -i) {
            const ll* base = ys.data() + off[i];
            int c = cnt[i];
            array<L, 4>* t = s.data() + off[i] - 1;
            for (int k = int(lower_bound(base, base + c, y) - base) + 1; k <= c; k += k & -k)
                t[k][0] += d, t[k][1] += dx, t[k][2] += dy, t[k][3] += dxy;
        }
    }

    // the sum of the cells with x <= X and y <= Y (any integers)
    L prefix(ll X, ll Y) const {
        if (X > maxX) X = maxX;
        if (Y > maxY) Y = maxY;
        L a = 0, b = 0, c = 0, e = 0;
        for (int i = int(upper_bound(xs.begin(), xs.end(), X) - xs.begin()); i > 0; i &= i - 1) {
            const ll* base = ys.data() + off[i];
            const array<L, 4>* t = s.data() + off[i] - 1;
            for (int k = int(upper_bound(base, base + cnt[i], Y) - base); k > 0; k &= k - 1)
                a += t[k][0], b += t[k][1], c += t[k][2], e += t[k][3];
        }
        return (L)(X + 1) * (Y + 1) * a - (L)(Y + 1) * b - (L)(X + 1) * c + e;
    }

    void add(ll x1, ll y1, ll x2, ll y2, T v, const char* name) {
        if (!binary_search(rects.begin(), rects.end(), array<ll, 4>{x1, y1, x2, y2}))
            throw out_of_range(string(name) + ": the rectangle is not one of the rectangles given to the constructor");
        total += (L)v * (x2 - x1 + 1) * (y2 - y1 + 1);
        mark(x1, y1, v), mark(x2 + 1, y1, -(L)v), mark(x1, y2 + 1, -(L)v), mark(x2 + 1, y2 + 1, v);
    }

    L sumOf(ll x1, ll y1, ll x2, ll y2) const {
        return prefix(x2, y2) - prefix(x1 - 1, y2) - prefix(x2, y1 - 1) + prefix(x1 - 1, y1 - 1);
    }

    // O(log^2 N) -- adds v to every cell with x1 <= x <= x2 and y1 <= y <= y2; needs {x1, y1, x2, y2} to be one of the
    // rectangles given, else throws out_of_range
    void rectAdd(ll x1, ll y1, ll x2, ll y2, T v) { add(x1, y1, x2, y2, v, "rectAdd"); }

    // O(log^2 N) -- adds v to the cell (x, y); needs {x, y, x, y} to be one of the rectangles given, else throws
    // out_of_range
    void pointAdd(ll x, ll y, T v) { add(x, y, x, y, v, "pointAdd"); }

    // O(log^2 N) -- the value at (x, y); any integers
    T pointGet(ll x, ll y) const { return (T)sumOf(x, y, x, y); }

    // O(log^2 N) -- sum of the cells with x1 <= x <= x2 and y1 <= y <= y2; any integers, needs x1 <= x2 and y1 <= y2,
    // else throws out_of_range
    T rectSum(ll x1, ll y1, ll x2, ll y2) const {
        if (x1 > x2 || y1 > y2) throw out_of_range("rectSum: needs x1 <= x2 and y1 <= y2");
        return (T)sumOf(x1, y1, x2, y2);
    }

    // O(1) -- sum of every cell
    T sumAll() const { return (T)total; }
@CORNERS@};
'''

POINTS_CORNERS_PY = {
    "LteLte": "self._prefix(x, y)",
    "LteGte": "self._prefix(x, self.maxY) - self._prefix(x, y - 1)",
    "GteLte": "self._prefix(self.maxX, y) - self._prefix(x - 1, y)",
    "GteGte": "self.total - self._prefix(x - 1, self.maxY) - self._prefix(self.maxX, y - 1) + self._prefix(x - 1, y - 1)",
}
POINTS_CORNERS_CPP = {
    "LteLte": "prefix(x, y)",
    "LteGte": "prefix(x, maxY) - prefix(x, y - 1)",
    "GteLte": "prefix(maxX, y) - prefix(x - 1, y)",
    "GteGte": "total - prefix(x - 1, maxY) - prefix(maxX, y - 1) + prefix(x - 1, y - 1)",
}
SIDES = {"Lte": "<=", "Gte": ">="}
POINT_RULE = "needs xLo <= x <= xHi and yLo <= y <= yHi, else {err}"
RECT_RULE = "needs xLo <= x1 <= x2 <= xHi and yLo <= y1 <= y2 <= yHi, else {err}"


def lines(text, doc, cm):
    out = []
    for line in text.strip("\n").split("\n"):
        out += wrap_comment(doc, cm) if line.strip() == f"{cm} @DOC@" else [line]
    return out


def checks(text, lang):
    for op in ("rectAdd", "rectSum"):
        if lang == "py":
            chk = (f"        if not (self.xLo <= x1 <= x2 <= self.xHi and self.yLo <= y1 <= y2 <= self.yHi):\n"
                   f'            raise IndexError(f"{op}: needs xLo <= x1 <= x2 <= xHi and yLo <= y1 <= y2 <= yHi, got x1 = '
                   f'{{x1}}, "\n                             f"y1 = {{y1}}, x2 = {{x2}}, y2 = {{y2}}")')
        else:
            chk = (f"        if (x1 < xLo || x1 > x2 || x2 > xHi || y1 < yLo || y1 > y2 || y2 > yHi)\n"
                   f'            throw out_of_range("{op}: needs xLo <= x1 <= x2 <= xHi and yLo <= y1 <= y2 <= yHi");')
        text = text.replace(f"@RECT_CHECK_{op}@", chk)
    for op in ("pointAdd", "pointGet") + tuple(f"sum{c}" for c in ONLINE_CORNERS_PY):
        if lang == "py":
            chk = (f"        if not (self.xLo <= x <= self.xHi and self.yLo <= y <= self.yHi):\n"
                   f'            raise IndexError(f"{op}: needs xLo <= x <= xHi and yLo <= y <= yHi, got x = {{x}}, y = {{y}}")')
        else:
            chk = (f"        if (x < xLo || x > xHi || y < yLo || y > yHi)\n"
                   f'            throw out_of_range("{op}: needs xLo <= x <= xHi and yLo <= y <= yHi");')
        text = text.replace(f"@POINT_CHECK_{op}@", chk)
    err = "IndexError" if lang == "py" else "throws out_of_range"
    return text.replace("@RECT_RULE@", RECT_RULE.format(err=err)).replace("@POINT_RULE@", POINT_RULE.format(err=err))


def online():
    pyc, cppc = [], []
    for name, expr in ONLINE_CORNERS_PY.items():
        a, b = name[:3], name[3:]
        what = f"sum of the cells with x {SIDES[a]} the given x and y {SIDES[b]} the given y"
        pyc += ["", f"    # O(log^2 U) -- {what}; @POINT_RULE@", f"    def sum{name}(self, x, y):", f"@POINT_CHECK_sum{name}@",
                "        x -= self.xLo", "        y -= self.yLo", f"        return {expr}"]
        cppc += ["", f"    // O(log^2 U) -- {what}; @POINT_RULE@", f"    T sum{name}(ll x, ll y) const {{", f"@POINT_CHECK_sum{name}@",
                 "        x -= xLo, y -= yLo;", f"        return (T)({ONLINE_CORNERS_CPP[name]});", "    }"]
    py = checks(ONLINE_PY.replace("@FORMULA@", SUM_FORMULA).replace("@CORNERS@", "\n".join(pyc)), "py")
    cpp = checks(ONLINE_CPP.replace("@CORNERS@", "\n".join(cppc) + "\n"), "cpp")
    ops = ["rectAdd", "pointAdd", "pointGet", "rectSum", "sumAll"] + [f"sum{c}" for c in ONLINE_CORNERS_PY]
    costs = {op: "log^2(U)" for op in ops}
    costs["sumAll"] = "1"
    memory = {"layout": "sparse", "node": "s0[4*log^2(U)] sx[4*log^2(U)] sy[4*log^2(U)] sxy[4*log^2(U)]", "tags": "none",
              "other": "yLeft[4*log^2(U)] yRight[4*log^2(U)] xLeft[4*log(U)] xRight[4*log(U)] xTree[4*log(U)]",
              "note": "sizes are per update: a rect add is up to four marks, each making up to about log U x-nodes and "
                      "log U y-nodes under each"}
    folder = "online-rect-add-rect-sum"
    args = (ops, "BIT", costs, "1", memory, "online", [("model", "area")])
    write(folder, header(folder, "py", *args) + [""] + lines(py, ONLINE_DOC, "#"),
          header(folder, "cpp", *args) + [""] + lines(cpp, ONLINE_DOC, "//"))


def points():
    pyc, cppc = [], []
    for name, expr in POINTS_CORNERS_PY.items():
        a, b = name[:3], name[3:]
        what = f"sum of the cells with x {SIDES[a]} the given x and y {SIDES[b]} the given y; any integers"
        pyc += ["", f"    # O(log^2 N) -- {what}", f"    def sum{name}(self, x, y):", f"        return {expr}"]
        cppc += ["", f"    // O(log^2 N) -- {what}", f"    T sum{name}(ll x, ll y) const {{",
                 f"        return (T)({POINTS_CORNERS_CPP[name]});", "    }"]
    py = POINTS_PY.replace("@FORMULA@", SUM_FORMULA).replace("@CORNERS@", "\n".join(pyc))
    cpp = POINTS_CPP.replace("@CORNERS@", "\n".join(cppc) + "\n")
    ops = ["rectAdd", "pointAdd", "pointGet", "rectSum", "sumAll"] + [f"sum{c}" for c in POINTS_CORNERS_PY]
    costs = {op: "log^2(N)" for op in ops}
    costs["sumAll"] = "1"
    memory = {"layout": "none", "node": "s0[4*N*log(N)] sx[4*N*log(N)] sy[4*N*log(N)] sxy[4*N*log(N)]", "tags": "none",
              "other": "ys[4*N*log(N)] xs[4*N] off[4*N] cnt[4*N] rects[4*N]",
              "note": "N = how many rectangles; each makes four corner marks, and every mark's y is listed in each of the "
                      "O(log N) Fenwick x-nodes covering it"}
    folder = "points-rect-add-rect-sum"
    args = (ops, "BIT", costs, "N*log(N)", memory, "points", [("model", "area")])
    write(folder, header(folder, "py", *args) + [""] + lines(py, POINTS_DOC, "#"),
          header(folder, "cpp", *args) + [""] + lines(cpp, POINTS_DOC, "//"))


def main():
    online()
    points()
    print("area: 2 folders")


if __name__ == "__main__":
    main()
