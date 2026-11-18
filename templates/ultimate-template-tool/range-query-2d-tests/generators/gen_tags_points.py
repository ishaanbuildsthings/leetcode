"""Coordinates up front or online, rectangle chmax with point reads (and chmin): a tree of trees whose tags stay put.

    python3 gen_tags_points.py     # writes range-queries-2d/{points,online}-kept-tags-<max|min>/template.{py,cpp}

A rectangle chmax is stored at the O(log^2) nodes that make up the rectangle and never pushed down (a tree of trees
can't push down its outer tree, and chmax doesn't need it); a point read collects the tags on its O(log^2) nodes. This
covers rectChmax + pointGet. Rectangle chmax together with rectangle max over sparse points is the k-d tree's (no
log^2 structure: the tags of an outer node would have to be checked against the points of each x-range below it).
"""
from lib2d import header, write

KINDS = {
    "max": {"cap": "Max", "better": ">", "id_py": "NEG", "inf": "-inf", "none_cpp": "NO_MAX", "limit": "min", "word": "max"},
    "min": {"cap": "Min", "better": "<", "id_py": "POS", "inf": "inf", "none_cpp": "NO_MIN", "limit": "max", "word": "min"},
}


def fill(text, k):
    for key, val in (("CAP", k["cap"]), ("BETTER", k["better"]), ("IDPY", k["id_py"]), ("INF", k["inf"]),
                     ("NONE", k["none_cpp"]), ("LIMIT", k["limit"]), ("WORD", k["word"])):
        text = text.replace(f"@{key}@", val)
    return text.strip("\n").split("\n")


