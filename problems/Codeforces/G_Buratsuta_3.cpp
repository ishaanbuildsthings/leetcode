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

mt19937 rng(chrono::steady_clock::now().time_since_epoch().count());

int randomIndex(int L, int R) {
    return uniform_int_distribution<int>(L, R)(rng);
}

const int SAMPLES = 40;

void solve() {
    int n, q; cin >> n >> q;
    vector<int> A(n); for (int i = 0; i < n; i++) cin >> A[i];
    gp_hash_table<int, vector<int>, custom_hash> pos;
    for (int i = 0; i < n; i++) {
        pos[A[i]].push_back(i);
    }
    auto cntInRange = [&](int num, int l, int r) -> int {
        return upper_bound(pos[num].begin(), pos[num].end(), r) - lower_bound(pos[num].begin(), pos[num].end(), l);
    };
    while (q--) {
        int l, r; cin >> l >> r; l--; r--;
        vector<int> sampled(SAMPLES);
        for (int i = 0; i < SAMPLES; i++) {
            int randomI = randomIndex(l, r);
            int num = A[randomI];
            sampled[i] = num;
        }
        vector<int> res;
        int width = (r - l + 1) / 3;
        for (auto num : sampled) {
            if (find(res.begin(), res.end(), num) != res.end()) continue;
            int cnt = cntInRange(num, l, r);
            if (cnt > width) res.push_back(num);
        }
        sort(res.begin(), res.end());
        if (res.size() == 0) {
            cout << -1 << endl;
        } else {
            for (auto x : res) cout << x << " ";
            cout << endl;
        }
    }
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int t; cin >> t;
    while (t--) solve();
}