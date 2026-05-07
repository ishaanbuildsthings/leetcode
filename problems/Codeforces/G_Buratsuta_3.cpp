// SOLUTION 0, boyer moore seg tree with multiple candidates
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

#include <ext/pb_ds/assoc_container.hpp>
using namespace __gnu_pbds;

struct custom_hash {
    static uint64_t splitmix64(uint64_t x) {
        x += 0x9e3779b97f4a7c15;
        x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9;
        x = (x ^ (x >> 27)) * 0x94d049bb133111eb;
        return x ^ (x >> 31);
    }
    size_t operator()(uint64_t x) const {
        static const uint64_t FIXED_RANDOM =
            chrono::steady_clock::now().time_since_epoch().count();
        return splitmix64(x + FIXED_RANDOM);
    }
};

template<class K, class V> using hash_map = gp_hash_table<K, V, custom_hash>;
template<class K>          using hash_set = gp_hash_table<K, null_type, custom_hash>;

// unordered map is now:
// hash_map<int, vector<int>> pos;

// unordered set is now:
// hash_set<int> seen;

struct Node {
    int cand1 = -1;
    int cnt1 = 0; // indicates an empty slot
    int cand2 = -1;
    int cnt2 = 0;
};

struct Seg {
    int n;
    vector<Node> tree;
    Node _leaf(int val) {
        return {val, 1, -1, 0};
    }
    void _build(int nodeI, int tl, int tr, const vector<int>& A) {
        if (tl == tr) {
            tree[nodeI] = _leaf(A[tl]);
            return;
        }
        int tm = (tl + tr) / 2;
        _build(2 * nodeI, tl, tm, A);
        _build(2 * nodeI + 1, tm + 1, tr, A);
        _pull(nodeI);
    }
    void _pull(int nodeI) {
        tree[nodeI] = _combine(tree[2*nodeI], tree[2*nodeI + 1]);
    }
    Node _combine(const Node& a, const Node& b) {
        Node out = a;
        auto apply = [&](int num, int surplus) {
            while (surplus > 0) {
                if (out.cnt1 > 0 && out.cand1 == num) { out.cnt1 += surplus; return; }
                if (out.cnt2 > 0 && out.cand2 == num) { out.cnt2 += surplus; return; }
                if (out.cnt1 == 0) { out.cand1 = num; out.cnt1 = surplus; return; }
                if (out.cnt2 == 0) { out.cand2 = num; out.cnt2 = surplus; return; }
                int mn = min({out.cnt1, out.cnt2, surplus});
                out.cnt1 -= mn;
                out.cnt2 -= mn;
                surplus -= mn;
            }
        };
        apply(b.cand1, b.cnt1);
        apply(b.cand2, b.cnt2);
        return out;
    }
    Seg(const vector<int>& A) {
        n = A.size();
        tree.resize(4 * n);
        _build(1, 0, n - 1, A);
    }
    Node _query(int nodeI, int tl, int tr, int ql, int qr) {
        // fully inside
        if (ql <= tl && qr >= tr) {
            return tree[nodeI];
        }
        int tm = (tl + tr) / 2;
        if (qr <= tm) {
            Node left = _query(2 * nodeI, tl, tm, ql, qr);
            return left;
        } else if (ql >= tm + 1) {
            Node right = _query(2 * nodeI + 1, tm + 1, tr, ql, qr);
            return right;
        }
        Node left = _query(2 * nodeI, tl, tm, ql, qr);
        Node right = _query(2 * nodeI + 1, tm + 1, tr, ql, qr);
        return _combine(left, right);
    }
    Node query(int l, int r) {
        return _query(1, 0, n - 1, l, r);
    }
};

void solve() {
    int n, q; cin >> n >> q;
    vector<int> A(n); for (int i = 0; i < n; i++) cin >> A[i];
    hash_map<int, vector<int>> pos;
    for (int i = 0; i < n; i++) {
        pos[A[i]].push_back(i);
    }
    auto cntInRange = [&](int num, int l, int r) -> int {
        return upper_bound(pos[num].begin(), pos[num].end(), r) - lower_bound(pos[num].begin(), pos[num].end(), l);
    };
    Seg seg(A);
    while (q--) {
        int l, r; cin >> l >> r; l--; r--;
        Node out = seg.query(l, r);
        int width = r - l + 1; // need strictly more than this
        vector<int> res;
        if (out.cand1 != -1) {
            int cnt = cntInRange(out.cand1, l, r);
            if (cnt > width / 3) {
                res.push_back(out.cand1);
            }
        }
        if (out.cand2 != -1 && out.cand2 != out.cand1) {
            int cnt = cntInRange(out.cand2, l, r);
            if (cnt > width / 3) {
                res.push_back(out.cand2);
            }
        }
        if (res.size() == 0) {
            cout << -1 << '\n';
        } else {
            sort(res.begin(), res.end());
            for (auto ans : res) cout << ans << " ";
            cout << '\n';
        }
    }
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int t; cin >> t;
    while (t--) {
        solve();
    }
}


// SOLTUION 1, randomized 40 samples, each sample check how many times it occurs in the range
// #include <bits/stdc++.h>
// using namespace std;
// using ll = long long;

// #include <ext/pb_ds/assoc_container.hpp>
// using namespace __gnu_pbds;

// struct custom_hash {
//     static uint64_t splitmix64(uint64_t x) {
//         x += 0x9e3779b97f4a7c15;
//         x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9;
//         x = (x ^ (x >> 27)) * 0x94d049bb133111eb;
//         return x ^ (x >> 31);
//     }
//     size_t operator()(uint64_t x) const {
//         static const uint64_t FIXED_RANDOM =
//             chrono::steady_clock::now().time_since_epoch().count();
//         return splitmix64(x + FIXED_RANDOM);
//     }
// };

// mt19937 rng(chrono::steady_clock::now().time_since_epoch().count());

// int randomIndex(int L, int R) {
//     return uniform_int_distribution<int>(L, R)(rng);
// }

// const int SAMPLES = 40;

// void solve() {
//     int n, q; cin >> n >> q;
//     vector<int> A(n); for (int i = 0; i < n; i++) cin >> A[i];
//     gp_hash_table<int, vector<int>, custom_hash> pos;
//     for (int i = 0; i < n; i++) {
//         pos[A[i]].push_back(i);
//     }
    // auto cntInRange = [&](int num, int l, int r) -> int {
    //     return upper_bound(pos[num].begin(), pos[num].end(), r) - lower_bound(pos[num].begin(), pos[num].end(), l);
    // };
//     while (q--) {
//         int l, r; cin >> l >> r; l--; r--;
//         vector<int> sampled(SAMPLES);
//         for (int i = 0; i < SAMPLES; i++) {
//             int randomI = randomIndex(l, r);
//             int num = A[randomI];
//             sampled[i] = num;
//         }
//         vector<int> res;
//         int width = (r - l + 1) / 3;
//         for (auto num : sampled) {
//             if (find(res.begin(), res.end(), num) != res.end()) continue;
//             int cnt = cntInRange(num, l, r);
//             if (cnt > width) res.push_back(num);
//         }
//         sort(res.begin(), res.end());
//         if (res.size() == 0) {
//             cout << -1 << endl;
//         } else {
//             for (auto x : res) cout << x << " ";
//             cout << endl;
//         }
//     }
// }

// int main() {
//     ios::sync_with_stdio(false);
//     cin.tie(nullptr);
//     int t; cin >> t;
//     while (t--) solve();
// }