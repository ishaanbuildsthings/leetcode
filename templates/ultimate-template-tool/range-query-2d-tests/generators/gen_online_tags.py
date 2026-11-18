"""Online (nothing known up front) rectangle updates with tags that stay put, on dynamic trees of trees:

    python3 gen_online_tags.py     # writes range-queries-2d/online-rect-assign-point-get and
                                   # online-kept-tags-rect-<max|min> (template.{py,cpp})

  online-rect-assign-point-get       rect assign + point get: every write gets the next timestamp and leaves it at the
                                     O(log^2 U) nodes of its rectangle; a read takes the newest timestamp on its path
  online-kept-tags-rect-<max|min>    rect chmax + rect max (chmin + min): every x-node keeps two y-trees (writes that
                                     cover all of its x's, writes that touch any of them), and every y-node two values
                                     (the same, for y); a query reads "touch" where it covers a node and "cover" above
"""
from lib2d import header, write

BOUNDS_PY = '''        if xLo > xHi or yLo > yHi:
            raise ValueError(f"@CLS@: needs xLo <= xHi and yLo <= yHi, got xLo = {xLo}, "
                             f"xHi = {xHi}, yLo = {yLo}, yHi = {yHi}")
        self.xLo, self.xHi, self.yLo, self.yHi = xLo, xHi, yLo, yHi'''
POINT_CHECK_PY = '''        if not (self.xLo <= x <= self.xHi and self.yLo <= y <= self.yHi):
            raise IndexError(f"@OP@: needs xLo <= x <= xHi and yLo <= y <= yHi, got x = {x}, y = {y}")'''
RECT_CHECK_PY = '''        if not (self.xLo <= x1 <= x2 <= self.xHi and self.yLo <= y1 <= y2 <= self.yHi):
            raise IndexError(f"@OP@: needs xLo <= x1 <= x2 <= xHi and yLo <= y1 <= y2 <= yHi, got x1 = {x1}, "
                             f"y1 = {y1}, x2 = {x2}, y2 = {y2}")'''
POINT_CHECK_CPP = ('        if (x < xLo || x > xHi || y < yLo || y > yHi)\n'
                   '            throw out_of_range("@OP@: needs xLo <= x <= xHi and yLo <= y <= yHi");')
RECT_CHECK_CPP = ('        if (x1 < xLo || x1 > x2 || x2 > xHi || y1 < yLo || y1 > y2 || y2 > yHi)\n'
                  '            throw out_of_range("@OP@: needs xLo <= x1 <= x2 <= xHi and yLo <= y1 <= y2 <= yHi");')
POINT_RULE = "needs xLo <= x <= xHi and yLo <= y <= yHi, else {err}"
RECT_RULE = "needs xLo <= x1 <= x2 <= xHi and yLo <= y1 <= y2 <= yHi, else {err}"


def sub(text, **kw):
    for key, val in kw.items():
        text = text.replace(f"@{key}@", val)
    return text


# ------------------------------------------------------------------------------------------------ rect assign
ASSIGN_DOC = ("Rectangle assign with point reads over a huge coordinate range, nothing known up front: O(log^2 U) per "
              "rectAssign and per pointGet, and up to about 4 log^2 U new nodes per rectAssign. A dynamic tree over x "
              "whose every node owns a dynamic tree over y, nodes made only where a write goes. Every write gets the next "
              "timestamp and leaves it at the O(log U) x-nodes that make up x1..x2, and in each of them at the O(log U) "
              "y-nodes that make up y1..y2. A read takes the newest timestamp on its way down to (x, y) and returns the "
              "value written then: a newer write always wins, so nothing is ever pushed down or undone. A cell no write "
              "has reached reads 0.")

