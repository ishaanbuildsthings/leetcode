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


void solve() {
    // cout << "=========" << endl;
    int n; cin >> n;
    vector<int> A(n); for (int i = 0; i < n; i++) cin >> A[i];

    hash_map<int, int> ops; // maps number -> total ops used to reach that
    hash_map<int, int> occs; // maps number -> occurrences in original array elements
    for (auto v : A) {
        vector<int> outputs;
        int steps = 0;
        if (v == 1) {
            outputs.push_back(1);
            outputs.push_back(2);
            ops[2]++;
        } else {
            while (true) {
                outputs.push_back(v);
                ops[v] += steps;
                if (v == 1) break;
                if (v % 2) {
                    v++;
                } else {
                    v /= 2;
                }
                steps++;
            }
        }
        // cout << "outputs is: " << endl;
        // for (auto z : outputs) cout << z << " ";
        // cout << endl;
        sort(outputs.begin(), outputs.end());
        outputs.erase(unique(outputs.begin(), outputs.end()), outputs.end());
        for (auto x : outputs) occs[x]++;
    }
    int res = INT_MAX;
    for (auto [k, v] : occs) {
        if (v != n) continue;
        res = min(res, ops[k]);
    }
    cout << res << '\n';
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int t; cin >> t;
    while (t--) {
        solve();
    }
}