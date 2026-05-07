#include <bits/stdc++.h>
using namespace std;
using ll = long long;

const int NUM_PICKS = 50;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, q; cin >> n >> q;
    vector<int> A(n);
    vector<vector<int>> pos(n + 1); // values are in [1, n]
    for (int i = 0; i < n; i++) {
        cin >> A[i];
        pos[A[i]].push_back(i);
    }

    mt19937 rng(chrono::steady_clock::now().time_since_epoch().count());

    while (q--) {
        int l, r, k; cin >> l >> r >> k; l--; r--;
        int len = r - l + 1;
        int threshold = len / k; // need strictly more than this many occurrences

        int best = -1;
        vector<int> seen;

        for (int pick = 0; pick < NUM_PICKS; pick++) {
            int idx = l + rng() % len;
            int v = A[idx];

            // skip if we already checked this value
            // bool already = false;
            // for (int s : seen) if (s == v) { already = true; break; }
            // if (already) continue;
            // seen.push_back(v);

            // count occurrences of v in [l, r]
            auto& p = pos[v];
            int cnt = upper_bound(p.begin(), p.end(), r) - lower_bound(p.begin(), p.end(), l);

            if (cnt > threshold) {
                if (best == -1 || v < best) best = v;
            }
        }

        cout << best << '\n';
    }
}