ASSIGN_PY = '''
# @DOC@
class OnlineRectAssignPointGet2D:
    __slots__ = ("xLo", "xHi", "yLo", "yHi", "xLeft", "xRight", "xTree", "yLeft", "yRight", "stamp", "vals")

    # O(1) -- every cell of [xLo, xHi] by [yLo, yHi] starts at 0; needs xLo <= xHi and yLo <= yHi, else ValueError
    def __init__(self, xLo, xHi, yLo, yHi):
@BOUNDS@
        self.xLeft = [0, 0]  # x-node 0 = nothing there, x-node 1 = the root
        self.xRight = [0, 0]
        self.xTree = [0, 0]  # an x-node's own y-tree (its root, 0 = none yet)
        self.yLeft = [0]  # y-node 0 = nothing there
        self.yRight = [0]
        self.stamp = [0]  # the newest timestamp left at a y-node (0 = none)
        self.vals = [0]  # vals[t]: the value written at timestamp t (vals[0] = 0: never written)

    # the y-tree rooted at root (0: a new one): y1..y2 get timestamp t; returns its root
    def _cols(self, root, y1, y2, t):
        yLeft, yRight, stamp = self.yLeft, self.yRight, self.stamp
        if not root:
            root = len(stamp)
            yLeft.append(0)
            yRight.append(0)
            stamp.append(0)
        todo = [(root, self.yLo, self.yHi)]
        while todo:
            q, lo, hi = todo.pop()
            if y1 <= lo and hi <= y2:
                stamp[q] = t
                continue
            mid = (lo + hi) >> 1
            if y1 <= mid:
                if not yLeft[q]:
                    yLeft[q] = len(stamp)
                    yLeft.append(0)
                    yRight.append(0)
                    stamp.append(0)
                todo.append((yLeft[q], lo, mid))
            if y2 > mid:
                if not yRight[q]:
                    yRight[q] = len(stamp)
                    yLeft.append(0)
                    yRight.append(0)
                    stamp.append(0)
                todo.append((yRight[q], mid + 1, hi))
        return root

    # every cell of the rectangle gets the next timestamp, which stands for v
    def _write(self, x1, y1, x2, y2, v):
        self.vals.append(v)
        t = len(self.vals) - 1
        xLeft, xRight, xTree = self.xLeft, self.xRight, self.xTree
        todo = [(1, self.xLo, self.xHi)]
        while todo:
            p, lo, hi = todo.pop()
            if x1 <= lo and hi <= x2:
                xTree[p] = self._cols(xTree[p], y1, y2, t)
                continue
            mid = (lo + hi) >> 1
            if x1 <= mid:
                if not xLeft[p]:
                    xLeft[p] = len(xTree)
                    xLeft.append(0)
                    xRight.append(0)
                    xTree.append(0)
                todo.append((xLeft[p], lo, mid))
            if x2 > mid:
                if not xRight[p]:
                    xRight[p] = len(xTree)
                    xLeft.append(0)
                    xRight.append(0)
                    xTree.append(0)
                todo.append((xRight[p], mid + 1, hi))

    # O(log^2 U) -- every cell with x1 <= x <= x2 and y1 <= y <= y2 becomes v; @RECT_RULE@
    def rectAssign(self, x1, y1, x2, y2, v):
@RECT_CHECK_A@
        self._write(x1, y1, x2, y2, v)

    # O(log^2 U) -- the cell (x, y) becomes v; @POINT_RULE@
    def pointAssign(self, x, y, v):
@POINT_CHECK_A@
        self._write(x, y, x, y, v)

    # O(log^2 U) -- the value at (x, y), 0 if no write has reached it; @POINT_RULE@
    def pointGet(self, x, y):
@POINT_CHECK_G@
        xLeft, xRight, xTree = self.xLeft, self.xRight, self.xTree
        yLeft, yRight, stamp = self.yLeft, self.yRight, self.stamp
        best = 0
        p, lo, hi = 1, self.xLo, self.xHi
        while p:
            q, ylo, yhi = xTree[p], self.yLo, self.yHi
            while q:
                if stamp[q] > best:
                    best = stamp[q]
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
        return self.vals[best]
'''