POINTS_PY = '''
from bisect import bisect_left, bisect_right

@IDPY@ = float("@INF@")  # no update has reached it


# Rectangle ch@WORD@ with point reads over points known up front (any integers, negative is fine): O(log^2 N) per
# rectChmax, O(log^2 N) per pointGet, N log N memory. A tree over the distinct x's, where every x-node keeps a tree over
# the y's of its own points. rectCh@WORD@(x1, y1, x2, y2, v) leaves v as a tag on the O(log N) x-nodes that make up
# x1..x2, and in each of them on the O(log N) y-nodes that make up y1..y2; pointGet(x, y) takes the @WORD@ of the tags
# on the way from (x, y) up. Tags are never pushed down, which works because ch@WORD@ never has to be undone. The
# points given are the ones you will read or ch@WORD@ one at a time; a rectangle's corners can be anything. A point no
# update has reached reads None.
class PointsRectCh@WORD@2D:
    __slots__ = ("X", "xs", "ys", "off", "cnt", "tag", "given")

    # O(N log N) -- points: every (x, y) you will call pointGet or pointCh@WORD@ on, as pairs of integers (negative is
    # fine, repeats are fine); needs at least one, else ValueError
    def __init__(self, points):
        if not points:
            raise ValueError("PointsRectCh@WORD@2D: needs at least one point")
        given = self.given = set(map(tuple, points))
        xs = self.xs = sorted({x for x, _ in given})
        X = self.X = len(xs)
        lists = [[] for _ in range(2 * X)]
        for x, y in given:
            lists[X + bisect_left(xs, x)].append(y)
        for i in range(X, 2 * X):
            lists[i].sort()
        for i in range(X - 1, 0, -1):  # an x-node's y's: its two halves' y's, merged, each y once
            a, b = lists[2 * i], lists[2 * i + 1]
            merged = []
            p = q = 0
            while p < len(a) or q < len(b):
                if q == len(b) or (p < len(a) and a[p] <= b[q]):
                    y = a[p]
                    p += 1
                else:
                    y = b[q]
                    q += 1
                if not merged or merged[-1] != y:
                    merged.append(y)
            lists[i] = merged
        off = self.off = [0] * (2 * X)
        cnt = self.cnt = [0] * (2 * X)
        ys = self.ys = []
        for i in range(1, 2 * X):
            off[i] = len(ys)
            cnt[i] = len(lists[i])
            ys += lists[i]
        # x-node i's y-tree: tag[2 * off[i] + k], its leaves at k = cnt[i] + (the y's place in the x-node's list)
        self.tag = [@IDPY@] * (2 * len(ys))

    # x-node i: the y's in y1..y2 become @WORD@(themselves, v)
    def _cols(self, i, y1, y2, v):
        ys, o, m, tag = self.ys, self.off[i], self.cnt[i], self.tag
        a = bisect_left(ys, y1, o, o + m) - o + m
        b = bisect_right(ys, y2, o, o + m) - o + m
        base = 2 * o
        while a < b:
            if a & 1:
                if v @BETTER@ tag[base + a]:
                    tag[base + a] = v
                a += 1
            if b & 1:
                b -= 1
                if v @BETTER@ tag[base + b]:
                    tag[base + b] = v
            a >>= 1
            b >>= 1

    # O(log^2 N) -- every given point with x1 <= x <= x2 and y1 <= y <= y2 becomes @WORD@(itself, v) (one never
    # reached becomes v); any integers; needs x1 <= x2 and y1 <= y2, else IndexError
    def rectCh@WORD@(self, x1, y1, x2, y2, v):
        if x1 > x2 or y1 > y2:
            raise IndexError(f"rectCh@WORD@: needs x1 <= x2 and y1 <= y2, got x1 = {x1}, y1 = {y1}, x2 = {x2}, y2 = {y2}")
        xs, X = self.xs, self.X
        l = bisect_left(xs, x1) + X
        r = bisect_right(xs, x2) + X
        while l < r:
            if l & 1:
                self._cols(l, y1, y2, v)
                l += 1
            if r & 1:
                r -= 1
                self._cols(r, y1, y2, v)
            l >>= 1
            r >>= 1

    # O(log N) -- the point (x, y) becomes @WORD@(itself, v) (one never reached becomes v); needs (x, y) to be one of
    # the points given, else IndexError
    def pointCh@WORD@(self, x, y, v):
        if (x, y) not in self.given:
            raise IndexError(f"pointCh@WORD@: ({x}, {y}) is not one of the points given to the constructor")
        i = bisect_left(self.xs, x) + self.X
        o, m = self.off[i], self.cnt[i]
        k = 2 * o + bisect_left(self.ys, y, o, o + m) - o + m
        if v @BETTER@ self.tag[k]:
            self.tag[k] = v

    # O(log^2 N) -- the value at (x, y), None if no update has reached it; needs (x, y) to be one of the points given,
    # else IndexError
    def pointGet(self, x, y):
        if (x, y) not in self.given:
            raise IndexError(f"pointGet: ({x}, {y}) is not one of the points given to the constructor")
        ys, off, cnt, tag = self.ys, self.off, self.cnt, self.tag
        res = @IDPY@
        i = bisect_left(self.xs, x) + self.X
        while i:
            o, m = off[i], cnt[i]
            base = 2 * o
            k = bisect_left(ys, y, o, o + m) - o + m
            while k:
                cand = tag[base + k]
                if cand @BETTER@ res:
                    res = cand
                k >>= 1
            i >>= 1
        return None if res == @IDPY@ else res
'''

