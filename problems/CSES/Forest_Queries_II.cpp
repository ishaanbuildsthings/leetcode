// TEMPLATE BY ISHAANBUILDSTHINGS (see my github)
//
// EXAMPLE
//   CompressedBIT2D bit(allXs, allYs);              // every coord ever point-updated
//   bit.pointAdd(x, y, +5);                         // cell += 5
//   bit.pointSet(x, y, 7);                          // cell = 7
//   bit.pointChmax(x, y, 9);                        // cell = max(cell, 9)
//   long long s = bit.rectSum(x1, y1, x2, y2);      // inclusive rectangle sum
//
// 2D Fenwick over compressed coordinates. Both axes are compressed once in the
// constructor. Write distinctX = number of DISTINCT x values after dedup, and
// distinctY likewise. The grid is distinctX by distinctY -- dense in RANK
// space, however large or sparse the raw coordinates are. Coordinates and
// values may both be negative.
//
// POINT OPS take raw coords that MUST have been passed to the constructor
// (asserted). RECTSUM takes raw bounds that need NOT appear anywhere -- they
// are binary-searched into rank space, so you can query any window, including
// bounds between two existing coords or outside the whole range. All ranges
// inclusive; inverted or empty ranges return 0.
//
// pointSet/Chmax/Chmin need to know the cell's current value, so a plain grid
// of values is kept alongside the tree; pointGet reads it. Only SUM is
// queryable over a rectangle -- max and min have no inverse, so Fenwick's
// prefix subtraction cannot recover them. Chmax/Chmin here are POINT ops that
// happen to compute a delta, NOT rectangle max/min queries.
//
// COMPLEXITY (inputCount = how many coords you hand the constructor;
// distinctX, distinctY <= inputCount):
//   build    O(inputCount log inputCount)      -- the sort and dedup
//   every op O(log distinctX * log distinctY)
//   memory   2 * (distinctX+1) * (distinctY+1) longs
//
// THE MEMORY TRAP: cost scales with distinctX * distinctY, the PRODUCT, not
// with how many points you actually store. Compression only helps if your
// points REUSE coordinates. 2000 distinct x by 2000 distinct y is 4e6 cells,
// 64 MB, fine. But 2e5 points with all-distinct x and y gives 4e10 cells and
// will not fit no matter how sparse the points are. For that case use a BIT of
// sorted vectors (offline) or sweep + 1D BIT instead of this.
#include <bits/stdc++.h>
using namespace std;
class CompressedBIT2D {
public:
    // O(inputCount log inputCount) -- pass every coord that will ever be
    // point-updated; duplicates are fine and get deduped
    CompressedBIT2D(vector<int> xs, vector<int> ys) {
        sort(xs.begin(), xs.end()); xs.erase(unique(xs.begin(), xs.end()), xs.end());
        sort(ys.begin(), ys.end()); ys.erase(unique(ys.begin(), ys.end()), ys.end());
        ax = move(xs); ay = move(ys);
        distinctX = (int)ax.size(); distinctY = (int)ay.size();
        t.assign(distinctX + 1, vector<long long>(distinctY + 1, 0));
        val.assign(distinctX + 1, vector<long long>(distinctY + 1, 0));
    }
    // O(log distinctX * log distinctY) -- cell += delta (ADDS, does not overwrite).
    // Coords must be in the tables.
    void pointAdd(int x, int y, long long delta) {
        int i = _idxX(x), j = _idxY(y);
        val[i][j] += delta;
        for (int ii = i; ii <= distinctX; ii += ii & -ii)
            for (int jj = j; jj <= distinctY; jj += jj & -jj)
                t[ii][jj] += delta;
    }
    // O(log distinctX * log distinctY) -- cell = newVal (OVERWRITES, does not add)
    void pointSet(int x, int y, long long newVal) {
        pointAdd(x, y, newVal - val[_idxX(x)][_idxY(y)]);
    }
    // O(log distinctX * log distinctY) -- cell = max(cell, v); no-op if already >= v
    void pointChmax(int x, int y, long long v) {
        long long cur = val[_idxX(x)][_idxY(y)];
        if (v > cur) pointAdd(x, y, v - cur);
    }
    // O(log distinctX * log distinctY) -- cell = min(cell, v); no-op if already <= v
    void pointChmin(int x, int y, long long v) {
        long long cur = val[_idxX(x)][_idxY(y)];
        if (v < cur) pointAdd(x, y, v - cur);
    }
    // O(1) -- current value at a cell. Coords must be in the tables.
    long long pointGet(int x, int y) const { return val[_idxX(x)][_idxY(y)]; }
    // O(log distinctX * log distinctY) -- sum over x in [x1,x2], y in [y1,y2],
    // inclusive. Bounds are raw coords and need NOT appear in the tables.
    long long rectSum(int x1, int y1, int x2, int y2) const {
        if (x1 > x2 || y1 > y2) return 0;
        int loI = _lbX(x1) - 1, hiI = _ubX(x2);   // prefix endpoints, 1-based
        int loJ = _lbY(y1) - 1, hiJ = _ubY(y2);
        if (loI >= hiI || loJ >= hiJ) return 0;
        return _pref(hiI, hiJ) - _pref(loI, hiJ) - _pref(hiI, loJ) + _pref(loI, loJ);
    }
private:
    int distinctX, distinctY;
    vector<int> ax, ay;                       // sorted unique raw coords per axis
    vector<vector<long long>> t, val;         // Fenwick tree, and plain current values
    // 1-based rank of the first coord >= v
    int _lbX(int v) const { return (int)(lower_bound(ax.begin(), ax.end(), v) - ax.begin()) + 1; }
    int _lbY(int v) const { return (int)(lower_bound(ay.begin(), ay.end(), v) - ay.begin()) + 1; }
    // 1-based rank of the last coord <= v (0 if there is none)
    int _ubX(int v) const { return (int)(upper_bound(ax.begin(), ax.end(), v) - ax.begin()); }
    int _ubY(int v) const { return (int)(upper_bound(ay.begin(), ay.end(), v) - ay.begin()); }
    // exact 1-based index; asserts the coord was declared to the constructor
    int _idxX(int v) const {
        int i = _lbX(v);
        assert(i <= distinctX && ax[i - 1] == v);
        return i;
    }
    int _idxY(int v) const {
        int j = _lbY(v);
        assert(j <= distinctY && ay[j - 1] == v);
        return j;
    }
    long long _pref(int i, int j) const {
        long long s = 0;
        for (; i > 0; i -= i & -i)
            for (int jj = j; jj > 0; jj -= jj & -jj)
                s += t[i][jj];
        return s;
    }
};