ASSIGN_CPP = '''
// @DOC@
// T is any number type. Coordinates are long long.
template <typename T>
struct OnlineRectAssignPointGet2D {
    using ll = long long;
    ll xLo, xHi, yLo, yHi;
    int xUsed = 2, yUsed = 1;  // how many x-nodes / y-nodes exist (the arrays are longer: they double when full)
    vector<int> xLeft, xRight, xTree;  // x-node 0 = nothing there, 1 = the root; xTree = its own y-tree's root (0 = none)
    vector<int> yLeft, yRight, stamp;  // y-node 0 = nothing there; stamp = the newest timestamp left there (0 = none)
    vector<T> vals;  // vals[t]: the value written at timestamp t (vals[0] = 0: never written)

    // O(1) -- every cell of [xLo, xHi] by [yLo, yHi] starts at 0; needs xLo <= xHi and yLo <= yHi, else throws
    // invalid_argument
    OnlineRectAssignPointGet2D(ll xLo, ll xHi, ll yLo, ll yHi)
        : xLo(xLo), xHi(xHi), yLo(yLo), yHi(yHi), xLeft(64, 0), xRight(64, 0), xTree(64, 0) {
        if (xLo > xHi || yLo > yHi) throw invalid_argument("OnlineRectAssignPointGet2D: needs xLo <= xHi and yLo <= yHi");
        yLeft.assign(64, 0), yRight.assign(64, 0), stamp.assign(64, 0);
        vals.push_back(T(0));
    }

    // a new node is the next unused slot (already blank); a full array doubles
    int newX() {
        if (xUsed == (int)xLeft.size())
            xLeft.resize(2 * xUsed, 0), xRight.resize(2 * xUsed, 0), xTree.resize(2 * xUsed, 0);
        return xUsed++;
    }

    int newY() {
        if (yUsed == (int)yLeft.size())
            yLeft.resize(2 * (size_t)yUsed, 0), yRight.resize(2 * (size_t)yUsed, 0), stamp.resize(2 * (size_t)yUsed, 0);
        return yUsed++;
    }

    // y-node q (covering lo..hi): y1..y2 get timestamp t
    void cols(int q, ll lo, ll hi, ll y1, ll y2, int t) {
        if (y1 <= lo && hi <= y2) {
            stamp[q] = t;
            return;
        }
        ll mid = lo + (hi - lo) / 2;
        if (y1 <= mid) {
            if (!yLeft[q]) { int made = newY(); yLeft[q] = made; }
            cols(yLeft[q], lo, mid, y1, y2, t);
        }
        if (y2 > mid) {
            if (!yRight[q]) { int made = newY(); yRight[q] = made; }
            cols(yRight[q], mid + 1, hi, y1, y2, t);
        }
    }

    // x-node p (covering lo..hi): the rectangle's part of it gets timestamp t
    void update(int p, ll lo, ll hi, ll x1, ll y1, ll x2, ll y2, int t) {
        if (x1 <= lo && hi <= x2) {
            if (!xTree[p]) { int made = newY(); xTree[p] = made; }
            cols(xTree[p], yLo, yHi, y1, y2, t);
            return;
        }
        ll mid = lo + (hi - lo) / 2;
        if (x1 <= mid) {
            if (!xLeft[p]) { int made = newX(); xLeft[p] = made; }
            update(xLeft[p], lo, mid, x1, y1, x2, y2, t);
        }
        if (x2 > mid) {
            if (!xRight[p]) { int made = newX(); xRight[p] = made; }
            update(xRight[p], mid + 1, hi, x1, y1, x2, y2, t);
        }
    }

    // O(log^2 U) -- every cell with x1 <= x <= x2 and y1 <= y <= y2 becomes v; @RECT_RULE@
    void rectAssign(ll x1, ll y1, ll x2, ll y2, T v) {
@RECT_CHECK_A@
        vals.push_back(v);
        update(1, xLo, xHi, x1, y1, x2, y2, (int)vals.size() - 1);
    }

    // O(log^2 U) -- the cell (x, y) becomes v; @POINT_RULE@
    void pointAssign(ll x, ll y, T v) {
@POINT_CHECK_A@
        vals.push_back(v);
        update(1, xLo, xHi, x, y, x, y, (int)vals.size() - 1);
    }

    // O(log^2 U) -- the value at (x, y), 0 if no write has reached it; @POINT_RULE@
    T pointGet(ll x, ll y) const {
@POINT_CHECK_G@
        int best = 0, p = 1;
        for (ll lo = xLo, hi = xHi; p;) {
            int q = xTree[p];
            for (ll ylo = yLo, yhi = yHi; q;) {
                if (stamp[q] > best) best = stamp[q];
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
        return vals[best];
    }
};
'''


