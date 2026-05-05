#include <bits/stdc++.h>
using namespace std;
using ll = long long;

struct P {
    int x, y;
};

struct Node {
    int mx = -1; // max Y in this range
};

struct Seg {
    int U; // from 0...U-1
    vector<int> maxY;
    vector<set<int>> ysAt;
    Seg(int _U) {
        U = _U;
        maxY.resize(4 * U);
        ysAt.resize(4 * U);
    }
    void _pull(int nodeI) {
        maxY[nodeI] = max(maxY[2*nodeI], maxY[2*nodeI+1]);
    }
    void _pointAdd(int nodeI, int tl, int tr, int xi, int y, bool addOrRemove) {
        if (tl == tr) {
            if (addOrRemove) {
                ysAt[nodeI].insert(y);
                maxY[nodeI] = max(maxY[nodeI], y);
            } else {
                ysAt[nodeI].erase(y);
                if (ysAt[nodeI].size() == 0) {
                    maxY[nodeI] = -1;
                } else {
                    maxY[nodeI] = *--ysAt[nodeI].end();
                }
            }
            return;
        }
        int tm = (tl + tr) / 2;
        if (xi <= tm) {
            _pointAdd(2 * nodeI, tl, tm, xi, y, addOrRemove);
        } else {
            _pointAdd(2 * nodeI + 1, tm + 1, tr, xi, y, addOrRemove);
        }
        _pull(nodeI);
    }
    void pointAdd(int i, int y, bool addOrRemove) {
        _pointAdd(1, 0, U - 1, i, y, addOrRemove);
    }
    // find the smallest Y > y for some tree coordinate > X
    pair<int,int> _walk(int nodeI, int xl, int xr, int x, int y) {
        // out of bounds
        if (xr <= x) return {-1, -1};
        // walk prune
        if (maxY[nodeI] <= y) return {-1, -1};
        if (xl == xr) {
            int smallestYGreaterThany = *ysAt[nodeI].upper_bound(y);
            // we hit a leaf, so we can just get the biggest Y
            return {xl, smallestYGreaterThany};
        }
        int xm = (xl + xr) / 2;

        // option 1, if we can go left we should
        if (xm > x) {
            auto leftRes = _walk(2 * nodeI, xl, xm, x, y);
            if (leftRes.second != -1) return leftRes;
            auto rightRes = _walk(2 * nodeI + 1, xm + 1, xr, x, y);
            return rightRes;
        }
        // otherwise we must go right
        auto rightRes = _walk(2 * nodeI + 1, xm + 1, xr, x, y);
        return rightRes;
    }
    // gets the smallest X >= x, and the largest Y at that X
    pair<int,int> walk(int x, int y) {
        return _walk(1, 0, U - 1, x, y);
    }
};

struct Query {
    string qtype; // "add", "find", "remove"
    int x;
    int y;
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n; cin >> n;
    vector<P> points(n);
    vector<Query> queries;
    for (int i = 0; i < n; i++) {
        string qtype; cin >> qtype;
        int x, y; cin >> x >> y;
        Query quer = {qtype, x, y};
        queries.push_back(quer);
        points[i].x = x;
        points[i].y = y;
    }
    vector<int> xs;
    for (auto& p : points) xs.push_back(p.x);
    sort(xs.begin(), xs.end());
    xs.erase(unique(xs.begin(), xs.end()), xs.end());
    unordered_map<int,int> cmp; // maps x -> compressed idx
    for (int i = 0; i < xs.size(); i++) {
        int x = xs[i];
        cmp[x] = i;
    }
    int U = xs.size(); // size of compressed universe
    Seg seg(U);
    for (int i = 0; i < queries.size(); i++) {
        Query quer = queries[i];
        if (quer.qtype == "add") {
            seg.pointAdd(cmp[quer.x], quer.y, true);
        } else if (quer.qtype == "remove") {
            seg.pointAdd(cmp[quer.x], quer.y, false);
        } else {
            auto pair = seg.walk(cmp[quer.x], quer.y);
            if (pair.second == -1) {
                cout << -1 << '\n';
            } else {
                cout << xs[pair.first] << " " << pair.second << endl;
            }
        }
    }
}