POINTS_CPP = '''
// Rectangle ch@WORD@ with point reads over points known up front (any integers, negative is fine): O(log^2 N) per
// rectChmax, O(log^2 N) per pointGet, N log N memory. A tree over the distinct x's, where every x-node keeps a tree over
// the y's of its own points. rectCh@WORD@(x1, y1, x2, y2, v) leaves v as a tag on the O(log N) x-nodes that make up
// x1..x2, and in each of them on the O(log N) y-nodes that make up y1..y2; pointGet(x, y) takes the @WORD@ of the tags
// on the way from (x, y) up. Tags are never pushed down, which works because ch@WORD@ never has to be undone. The
// points given are the ones you will read or ch@WORD@ one at a time; a rectangle's corners can be anything. A point no
// update has reached reads @NONE@.
// T is any integer type (int, long long, ...). Coordinates are long long.
template <typename T>
struct PointsRectCh@WORD@2D {
    using ll = long long;
    static constexpr T @NONE@ = numeric_limits<T>::@LIMIT@();  // what a point no update has reached reads
    int X;
    vector<pair<ll, ll>> given;  // sorted, each once
    vector<ll> xs, ys;  // ys: every x-node's y's, one x-node after another
    vector<int> off, cnt;  // x-node i's y's are ys[off[i] .. off[i] + cnt[i] - 1]
    vector<T> tag;  // x-node i's y-tree: tag[2 * off[i] + k], its leaves at k = cnt[i] + (the y's place in its list)

    // O(N log N) -- points: every (x, y) you will call pointGet or pointCh@WORD@ on (negative is fine, repeats are
    // fine); needs at least one, else throws invalid_argument
    explicit PointsRectCh@WORD@2D(vector<pair<ll, ll>> points) : given(std::move(points)) {
        if (given.empty()) throw invalid_argument("PointsRectCh@WORD@2D: needs at least one point");
        sort(given.begin(), given.end());
        given.erase(unique(given.begin(), given.end()), given.end());
        for (auto& p : given)
            if (xs.empty() || xs.back() != p.first) xs.push_back(p.first);
        X = (int)xs.size();
        vector<vector<ll>> lists(2 * X);
        for (size_t i = 0, j = 0; i < given.size(); i++) {  // (given is sorted by x, then y: each leaf's list comes sorted)
            while (xs[j] != given[i].first) j++;
            lists[X + j].push_back(given[i].second);
        }
        for (int i = X - 1; i >= 1; i--) {  // an x-node's y's: its two halves' y's, merged, each y once
            auto& out = lists[i];
            auto &a = lists[2 * i], &b = lists[2 * i + 1];
            merge(a.begin(), a.end(), b.begin(), b.end(), back_inserter(out));
            out.erase(unique(out.begin(), out.end()), out.end());
        }
        off.assign(2 * X, 0), cnt.assign(2 * X, 0);
        for (int i = 1; i < 2 * X; i++) {
            off[i] = (int)ys.size(), cnt[i] = (int)lists[i].size();
            ys.insert(ys.end(), lists[i].begin(), lists[i].end());
        }
        tag.assign(2 * ys.size(), @NONE@);
    }

    // where (x, y) is among the given points (its x's place in xs), or -1
    int find(ll x, ll y) const {
        auto it = lower_bound(given.begin(), given.end(), make_pair(x, y));
        if (it == given.end() || *it != make_pair(x, y)) return -1;
        return hotLowerBound(&xs[0], X, x);
    }

    // x-node i: the y's in y1..y2 become @WORD@(themselves, v)
    void cols(int i, ll y1, ll y2, T v) {
        const ll* first = &ys[off[i]];
        int m = cnt[i], base = 2 * off[i];
        int a = hotLowerBound(first, m, y1) + m, b = hotUpperBound(first, m, y2) + m;
        T* t = &tag[base];
        for (; a < b; a >>= 1, b >>= 1) {
            if (a & 1) {
                if (v @BETTER@ t[a]) t[a] = v;
                a++;
            }
            if (b & 1) {
                b--;
                if (v @BETTER@ t[b]) t[b] = v;
            }
        }
    }

    // O(log^2 N) -- every given point with x1 <= x <= x2 and y1 <= y <= y2 becomes @WORD@(itself, v) (one never
    // reached becomes v); any integers; needs x1 <= x2 and y1 <= y2, else throws out_of_range
    void rectCh@WORD@(ll x1, ll y1, ll x2, ll y2, T v) {
        if (x1 > x2 || y1 > y2) throw out_of_range("rectCh@WORD@: needs x1 <= x2 and y1 <= y2");
        int l = hotLowerBound(&xs[0], X, x1) + X, r = hotUpperBound(&xs[0], X, x2) + X;
        for (; l < r; l >>= 1, r >>= 1) {
            if (l & 1) cols(l++, y1, y2, v);
            if (r & 1) cols(--r, y1, y2, v);
        }
    }

    // O(log N) -- the point (x, y) becomes @WORD@(itself, v) (one never reached becomes v); needs (x, y) to be one of
    // the points given, else throws out_of_range
    void pointCh@WORD@(ll x, ll y, T v) {
        int j = find(x, y);
        if (j < 0) throw out_of_range("pointCh@WORD@: (x, y) is not one of the points given to the constructor");
        int i = j + X, m = cnt[i];
        T& t = tag[2 * off[i] + hotLowerBound(&ys[off[i]], m, y) + m];
        if (v @BETTER@ t) t = v;
    }

    // O(log^2 N) -- the value at (x, y), @NONE@ if no update has reached it; needs (x, y) to be one of the points given,
    // else throws out_of_range
    T pointGet(ll x, ll y) {
        int j = find(x, y);
        if (j < 0) throw out_of_range("pointGet: (x, y) is not one of the points given to the constructor");
        T res = @NONE@;
        for (int i = j + X; i; i >>= 1) {
            int m = cnt[i];
            const T* t = &tag[2 * off[i]];
            for (int k = hotLowerBound(&ys[off[i]], m, y) + m; k; k >>= 1)
                if (t[k] @BETTER@ res) res = t[k];
        }
        return res;
    }
};
'''