def lines(text, doc, cm):
    out = []
    for line in text.strip("\n").split("\n"):
        if line.strip() == f"{cm} @DOC@":
            from lib2d import wrap_comment
            out += wrap_comment(doc, cm)
        else:
            out.append(line)
    return out


def assign():
    folder = "online-rect-assign-point-get"
    py = sub(ASSIGN_PY, BOUNDS=sub(BOUNDS_PY, CLS="OnlineRectAssignPointGet2D"),
             RECT_CHECK_A=sub(RECT_CHECK_PY, OP="rectAssign"), POINT_CHECK_A=sub(POINT_CHECK_PY, OP="pointAssign"),
             POINT_CHECK_G=sub(POINT_CHECK_PY, OP="pointGet"),
             RECT_RULE=RECT_RULE.format(err="IndexError"), POINT_RULE=POINT_RULE.format(err="IndexError"))
    cpp = sub(ASSIGN_CPP, RECT_CHECK_A=sub(RECT_CHECK_CPP, OP="rectAssign"),
              POINT_CHECK_A=sub(POINT_CHECK_CPP, OP="pointAssign"), POINT_CHECK_G=sub(POINT_CHECK_CPP, OP="pointGet"),
              RECT_RULE=RECT_RULE.format(err="throws out_of_range"), POINT_RULE=POINT_RULE.format(err="throws out_of_range"))
    ops = ["rectAssign", "pointAssign", "pointGet"]
    costs = {op: "log^2(U)" for op in ops}
    memory = {"layout": "sparse", "node": "none", "tags": "stamp[4*log^2(U)]",
              "other": "yLeft[4*log^2(U)] yRight[4*log^2(U)] xLeft[2*log(U)] xRight[2*log(U)] xTree[2*log(U)] vals[1]",
              "note": "sizes are per write: a rectangle makes up to about 2 log U x-nodes and, in each of the O(log U) it "
                      "marks, up to about 2 log U y-nodes; vals keeps each write's value"}
    args = (ops, "seg-tree-kept-tags", costs, "1", memory, "online")
    write(folder, header(folder, "py", *args) + [""] + lines(py, ASSIGN_DOC, "#"),
          header(folder, "cpp", *args) + [""] + lines(cpp, ASSIGN_DOC, "//"))


# ------------------------------------------------------------------------------------------------ rect chmax + rect max
KINDS = {
    "max": {"CAP": "Max", "BETTER": ">", "ID": "NEG", "INF": "-inf", "NONE": "NO_MAX", "LIMIT": "lowest",
            "EXTREME": "smallest", "WORD": "max"},
    "min": {"CAP": "Min", "BETTER": "<", "ID": "POS", "INF": "inf", "NONE": "NO_MIN", "LIMIT": "max",
            "EXTREME": "largest", "WORD": "min"},
}
TAGS_DOC = ("Rectangle ch@WORD@ and rectangle @WORD@ over a huge coordinate range, nothing known up front: O(log^2 U) "
            "per operation, and up to about 8 log^2 U new nodes per update. A dynamic tree over x whose every node owns "
            "two dynamic trees over y: one for the updates that cover all of its x's, one for the updates that touch any "
            "of them. Every y-node keeps the same two values for its y's. An update goes into the touch side of every "
            "node it meets and the cover side of the nodes that make up its rectangle; a query reads the touch side of "
            "the nodes that make up its rectangle and the cover side of the nodes above them (an update covering a whole "
            "node above covers the query's part of it too). Tags are never pushed down, which works because ch@WORD@ "
            "never has to be undone and seeing one update twice doesn't change a @WORD@. A cell no update has reached is "
            "empty and queries only see set cells.")