struct Query {
    int qtype;
    int x1;
    int y1;
    int x2 = -1;
    int y2 = -1;
};

int main() {
    int n, q; cin >> n >> q;
    vector<int> xs;
    vector<int> ys;
    vector<pair<int,int>> trees;
    for (int r = 0; r < n; r++) {
        string row; cin >> row;
        for (int c = 0; c < n; c++) {
            if (row[c] == '*') {
                xs.push_back(c + 1);
                ys.push_back(r + 1);
                trees.push_back({c + 1, r + 1});
            }
        }
    }
    vector<Query> queries;
    for (int i = 0; i < q; i++) {
        int qtype; cin >> qtype;
        if (qtype == 1) {
            int y, x; cin >> y >> x;
            queries.push_back(Query{1, x, y});
            xs.push_back(x);
            ys.push_back(y);
        } else {
            int y1, x1, y2, x2; cin >> y1 >> x1 >> y2 >> x2;
            queries.push_back(Query{2, x1, y1, x2, y2});
        }
    }

    CompressedBIT2D seg(xs, ys);
    for (auto [x, y] : trees) {
        seg.pointAdd(x, y, 1);
    }

    for (auto query : queries) {
        if (query.qtype == 1) {
            int existing = seg.pointGet(query.x1, query.y1);
            int newV = existing ^ 1;
            seg.pointSet(query.x1, query.y1, newV);
        } else {
            cout << seg.rectSum(query.x1, query.y1, query.x2, query.y2) << '\n';
        }
    }

}