ONLINE_PY = '''
@IDPY@ = float("@INF@")  # no update has reached it


# Rectangle ch@WORD@ with point reads over a huge coordinate range, nothing known up front: O(log^2 U) per rectChmax,
# O(log^2 U) per pointGet, and up to about 4 log^2 U new nodes per rectChmax. A dynamic tree over x whose every node
# owns a dynamic tree over y, nodes made only where an update goes. rectCh@WORD@(x1, y1, x2, y2, v) leaves v as a tag
# on the O(log U) x-nodes that make up x1..x2, and in each of them on the O(log U) y-nodes that make up y1..y2;
# pointGet(x, y) takes the @WORD@ of the tags on the way down to (x, y). Tags are never pushed down, which works because
# ch@WORD@ never has to be undone. A cell no update has reached reads None.
class OnlineRectCh@WORD@2D:
    __slots__ = ("xLo", "xHi", "yLo", "yHi", "xLeft", "xRight", "xTree", "yLeft", "yRight", "tag")

    # O(1) -- every cell of [xLo, xHi] by [yLo, yHi] unreached; needs xLo <= xHi and yLo <= yHi, else ValueError
    def __init__(self, xLo, xHi, yLo, yHi):
        if xLo > xHi or yLo > yHi:
            raise ValueError(f"OnlineRectCh@WORD@2D: needs xLo <= xHi and yLo <= yHi, got xLo = {xLo}, xHi = {xHi}, "
                             f"yLo = {yLo}, yHi = {yHi}")
        self.xLo, self.xHi, self.yLo, self.yHi = xLo, xHi, yLo, yHi
        self.xLeft = [0, 0]  # x-node 0 = nothing there, x-node 1 = the root
        self.xRight = [0, 0]
        self.xTree = [0, 0]  # an x-node's own y-tree (its root, 0 = none yet)
        self.yLeft = [0]  # y-node 0 = nothing there
        self.yRight = [0]
        self.tag = [@IDPY@]

    # the y-tree rooted at root (0: a new one): y1..y2 become @WORD@(themselves, v); returns its root
    def _cols(self, root, y1, y2, v):
        yLeft, yRight, tag = self.yLeft, self.yRight, self.tag
        if not root:
            root = len(tag)
            yLeft.append(0)
            yRight.append(0)
            tag.append(@IDPY@)
        stack = [(root, self.yLo, self.yHi)]
        while stack:
            q, lo, hi = stack.pop()
            if y1 <= lo and hi <= y2:
                if v @BETTER@ tag[q]:
                    tag[q] = v
                continue
            mid = (lo + hi) >> 1
            if y1 <= mid:
                if not yLeft[q]:
                    yLeft[q] = len(tag)
                    yLeft.append(0)
                    yRight.append(0)
                    tag.append(@IDPY@)
                stack.append((yLeft[q], lo, mid))
            if y2 > mid:
                if not yRight[q]:
                    yRight[q] = len(tag)
                    yLeft.append(0)
                    yRight.append(0)
                    tag.append(@IDPY@)
                stack.append((yRight[q], mid + 1, hi))
        return root

    # O(log^2 U) -- every cell with x1 <= x <= x2 and y1 <= y <= y2 becomes @WORD@(itself, v) (one never reached becomes
    # v); needs xLo <= x1 <= x2 <= xHi and yLo <= y1 <= y2 <= yHi, else IndexError
    def rectCh@WORD@(self, x1, y1, x2, y2, v):
        if not (self.xLo <= x1 <= x2 <= self.xHi and self.yLo <= y1 <= y2 <= self.yHi):
            raise IndexError(f"rectCh@WORD@: needs xLo <= x1 <= x2 <= xHi and yLo <= y1 <= y2 <= yHi, got x1 = {x1}, "
                             f"y1 = {y1}, x2 = {x2}, y2 = {y2}")
        self._update(x1, y1, x2, y2, v)

    def _update(self, x1, y1, x2, y2, v):
        xLeft, xRight, xTree = self.xLeft, self.xRight, self.xTree
        stack = [(1, self.xLo, self.xHi)]
        while stack:
            p, lo, hi = stack.pop()
            if x1 <= lo and hi <= x2:
                xTree[p] = self._cols(xTree[p], y1, y2, v)
                continue
            mid = (lo + hi) >> 1
            if x1 <= mid:
                if not xLeft[p]:
                    xLeft[p] = len(xTree)
                    xLeft.append(0)
                    xRight.append(0)
                    xTree.append(0)
                stack.append((xLeft[p], lo, mid))
            if x2 > mid:
                if not xRight[p]:
                    xRight[p] = len(xTree)
                    xLeft.append(0)
                    xRight.append(0)
                    xTree.append(0)
                stack.append((xRight[p], mid + 1, hi))

    # O(log^2 U) -- the cell (x, y) becomes @WORD@(itself, v) (one never reached becomes v); needs xLo <= x <= xHi and
    # yLo <= y <= yHi, else IndexError
    def pointCh@WORD@(self, x, y, v):
        if not (self.xLo <= x <= self.xHi and self.yLo <= y <= self.yHi):
            raise IndexError(f"pointCh@WORD@: needs xLo <= x <= xHi and yLo <= y <= yHi, got x = {x}, y = {y}")
        self._update(x, y, x, y, v)

    # O(log^2 U) -- the value at (x, y), None if no update has reached it; needs xLo <= x <= xHi and yLo <= y <= yHi,
    # else IndexError
    def pointGet(self, x, y):
        if not (self.xLo <= x <= self.xHi and self.yLo <= y <= self.yHi):
            raise IndexError(f"pointGet: needs xLo <= x <= xHi and yLo <= y <= yHi, got x = {x}, y = {y}")
        xLeft, xRight, xTree = self.xLeft, self.xRight, self.xTree
        yLeft, yRight, tag = self.yLeft, self.yRight, self.tag
        res = @IDPY@
        p, lo, hi = 1, self.xLo, self.xHi
        while p:
            q, ylo, yhi = xTree[p], self.yLo, self.yHi
            while q:
                if tag[q] @BETTER@ res:
                    res = tag[q]
                if ylo == yhi:
                    break
                mid = (ylo + yhi) >> 1
                if y <= mid:
                    q, yhi = yLeft[q], mid
                else:
                    q, ylo = yRight[q], mid + 1
            if lo == hi:
                break
            mid = (lo + hi) >> 1
            if x <= mid:
                p, hi = xLeft[p], mid
            else:
                p, lo = xRight[p], mid + 1
        return None if res == @IDPY@ else res
'''

