#include <bits/stdc++.h>
using namespace std;
using ll = long long;

struct Race {
    int l, r;
    ll gain;
};

const ll NEG_INF = LLONG_MIN / 4;
struct SegTree {
    int n;
    vector<ll> tree, lazy;

    void build(vector<ll>& vals) {
        n = vals.size();
        tree.assign(4 * n, NEG_INF);
        lazy.assign(4 * n, 0);
        _build(1, 0, n - 1, vals);
    }
    void rangeAdd(int l, int r, ll val) {
        _rangeAdd(1, 0, n - 1, l, r, val);
    }
    ll queryMax(int l, int r) {
        return _query(1, 0, n - 1, l, r);
    }
    void pointAssign(int i, ll val) {
        _pointAssign(1, 0, n - 1, i, val);
    }
private:
    void _pointAssign(int v, int tl, int tr, int i, ll val) {
        if (tl == tr) { tree[v] = val; return; }
        push(v);
        int tm = (tl + tr) / 2;
        if (i <= tm) _pointAssign(2*v, tl, tm, i, val);
        else _pointAssign(2*v+1, tm+1, tr, i, val);
        tree[v] = max(tree[2*v], tree[2*v+1]);
    }
    void push(int v) {
        if (lazy[v]) {
            for (int c : {2*v, 2*v+1}) {
                tree[c] += lazy[v];
                lazy[c] += lazy[v];
            }
            lazy[v] = 0;
        }
    }
    void _build(int v, int tl, int tr, vector<ll>& vals) {
        if (tl == tr) { tree[v] = vals[tl]; return; }
        int tm = (tl + tr) / 2;
        _build(2*v, tl, tm, vals);
        _build(2*v+1, tm+1, tr, vals);
        tree[v] = max(tree[2*v], tree[2*v+1]);
    }
    void _rangeAdd(int v, int tl, int tr, int l, int r, ll val) {
        if (l > r || tl > r || tr < l) return;
        if (l <= tl && tr <= r) { tree[v] += val; lazy[v] += val; return; }
        push(v);
        int tm = (tl + tr) / 2;
        _rangeAdd(2*v, tl, tm, l, r, val);
        _rangeAdd(2*v+1, tm+1, tr, l, r, val);
        tree[v] = max(tree[2*v], tree[2*v+1]);
    }
    ll _query(int v, int tl, int tr, int l, int r) {
        if (l > r || tl > r || tr < l) return NEG_INF;
        if (l <= tl && tr <= r) return tree[v];
        push(v);
        int tm = (tl + tr) / 2;
        return max(_query(2*v, tl, tm, l, r), _query(2*v+1, tm+1, tr, l, r));
    }
};

// SAMPLE USAGE
// SegTree st;
// vector<ll> vals(nums.begin(), nums.end());
// st.build(vals);

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m; cin >> n >> m;
    vector<int> costs(n);
    for (int i = 0; i < n; i++) cin >> costs[i];
    vector<Race> races(m);
    vector<vector<Race>> byR(n);
    ll gainsByFirst = 0;
    for (int i = 0; i < m; i++) {
        int l, r, gain; cin >> l >> r >> gain; l--; r--;
        races[i].l = l;
        races[i].r = r;
        races[i].gain = gain;
        if (r == 0) {
            gainsByFirst += gain;
        }
        byR[r].push_back({l, r, gain});
    }
    // we maintain dp on a segment tree, the maximum we can gain where we have contiguously built a prefix from l... current index
    vector<ll> dp(n, 0);
    dp[0] = gainsByFirst - costs[0];
    SegTree seg;
    seg.build(dp);
    ll bestNoBuilds = 0;

    for (int r = 1; r < n; r++) {
        // if we build at this index
        ll prevMax = seg.queryMax(0, r - 1);
        prevMax = max(prevMax, bestNoBuilds);
        bestNoBuilds = max(bestNoBuilds, (ll)seg.queryMax(0, r - 1));
        seg.pointAssign(r, max(0LL, prevMax) - costs[r]); // building from r...r is just the cost to build here + our previous best
        // anything in 0...r-1 now pays more penalty to stay alive
        seg.rangeAdd(0, r - 1, -1 * costs[r]);
        for (auto& race : byR[r]) {
            int l = race.l;
            int gain = race.gain;
            seg.rangeAdd(0, l, gain);
        }
    }
    
    cout << max(bestNoBuilds, seg.queryMax(0, n - 1)) << "\n";
}