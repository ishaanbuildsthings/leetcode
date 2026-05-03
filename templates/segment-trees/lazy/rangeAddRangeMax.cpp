using ll = long long;
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

private:
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