ONLINE_CPP = '''
// Rectangle ch@WORD@ with point reads over a huge coordinate range, nothing known up front: O(log^2 U) per rectChmax,
// O(log^2 U) per pointGet, and up to about 4 log^2 U new nodes per rectChmax. A dynamic tree over x whose every node
// owns a dynamic tree over y, nodes made only where an update goes. rectCh@WORD@(x1, y1, x2, y2, v) leaves v as a tag
// on the O(log U) x-nodes that make up x1..x2, and in each of them on the O(log U) y-nodes that make up y1..y2;
// pointGet(x, y) takes the @WORD@ of the tags on the way down to (x, y). Tags are never pushed down, which works because
// ch@WORD@ never has to be undone. A cell no update has reached reads @NONE@.
// T is any integer type (int, long long, ...). Coordinates are long long.
template <typename T>
struct OnlineRectCh@WORD@2D {
    using ll = long long;
    static constexpr T @NONE@ = numeric_limits<T>::@LIMIT@();  // what a cell no update has reached reads
    ll xLo, xHi, yLo, yHi;
    int xUsed = 2, yUsed = 1;  // how many x-nodes / y-nodes exist (the arrays are longer: they double when full)
    vector<int> xLeft, xRight, xTree;  // x-node 0 = nothing there, 1 = the root; xTree = its own y-tree's root (0 = none)
    vector<int> yLeft, yRight;  // y-node 0 = nothing there
    vector<T> tag;

    // O(1) -- every cell of [xLo, xHi] by [yLo, yHi] unreached; needs xLo <= xHi and yLo <= yHi, else throws
    // invalid_argument
    OnlineRectCh@WORD@2D(ll xLo, ll xHi, ll yLo, ll yHi)
        : xLo(xLo), xHi(xHi), yLo(yLo), yHi(yHi), xLeft(64, 0), xRight(64, 0), xTree(64, 0) {
        if (xLo > xHi || yLo > yHi) throw invalid_argument("OnlineRectCh@WORD@2D: needs xLo <= xHi and yLo <= yHi");
        yLeft.assign(64, 0), yRight.assign(64, 0), tag.assign(64, @NONE@);
    }

    // a new node is the next unused slot (already blank); a full array doubles
    int newX() {
        if (xUsed == (int)xLeft.size())
            xLeft.resize(2 * xUsed, 0), xRight.resize(2 * xUsed, 0), xTree.resize(2 * xUsed, 0);
        return xUsed++;
    }

    int newY() {
        if (yUsed == (int)yLeft.size())
            yLeft.resize(2 * (size_t)yUsed, 0), yRight.resize(2 * (size_t)yUsed, 0),
                tag.resize(2 * (size_t)yUsed, @NONE@);
        return yUsed++;
    }

    // y-node q (covering lo..hi): y1..y2 become @WORD@(themselves, v)
    void cols(int q, ll lo, ll hi, ll y1, ll y2, T v) {
        if (y1 <= lo && hi <= y2) {
            if (v @BETTER@ tag[q]) tag[q] = v;
            return;
        }
        ll mid = lo + (hi - lo) / 2;
        if (y1 <= mid) {
            if (!yLeft[q]) { int made = newY(); yLeft[q] = made; }
            cols(yLeft[q], lo, mid, y1, y2, v);
        }
        if (y2 > mid) {
            if (!yRight[q]) { int made = newY(); yRight[q] = made; }
            cols(yRight[q], mid + 1, hi, y1, y2, v);
        }
    }

    // x-node p (covering lo..hi): the rectangle's part of it
    void update(int p, ll lo, ll hi, ll x1, ll y1, ll x2, ll y2, T v) {
        if (x1 <= lo && hi <= x2) {
            if (!xTree[p]) { int made = newY(); xTree[p] = made; }
            cols(xTree[p], yLo, yHi, y1, y2, v);
            return;
        }
        ll mid = lo + (hi - lo) / 2;
        if (x1 <= mid) {
            if (!xLeft[p]) { int made = newX(); xLeft[p] = made; }
            update(xLeft[p], lo, mid, x1, y1, x2, y2, v);
        }
        if (x2 > mid) {
            if (!xRight[p]) { int made = newX(); xRight[p] = made; }
            update(xRight[p], mid + 1, hi, x1, y1, x2, y2, v);
        }
    }

    // O(log^2 U) -- every cell with x1 <= x <= x2 and y1 <= y <= y2 becomes @WORD@(itself, v) (one never reached becomes
    // v); needs xLo <= x1 <= x2 <= xHi and yLo <= y1 <= y2 <= yHi, else throws out_of_range
    void rectCh@WORD@(ll x1, ll y1, ll x2, ll y2, T v) {
        if (x1 < xLo || x1 > x2 || x2 > xHi || y1 < yLo || y1 > y2 || y2 > yHi)
            throw out_of_range("rectCh@WORD@: needs xLo <= x1 <= x2 <= xHi and yLo <= y1 <= y2 <= yHi");
        update(1, xLo, xHi, x1, y1, x2, y2, v);
    }

    // O(log^2 U) -- the cell (x, y) becomes @WORD@(itself, v) (one never reached becomes v); needs xLo <= x <= xHi and
    // yLo <= y <= yHi, else throws out_of_range
    void pointCh@WORD@(ll x, ll y, T v) {
        if (x < xLo || x > xHi || y < yLo || y > yHi) throw out_of_range("pointCh@WORD@: needs xLo <= x <= xHi and yLo <= y <= yHi");
        update(1, xLo, xHi, x, y, x, y, v);
    }

    // O(log^2 U) -- the value at (x, y), @NONE@ if no update has reached it; needs xLo <= x <= xHi and yLo <= y <= yHi,
    // else throws out_of_range
    T pointGet(ll x, ll y) const {
        if (x < xLo || x > xHi || y < yLo || y > yHi) throw out_of_range("pointGet: needs xLo <= x <= xHi and yLo <= y <= yHi");
        T res = @NONE@;
        int p = 1;
        for (ll lo = xLo, hi = xHi; p;) {
            int q = xTree[p];
            for (ll ylo = yLo, yhi = yHi; q;) {
                if (tag[q] @BETTER@ res) res = tag[q];
                if (ylo == yhi) break;
                ll mid = ylo + (yhi - ylo) / 2;
                if (y <= mid) q = yLeft[q], yhi = mid;
                else q = yRight[q], ylo = mid + 1;
            }
            if (lo == hi) break;
            ll mid = lo + (hi - lo) / 2;
            if (x <= mid) p = xLeft[p], hi = mid;
            else p = xRight[p], lo = mid + 1;
        }
        return res;
    }
};
'''


