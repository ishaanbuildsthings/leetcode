#include <bits/stdc++.h>
using namespace std;

struct MinSeg {
    struct Node {
        long long mn;
    };

    int n;
    vector<Node> tree;
    vector<long long> lazy;

    MinSeg(int _n) {
        n = _n;
        tree.resize(4 * n + 5);
        lazy.assign(4 * n + 5, 0);
        build();
    }

    Node merge(const Node& left, const Node& right) {
        return Node{min(left.mn, right.mn)};
    }

    void apply(int i, long long add) {
        tree[i].mn += add;
        lazy[i] += add;
    }

    void push(int i) {
        if (lazy[i] != 0) {
            apply(2 * i, lazy[i]);
            apply(2 * i + 1, lazy[i]);
            lazy[i] = 0;
        }
    }

    void pull(int i) {
        tree[i] = merge(tree[2 * i], tree[2 * i + 1]);
    }

    void build() { _build(1, 0, n - 1); }

    void _build(int i, int tl, int tr) {
        if (tl == tr) {
            tree[i] = Node{(tl == 0 ? 0LL : (long long)4e18)};
            return;
        }
        int tm = (tl + tr) / 2;
        _build(2 * i, tl, tm);
        _build(2 * i + 1, tm + 1, tr);
        pull(i);
    }

    void rangeAdd(int l, int r, long long add) { _rangeAdd(1, 0, n - 1, l, r, add); }

    void _rangeAdd(int i, int tl, int tr, int ql, int qr, long long add) {
        if (qr < tl || tr < ql) return;
        if (ql <= tl && tr <= qr) {
            apply(i, add);
            return;
        }
        push(i);
        int tm = (tl + tr) / 2;
        _rangeAdd(2 * i, tl, tm, ql, qr, add);
        _rangeAdd(2 * i + 1, tm + 1, tr, ql, qr, add);
        pull(i);
    }

    long long queryMin(int l, int r) { return _queryMin(1, 0, n - 1, l, r); }

    long long _queryMin(int i, int tl, int tr, int ql, int qr) {
        if (qr < tl || tr < ql) return (long long)4e18;
        if (ql <= tl && tr <= qr) return tree[i].mn;
        push(i);
        int tm = (tl + tr) / 2;
        return min(
            _queryMin(2 * i, tl, tm, ql, qr),
            _queryMin(2 * i + 1, tm + 1, tr, ql, qr)
        );
    }

    // point chmin: tree[pos] = min(tree[pos], val)
    void pointChMin(int pos, long long val) { _pointChMin(1, 0, n - 1, pos, val); }

    void _pointChMin(int i, int tl, int tr, int pos, long long val) {
        if (tl == tr) {
            tree[i].mn = min(tree[i].mn, val);
            return;
        }
        push(i);
        int tm = (tl + tr) / 2;
        if (pos <= tm) _pointChMin(2 * i, tl, tm, pos, val);
        else _pointChMin(2 * i + 1, tm + 1, tr, pos, val);
        pull(i);
    }
};


const long long INF = 1000000000000000;
void solve() {
    int n; cin >> n;
    vector<int> A(n); for (int i = 0; i < n; i++) cin >> A[i];
    vector<int> costs(n); for (int i = 0; i < n; i++) cin >> costs[i];

    // We will coordinate compress the heights
    vector<int> vals = A;
    sort(vals.begin(), vals.end());
    unordered_map<int,int> cmp;
    int comp = 0;
    for (int i = 0; i < n; i++) {
        if (i > 0 && vals[i] == vals[i - 1]) continue;
        cmp[vals[i]] = comp++;
    }

    // seg[x] is the minimum cost we can have to make the previous tower size X, as we iterate on the n numbers
    // when we encounter a new number Y, for any previous X <= Y we can carry over that cost
    // for all other values to end with, we must take their preceeding best and add our new cost

    MinSeg seg = MinSeg(comp + 1);

    for (int i = 0; i < n; i++) {
        int num = A[i];
        int cost = costs[i];
        int compressed = cmp[num];
        // Any previous value <= compressed we can leech off of
        long long prevMin = seg.queryMin(0, compressed);
        // But we can also change our heigth to be any previous height
        seg.rangeAdd(0, comp, cost);
        seg.pointChMin(compressed, prevMin); 
    }

    long long out = INF;
    for (int ending = 0; ending <= comp; ending++) {
        out = min(out, seg.queryMin(ending, ending));
    }

    cout << out << endl;
    
    // Old n^2 idea, dp[value] is the min cost to make the previous number end in value
    // TLEs due to hashmap but could be optimized with some coordinate compression to be faster
    
    // unordered_map<int, long long> dp; // dp[prevNumber] = min cost to handle that previous array where the previous number was X
    // dp.reserve(n);
    // dp[0] = 0;
    // for (int i = 0; i < n; i++) {
    //     int num = A[i];
    //     int cost = costs[i];
    //     unordered_map<int, long long> ndp;
    //     ndp.reserve(n);
    //     // for every previous value, we can do nothing or set to that value
    //     for (auto& kv : dp) {
    //         int key = kv.first;
    //         long long value = kv.second;
    //         if (ndp.find(num) == ndp.end()) {
    //             ndp[num] = INF;
    //         }
    //         if (ndp.find(key) == ndp.end()) {
    //             ndp[key] = INF;
    //         }
    //         // if the previous value is <= num, we can do nothing
    //         if (key <= num) {
    //             ndp[num] = min(ndp[num], value);
    //         }
    //         // We can always set to that value
    //         ndp[key] = min(ndp[key], value + cost);
    //     }
    //     dp = move(ndp);
    // }
    // long long out = INF;
    // for (auto& kv : dp) {
    //     out = min(out, kv.second);
    // }
    // cout << out << endl;
}

int main() {
    cin.tie(nullptr);
    ios::sync_with_stdio(false);
    int t; cin >> t;
    while (t--) solve();
}