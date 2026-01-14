// O(21)
// Maps [L, R] -> some ordering
// 2^pow must be > max(R)
// 21: 2e6, 22: 4e6, etc.
/*
Use like:
struct Q { ... };
sort(queries.begin(), queries.end(), [](const Q& a, const Q& b) {
    return a.ord < b.ord;
});

Using mo's on hilbert order gives O(N * root Q) which is always better than O(N + Q) root N from normal Mo's. O(N * root Q) is also doable with normal Mo's using some other techniques.
*/
// ⚠️ Not optimized
long long hilbertOrder(int l, int r, int pow = 21, int rot = 0) {
    if (!pow) return 0;
    int hpow = 1 << (pow - 1);
    int seg = (l < hpow) ? ((r < hpow) ? 0 : 3) : ((r < hpow) ? 1 : 2);
    seg = (seg + rot) & 3;
    int rotateDelta[] = {3, 0, 0, 1};
    int nx = l & (hpow - 1), ny = r & (hpow - 1);
    int nrot = (rot + rotateDelta[seg]) & 3;
    long long subSize = 1LL << (2 * pow - 2);
    long long ord = seg * subSize;
    long long add = hilbertOrder(nx, ny, pow - 1, nrot);
    ord += (seg == 1 || seg == 2) ? add : (subSize - add - 1);
    return ord;
}

struct Q {
    int l;
    int r;
    int idx;
    long long ord;
};

#include <bits/stdc++.h>
using namespace std;

int main() {
    cin.tie(nullptr);
    ios::sync_with_stdio(false);
    int n, q; cin >> n >> q;
    vector<int> nums(n); for (int i = 0; i < n; i++) cin >> nums[i];
    vector<Q> qs;
    for (int i = 0; i < q; i++) {
        int l, r; cin >> l >> r; l--; r--;
        qs.push_back(Q{l, r, i, hilbertOrder(l, r)});
    }
    sort(qs.begin(), qs.end(), [](const Q& a, const Q& b) {
        return a.ord < b.ord;
    });

    vector<int> vals = nums;
    sort(vals.begin(), vals.end());
    vals.erase(unique(vals.begin(), vals.end()), vals.end());

    for (int i = 0; i < n; i++) {
        nums[i] = lower_bound(vals.begin(), vals.end(), nums[i]) - vals.begin();
    }
    vector<int> frq(vals.size(), 0);
    int activeCount = 0;


    // unordered_map<int,int> frq;
    vector<int> out(q);
    int l = qs[0].l;
    int r = qs[0].l - 1;
    for (auto [ql, qr, idx, ord] : qs) {
        while (r < qr) {
            r++;
            frq[nums[r]]++;
            if (frq[nums[r]] == 1) {
                activeCount++;
            }
        }
        while (l > ql) {
            l--;
            frq[nums[l]]++;
            if (frq[nums[l]] == 1) activeCount++;
        }
        while (l < ql) {
            frq[nums[l]]--;
            if (frq[nums[l]] == 0) {
                activeCount--;
            }
            l++;
        }
        while (r > qr) {
            frq[nums[r]]--;
            if (frq[nums[r]] == 0) {
                activeCount--;
            }
            r--;
        }
        out[idx] = activeCount;
    }
    for (auto x : out) cout << x << endl;
}