TAGS_PY = '''
@ID@ = float("@INF@")  # no update has reached it


# @DOC@
class OnlineRectCh@WORD@Rect@CAP@2D:
    __slots__ = ("xLo", "xHi", "yLo", "yHi", "xLeft", "xRight", "xCover", "xTouch", "yLeft", "yRight", "yCover", "yTouch", "best")

    # O(1) -- every cell of [xLo, xHi] by [yLo, yHi] empty; needs xLo <= xHi and yLo <= yHi, else ValueError
    def __init__(self, xLo, xHi, yLo, yHi):
@BOUNDS@
        self.xLeft = [0, 0]  # x-node 0 = nothing there, x-node 1 = the root
        self.xRight = [0, 0]
        self.xCover = [0, 0]  # an x-node's y-tree for the updates covering all of its x's (its root, 0 = none yet)
        self.xTouch = [0, 0]  # ... and its y-tree for the updates touching any of its x's
        self.yLeft = [0]  # y-node 0 = nothing there
        self.yRight = [0]
        self.yCover = [@ID@]  # the best update covering all of a y-node's y's
        self.yTouch = [@ID@]  # the best update touching any of them
        self.best = @ID@

    def _newY(self):
        self.yLeft.append(0)
        self.yRight.append(0)
        self.yCover.append(@ID@)
        self.yTouch.append(@ID@)
        return len(self.yCover) - 1

    # the y-tree rooted at root (0: a new one): y1..y2 become @WORD@(themselves, v); returns its root
    def _cols(self, root, y1, y2, v):
        yLeft, yRight, yCover, yTouch = self.yLeft, self.yRight, self.yCover, self.yTouch
        if not root:
            root = self._newY()
        todo = [(root, self.yLo, self.yHi)]
        while todo:
            q, lo, hi = todo.pop()
            if v @BETTER@ yTouch[q]:
                yTouch[q] = v
            if y1 <= lo and hi <= y2:
                if v @BETTER@ yCover[q]:
                    yCover[q] = v
                continue
            mid = (lo + hi) >> 1
            if y1 <= mid:
                if not yLeft[q]:
                    yLeft[q] = self._newY()
                todo.append((yLeft[q], lo, mid))
            if y2 > mid:
                if not yRight[q]:
                    yRight[q] = self._newY()
                todo.append((yRight[q], mid + 1, hi))
        return root

    # the @WORD@ the y-tree rooted at q (0: none) holds for y1..y2
    def _colsBest(self, q, y1, y2):
        if not q:
            return @ID@
        yLeft, yRight, yCover, yTouch = self.yLeft, self.yRight, self.yCover, self.yTouch
        res = @ID@
        todo = [(q, self.yLo, self.yHi)]
        while todo:
            q, lo, hi = todo.pop()
            if y1 <= lo and hi <= y2:
                if yTouch[q] @BETTER@ res:
                    res = yTouch[q]
                continue
            if yCover[q] @BETTER@ res:
                res = yCover[q]
            mid = (lo + hi) >> 1
            if y1 <= mid and yLeft[q]:
                todo.append((yLeft[q], lo, mid))
            if y2 > mid and yRight[q]:
                todo.append((yRight[q], mid + 1, hi))
        return res

    def _update(self, x1, y1, x2, y2, v):
        if v @BETTER@ self.best:
            self.best = v
        xLeft, xRight, xCover, xTouch = self.xLeft, self.xRight, self.xCover, self.xTouch
        todo = [(1, self.xLo, self.xHi)]
        while todo:
            p, lo, hi = todo.pop()
            xTouch[p] = self._cols(xTouch[p], y1, y2, v)
            if x1 <= lo and hi <= x2:
                xCover[p] = self._cols(xCover[p], y1, y2, v)
                continue
            mid = (lo + hi) >> 1
            for side, a, b in ((xLeft, lo, mid), (xRight, mid + 1, hi)):
                if x1 <= b and a <= x2:
                    if not side[p]:
                        side[p] = len(xCover)
                        xLeft.append(0)
                        xRight.append(0)
                        xCover.append(0)
                        xTouch.append(0)
                    todo.append((side[p], a, b))

    def _query(self, x1, y1, x2, y2):
        xLeft, xRight, xCover, xTouch = self.xLeft, self.xRight, self.xCover, self.xTouch
        res = @ID@
        todo = [(1, self.xLo, self.xHi)]
        while todo:
            p, lo, hi = todo.pop()
            if x1 <= lo and hi <= x2:
                got = self._colsBest(xTouch[p], y1, y2)
                if got @BETTER@ res:
                    res = got
                continue
            got = self._colsBest(xCover[p], y1, y2)
            if got @BETTER@ res:
                res = got
            mid = (lo + hi) >> 1
            if x1 <= mid and xLeft[p]:
                todo.append((xLeft[p], lo, mid))
            if x2 > mid and xRight[p]:
                todo.append((xRight[p], mid + 1, hi))
        return None if res == @ID@ else res

    # O(log^2 U) -- every cell with x1 <= x <= x2 and y1 <= y <= y2 becomes @WORD@(itself, v) (an empty one becomes v);
    # @RECT_RULE@
    def rectCh@WORD@(self, x1, y1, x2, y2, v):
@RECT_CHECK_U@
        self._update(x1, y1, x2, y2, v)

    # O(log^2 U) -- the cell (x, y) becomes @WORD@(itself, v) (an empty one becomes v); @POINT_RULE@
    def pointCh@WORD@(self, x, y, v):
@POINT_CHECK_U@
        self._update(x, y, x, y, v)

    # O(log^2 U) -- the value at (x, y), None if the cell is empty; @POINT_RULE@
    def pointGet(self, x, y):
@POINT_CHECK_G@
        return self._query(x, y, x, y)

    # O(log^2 U) -- @WORD@ of the set cells with x1 <= x <= x2 and y1 <= y <= y2 (None if there are none); @RECT_RULE@
    def rect@CAP@(self, x1, y1, x2, y2):
@RECT_CHECK_Q@
        return self._query(x1, y1, x2, y2)

    # O(1) -- @WORD@ of every set cell (None if there are none)
    def @WORD@All(self):
        return None if self.best == @ID@ else self.best
@CORNERS@'''

