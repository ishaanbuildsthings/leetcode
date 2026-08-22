#include <bits/stdc++.h>
using namespace std;

// TEMPLATE BY ISHAANBUILDSTHINGS (see my github)
//
// EXAMPLE
//   StaticValueRangeSum vrs(A);
//   long long s = vrs.sumValsInValRange(l, r, lowVal, highVal);  // lowVal <= A[i] <= highVal
//   long long t = vrs.sumValsLteX(l, r, X);                      // X need not appear in A
//   long long c = vrs.cntValsLtX(l, r, X);
//
// Static array, offline or online queries. Values are compressed once in the
// constructor; query bounds are binary-searched into the compressed domain, so
// nothing depends on the value magnitude -- all costs are log n, not log U.
//
// Persistent sum segtree over value ranks; version p = histogram of A[0..p-1].
// Index range [l,r] comes from subtracting versions r+1 and l; the value window
// comes from the tree query. Index range always inclusive. Empty/inverted
// ranges return 0.
//
// Naming: sumVals* adds up the A[i] themselves, cntVals* counts how many there
// are. Lte/Gte are inclusive, Lt/Gt strict. InValRange is inclusive both ends.
//
// Build O(n log n) time and nodes. Query O(log n). ~20 bytes/node, so n = 2e5
// is ~72 MB -- delete C/cntVals* if you only need sums and want 20% back.
#include <bits/stdc++.h>
using namespace std;
// TEMPLATE BY ISHAANBUILDSTHINGS (see my github)
//
// EXAMPLE
//   StaticValueRangeSum vrs(A);
//   long long s = vrs.sumValsInValRange(l, r, lowVal, highVal);  // lowVal <= A[i] <= highVal
//   long long t = vrs.sumValsLteX(l, r, X);                      // X need not appear in A
//   long long c = vrs.cntValsLtX(l, r, X);
//
// Static array, offline or online queries. Values are compressed once in the
// constructor; query bounds are binary-searched into the compressed domain, so
// nothing depends on the value magnitude -- all costs are log n, not log U.
//
// Persistent sum segtree over value ranks; version p = histogram of A[0..p-1].
// Index range [l,r] comes from subtracting versions r+1 and l; the value window
// comes from the tree query. Index range always inclusive. Empty/inverted
// ranges return 0.
//
// Naming: sumVals* adds up the A[i] themselves, cntVals* counts how many there
// are. Lte/Gte are inclusive, Lt/Gt strict. InValRange is inclusive both ends.
//
// A holds ints, but VALUE BOUNDS ARE long long -- pass an accumulated sum or
// anything past 2^31 directly, no clamping needed. Index args stay int.
//
// Build O(n log n) time and nodes. Query O(log n). ~20 bytes/node, so n = 2e5
// is ~72 MB -- delete C/cntVals* if you only need sums and want 20% back.
#include <bits/stdc++.h>
using namespace std;
class StaticValueRangeSum {
public:
    // O(n log n)
    explicit StaticValueRangeSum(const vector<int>& A) : n((int)A.size()) {
        srt = A;
        sort(srt.begin(), srt.end());
        srt.erase(unique(srt.begin(), srt.end()), srt.end());
        m = (int)srt.size();
        L.push_back(0); R.push_back(0); S.push_back(0); C.push_back(0);  // node 0 = null
        root.assign(n + 1, 0);
        if (m == 0) return;
        int depth = 1; while ((1 << depth) < m) depth++;
        int cap = n * (depth + 2) + 1;
        L.reserve(cap); R.reserve(cap); S.reserve(cap); C.reserve(cap);
        for (int i = 0; i < n; i++)
            root[i + 1] = _add(root[i], 0, m - 1, _lb(A[i]), A[i]);
    }
    // ---- sums of the values themselves, over i in [l,r] ----
    // O(log n) -- lowVal <= A[i] <= highVal
    long long sumValsInValRange(int l, int r, long long lowVal, long long highVal) const {
        return _ranks(l, r, _lb(lowVal), _ub(highVal) - 1).first;
    }
    long long sumValsLteX(int l, int r, long long X) const { return _ranks(l, r, 0, _ub(X) - 1).first; }
    long long sumValsLtX (int l, int r, long long X) const { return _ranks(l, r, 0, _lb(X) - 1).first; }
    long long sumValsGteX(int l, int r, long long X) const { return _ranks(l, r, _lb(X), m - 1).first; }
    long long sumValsGtX (int l, int r, long long X) const { return _ranks(l, r, _ub(X), m - 1).first; }
    long long sumValsAll (int l, int r)              const { return _ranks(l, r, 0, m - 1).first; }
    // ---- counts of how many such i ----
    // O(log n) -- lowVal <= A[i] <= highVal
    long long cntValsInValRange(int l, int r, long long lowVal, long long highVal) const {
        return _ranks(l, r, _lb(lowVal), _ub(highVal) - 1).second;
    }
    long long cntValsLteX(int l, int r, long long X) const { return _ranks(l, r, 0, _ub(X) - 1).second; }
    long long cntValsLtX (int l, int r, long long X) const { return _ranks(l, r, 0, _lb(X) - 1).second; }
    long long cntValsGteX(int l, int r, long long X) const { return _ranks(l, r, _lb(X), m - 1).second; }
    long long cntValsGtX (int l, int r, long long X) const { return _ranks(l, r, _ub(X), m - 1).second; }
    long long cntValsAll (int l, int r)              const { return _ranks(l, r, 0, m - 1).second; }
private:
    int n, m;
    vector<int> srt, root, L, R, C;
    vector<long long> S;
    // first rank with value >= v (comparison promotes to long long, so v may exceed int range)
    int _lb(long long v) const { return (int)(lower_bound(srt.begin(), srt.end(), v) - srt.begin()); }
    // first rank with value > v
    int _ub(long long v) const { return (int)(upper_bound(srt.begin(), srt.end(), v) - srt.begin()); }
    int _new(int l, int r, long long s, int c) {
        L.push_back(l); R.push_back(r); S.push_back(s); C.push_back(c);
        return (int)S.size() - 1;
    }
    int _add(int node, int nl, int nh, int rk, long long w) {
        if (nl == nh) return _new(0, 0, S[node] + w, C[node] + 1);
        int mid = nl + (nh - nl) / 2;
        int lc = L[node], rc = R[node];
        if (rk <= mid) lc = _add(lc, nl, mid, rk, w);
        else           rc = _add(rc, mid + 1, nh, rk, w);
        return _new(lc, rc, S[lc] + S[rc], C[lc] + C[rc]);
    }
    // rank window already resolved; diff versions r+1 and l
    pair<long long, long long> _ranks(int l, int r, int lo, int hi) const {
        if (m == 0 || l > r || l < 0 || r >= n || lo > hi) return {0, 0};
        return _q(root[r + 1], root[l], 0, m - 1, lo, hi);
    }
    pair<long long, long long> _q(int a, int b, int nl, int nh, int lo, int hi) const {
        if (nh < lo || hi < nl) return {0, 0};
        if (lo <= nl && nh <= hi) return {S[a] - S[b], (long long)(C[a] - C[b])};
        int mid = nl + (nh - nl) / 2;
        auto x = _q(L[a], L[b], nl, mid, lo, hi);
        auto y = _q(R[a], R[b], mid + 1, nh, lo, hi);
        return {x.first + y.first, x.second + y.second};
    }
};
#include<bits/stdc++.h>
using namespace std;
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, q; cin >> n >> q;
    vector<int> A(n); for (int i = 0; i < n; i++) cin >> A[i];
    vector<pair<int,int>> Q(q);
    for (int i = 0; i < q; i++) {
        int l, r; cin >> l >> r; l--; r--;
        Q[i]= {l, r};
    }
    StaticValueRangeSum seg(A);
    for (auto [ql, qr] : Q) {
        long long absorbed = 0; // we absorbed up to this amount
        long long acc = 0;
        while (true) {
            long long gain = seg.sumValsInValRange(ql, qr, absorbed + 1, acc + 1);
            if (gain == 0) break;
            absorbed = acc + 1;
            acc += gain;
        }
        cout << (acc + 1) << '\n';
    }
}