def emit(folder, kind_input, ops, costs, build, memory, py, cpp):
    args = (ops, "seg-tree-kept-tags", costs, build, memory, kind_input, [("empty-cells", "yes")])
    write(folder, header(folder, "py", *args) + [""] + py, header(folder, "cpp", *args) + [""] + cpp)


def main():
    for key, k in KINDS.items():
        upd, pupd = f"rectCh{key}", f"pointCh{key}"
        ops = [upd, pupd, "pointGet"]
        emit(f"points-kept-tags-{key}", "points", ops, {upd: "log^2(N)", pupd: "log(N)", "pointGet": "log^2(N)"}, "N*log(N)",
             {"layout": "2n-iterative", "node": "none", "tags": "tag[2*N*log(N)]",
              "other": "ys[1*N*log(N)] xs[1*N] off[2*N] cnt[2*N] given[2*N]",
              "note": "every point's y is listed in each of the O(log N) x-nodes above it; an x-node's y-tree is twice its list"},
             fill(POINTS_PY, k), fill(POINTS_CPP, k))
        emit(f"online-kept-tags-{key}", "online", ops, {upd: "log^2(U)", pupd: "log^2(U)", "pointGet": "log^2(U)"}, "1",
             {"layout": "sparse", "node": "none", "tags": "tag[4*log^2(U)]", "other": "yLeft[4*log^2(U)] yRight[4*log^2(U)] "
              "xLeft[2*log(U)] xRight[2*log(U)] xTree[2*log(U)]",
              "note": "sizes are per update: a rectangle makes up to about 2 log U x-nodes and, in each of the O(log U) it "
                      "tags, up to about 2 log U y-nodes"},
             fill(ONLINE_PY, k), fill(ONLINE_CPP, k))
    print("kept tags over points / online: 4 folders")


if __name__ == "__main__":
    main()