TAGS_CPP = '''
// @DOC@
// T is any integer type (int, long long, ...). Coordinates are long long.
template <typename T>
struct OnlineRectCh@WORD@Rect@CAP@2D {
    using ll = long long;
    static constexpr T @NONE@ = numeric_limits<T>::@LIMIT@();  // the @EXTREME@ value T can hold: an empty cell
    ll xLo, xHi, yLo, yHi;
    int xUsed = 2, yUsed = 1;  // how many x-nodes / y-nodes exist (the arrays are longer: they double when full)
    // x-node 0 = nothing there, 1 = the root; xCover / xTouch = its y-trees (roots, 0 = none) for the updates that cover
    // all of its x's / touch any of them
    vector<int> xLeft, xRight, xCover, xTouch;
    vector<int> yLeft, yRight;  // y-node 0 = nothing there
    vector<T> yCover, yTouch;  // the best update covering all of a y-node's y's / touching any of them
    T best = @NONE@;

    // O(1) -- every cell of [xLo, xHi] by [yLo, yHi] empty; needs xLo <= xHi and yLo <= yHi, else throws
    // invalid_argument
    OnlineRectCh@WORD@Rect@CAP@2D(ll xLo, ll xHi, ll yLo, ll yHi)
        : xLo(xLo), xHi(xHi), yLo(yLo), yHi(yHi), xLeft(64, 0), xRight(64, 0), xCover(64, 0), xTouch(64, 0) {
        if (xLo > xHi || yLo > yHi) throw invalid_argument("OnlineRectCh@WORD@Rect@CAP@2D: needs xLo <= xHi and yLo <= yHi");
        yLeft.assign(64, 0), yRight.assign(64, 0), yCover.assign(64, @NONE@), yTouch.assign(64, @NONE@);
    }

    // a new node is the next unused slot (already blank); a full array doubles
    int newX() {
        if (xUsed == (int)xLeft.size()) {
            size_t n = 2 * (size_t)xUsed;
            xLeft.resize(n, 0), xRight.resize(n, 0), xCover.resize(n, 0), xTouch.resize(n, 0);
        }
        return xUsed++;
    }

    int newY() {
        if (yUsed == (int)yLeft.size()) {
            size_t n = 2 * (size_t)yUsed;
            yLeft.resize(n, 0), yRight.resize(n, 0), yCover.resize(n, @NONE@), yTouch.resize(n, @NONE@);
        }
        return yUsed++;
    }

    static bool better(T a, T b) { return a @BETTER@ b; }

    // y-node q (covering lo..hi): y1..y2 become @WORD@(themselves, v)
    void cols(int q, ll lo, ll hi, ll y1, ll y2, T v) {
        if (better(v, yTouch[q])) yTouch[q] = v;
        if (y1 <= lo && hi <= y2) {
            if (better(v, yCover[q])) yCover[q] = v;
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

    // the @WORD@ y-node q (covering lo..hi, 0 = none) holds for y1..y2
    T colsBest(int q, ll lo, ll hi, ll y1, ll y2) const {
        if (!q) return @NONE@;
        if (y1 <= lo && hi <= y2) return yTouch[q];
        T res = yCover[q];
        ll mid = lo + (hi - lo) / 2;
        if (y1 <= mid) {
            T got = colsBest(yLeft[q], lo, mid, y1, y2);
            if (better(got, res)) res = got;
        }
        if (y2 > mid) {
            T got = colsBest(yRight[q], mid + 1, hi, y1, y2);
            if (better(got, res)) res = got;
        }
        return res;
    }

    // x-node p (covering lo..hi): the update's part of it
    void update(int p, ll lo, ll hi, ll x1, ll y1, ll x2, ll y2, T v) {
        if (!xTouch[p]) { int made = newY(); xTouch[p] = made; }
        cols(xTouch[p], yLo, yHi, y1, y2, v);
        if (x1 <= lo && hi <= x2) {
            if (!xCover[p]) { int made = newY(); xCover[p] = made; }
            cols(xCover[p], yLo, yHi, y1, y2, v);
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

    // the @WORD@ x-node p (covering lo..hi, 0 = none) holds for the rectangle
    T query(int p, ll lo, ll hi, ll x1, ll y1, ll x2, ll y2) const {
        if (!p) return @NONE@;
        if (x1 <= lo && hi <= x2) return colsBest(xTouch[p], yLo, yHi, y1, y2);
        T res = colsBest(xCover[p], yLo, yHi, y1, y2);
        ll mid = lo + (hi - lo) / 2;
        if (x1 <= mid) {
            T got = query(xLeft[p], lo, mid, x1, y1, x2, y2);
            if (better(got, res)) res = got;
        }
        if (x2 > mid) {
            T got = query(xRight[p], mid + 1, hi, x1, y1, x2, y2);
            if (better(got, res)) res = got;
        }
        return res;
    }

    // O(log^2 U) -- every cell with x1 <= x <= x2 and y1 <= y <= y2 becomes @WORD@(itself, v) (an empty one becomes v);
    // @RECT_RULE@
    void rectCh@WORD@(ll x1, ll y1, ll x2, ll y2, T v) {
@RECT_CHECK_U@
        if (better(v, best)) best = v;
        update(1, xLo, xHi, x1, y1, x2, y2, v);
    }

    // O(log^2 U) -- the cell (x, y) becomes @WORD@(itself, v) (an empty one becomes v); @POINT_RULE@
    void pointCh@WORD@(ll x, ll y, T v) {
@POINT_CHECK_U@
        if (better(v, best)) best = v;
        update(1, xLo, xHi, x, y, x, y, v);
    }

    // O(log^2 U) -- the value at (x, y), @NONE@ if the cell is empty; @POINT_RULE@
    T pointGet(ll x, ll y) const {
@POINT_CHECK_G@
        return query(1, xLo, xHi, x, y, x, y);
    }

    // O(log^2 U) -- @WORD@ of the set cells with x1 <= x <= x2 and y1 <= y <= y2 (@NONE@ if there are none); @RECT_RULE@
    T rect@CAP@(ll x1, ll y1, ll x2, ll y2) const {
@RECT_CHECK_Q@
        return query(1, xLo, xHi, x1, y1, x2, y2);
    }

    // O(1) -- @WORD@ of every set cell (@NONE@ if there are none)
    T @WORD@All() const { return best; }
@CORNERS@};
'''

