"""Online (nothing known up front), rectangle chmax with point reads (and chmin): a tree of trees whose tags stay put.

    python3 gen_tags_points.py     # writes range-queries-2d/online-kept-tags-<max|min>/template.{py,cpp}

A rectangle chmax is stored at the O(log^2) nodes that make up the rectangle and never pushed down (a tree of trees
can't push down its outer tree, and chmax doesn't need it); a point read collects the tags on its O(log^2) nodes. This
covers rectChmax + pointGet. Rectangle chmax together with rectangle max over sparse points is the k-d tree's (no
log^2 structure: the tags of an outer node would have to be checked against the points of each x-range below it).
"""
from lib2d import header, write

KINDS = {
    "max": {"cap": "Max", "better": ">", "id_py": "NEG", "inf": "-inf", "none_cpp": "NO_MAX", "limit": "lowest", "word": "max"},
    "min": {"cap": "Min", "better": "<", "id_py": "POS", "inf": "inf", "none_cpp": "NO_MIN", "limit": "max", "word": "min"},
}


def fill(text, k):
    for key, val in (("CAP", k["cap"]), ("BETTER", k["better"]), ("IDPY", k["id_py"]), ("INF", k["inf"]),
                     ("NONE", k["none_cpp"]), ("LIMIT", k["limit"]), ("EXTREME", "smallest" if k["limit"] == "lowest" else "largest"), ("WORD", k["word"])):
        text = text.replace(f"@{key}@", val)
    return text.strip("\n").split("\n")


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
    static constexpr T @NONE@ = numeric_limits<T>::@LIMIT@();  // the @EXTREME@ value T can hold: a cell no update has reached
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
        emit(f"online-kept-tags-{key}", "online", ops, {upd: "log^2(U)", pupd: "log^2(U)", "pointGet": "log^2(U)"}, "1",
             {"layout": "sparse", "node": "none", "tags": "tag[4*log^2(U)]", "other": "yLeft[4*log^2(U)] yRight[4*log^2(U)] "
              "xLeft[2*log(U)] xRight[2*log(U)] xTree[2*log(U)]",
              "note": "sizes are per update: a rectangle makes up to about 2 log U x-nodes and, in each of the O(log U) it "
                      "tags, up to about 2 log U y-nodes"},
             fill(ONLINE_PY, k), fill(ONLINE_CPP, k))
    print("kept tags online: 2 folders")


if __name__ == "__main__":
    main()