CORNERS = [("LteLte", "<=", "<="), ("LteGte", "<=", ">="), ("GteLte", ">=", "<="), ("GteGte", ">=", ">=")]


def corner_box(name, lang):
    a, b = name[:3], name[3:]
    if lang == "py":
        x1, x2 = ("self.xLo", "x") if a == "Lte" else ("x", "self.xHi")
        y1, y2 = ("self.yLo", "y") if b == "Lte" else ("y", "self.yHi")
    else:
        x1, x2 = ("xLo", "x") if a == "Lte" else ("x", "xHi")
        y1, y2 = ("yLo", "y") if b == "Lte" else ("y", "yHi")
    return f"{x1}, {y1}, {x2}, {y2}"


def tags(key):
    k = KINDS[key]
    cls = f"OnlineRectCh{key}Rect{k['CAP']}2D"
    doc = sub(TAGS_DOC, **k)
    pyc, cppc = [], []
    for name, sx, sy in CORNERS:
        op = f"{key}{name}"
        pyc += ["", f"    # O(log^2 U) -- {key} of the set cells with x {sx} the given x and y {sy} the given y (None if there "
                    f"are none); {POINT_RULE.format(err='IndexError')}",
                f"    def {op}(self, x, y):", sub(POINT_CHECK_PY, OP=op), f"        return self._query({corner_box(name, 'py')})"]
        cppc += ["", f"    // O(log^2 U) -- {key} of the set cells with x {sx} the given x and y {sy} the given y ({k['NONE']} if "
                     f"there are none); {POINT_RULE.format(err='throws out_of_range')}",
                 f"    T {op}(ll x, ll y) const {{", sub(POINT_CHECK_CPP, OP=op),
                 f"        return query(1, xLo, xHi, {corner_box(name, 'cpp')});", "    }"]
    common = dict(k, RECT_RULE=RECT_RULE.format(err="IndexError"), POINT_RULE=POINT_RULE.format(err="IndexError"))
    py = sub(TAGS_PY, BOUNDS=sub(BOUNDS_PY, CLS=cls), RECT_CHECK_U=sub(RECT_CHECK_PY, OP=f"rectCh{key}"),
             POINT_CHECK_U=sub(POINT_CHECK_PY, OP=f"pointCh{key}"), POINT_CHECK_G=sub(POINT_CHECK_PY, OP="pointGet"),
             RECT_CHECK_Q=sub(RECT_CHECK_PY, OP=f"rect{k['CAP']}"), CORNERS="\n".join(pyc), **common)
    common = dict(k, RECT_RULE=RECT_RULE.format(err="throws out_of_range"),
                  POINT_RULE=POINT_RULE.format(err="throws out_of_range"))
    cpp = sub(TAGS_CPP, RECT_CHECK_U=sub(RECT_CHECK_CPP, OP=f"rectCh{key}"),
              POINT_CHECK_U=sub(POINT_CHECK_CPP, OP=f"pointCh{key}"), POINT_CHECK_G=sub(POINT_CHECK_CPP, OP="pointGet"),
              RECT_CHECK_Q=sub(RECT_CHECK_CPP, OP=f"rect{k['CAP']}"), CORNERS="\n".join(cppc) + "\n", **common)
    ops = [f"rectCh{key}", f"pointCh{key}", "pointGet", f"rect{k['CAP']}", f"{key}All"] + [f"{key}{n}" for n, _, _ in CORNERS]
    costs = {op: "log^2(U)" for op in ops}
    costs[f"{key}All"] = "1"
    memory = {"layout": "sparse", "node": "none", "tags": "yCover[8*log^2(U)] yTouch[8*log^2(U)]",
              "other": "yLeft[8*log^2(U)] yRight[8*log^2(U)] xLeft[2*log(U)] xRight[2*log(U)] xCover[2*log(U)] "
                       "xTouch[2*log(U)]",
              "note": "sizes are per update: a rectangle makes up to about 2 log U x-nodes and, in the two y-trees of "
                      "each x-node it meets, up to about 2 log U y-nodes"}
    folder = f"online-kept-tags-rect-{key}"
    args = (ops, "seg-tree-kept-tags", costs, "1", memory, "online", [("empty-cells", "yes")])
    write(folder, header(folder, "py", *args) + [""] + lines(py, doc, "#"),
          header(folder, "cpp", *args) + [""] + lines(cpp, doc, "//"))


def main():
    assign()
    for key in KINDS:
        tags(key)
    print("online tags: 3 folders")


if __name__ == "__main__":
    main()
