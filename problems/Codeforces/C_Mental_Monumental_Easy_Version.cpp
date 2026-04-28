#include <bits/stdc++.h>
#include <ext/pb_ds/assoc_container.hpp>
#include <ext/pb_ds/tree_policy.hpp>
using namespace std;
using namespace __gnu_pbds;
template<class T>
using orderedSet = tree<T, null_type, less<T>, rb_tree_tag, tree_order_statistics_node_update>;

int getReach(int v) {
    if (v == 0) {
        return 0;
    }
    if (v % 2 == 0) {
        int reach = (v / 2) - 1;
        return reach;
    }
    return v / 2;
}

void solve() {
    int n;
    cin >> n;
    vector<int> arr(n);
    for (int i = 0; i < n; i++) cin >> arr[i];

    vector<pair<int,int>> ranges; // holds (original number, reach from 0)
    for (int v : arr) {
        if (v == 0) {
            ranges.push_back({0, 0});
            continue;
        }
        if (v % 2 == 0) {
            ranges.push_back({v, getReach(v)});
        } else {
            ranges.push_back({v, getReach(v)});
        }
    }
    sort(ranges.begin(), ranges.end());

    auto canMex = [&](int mex) -> bool {
        if (mex == 0) {
            return true;
        }

        vector<int> numberStore(mex);

        // maps free singles -> count
        // unordered_map<int,int> numberStore;
        // stores sorted reach ranges
        orderedSet<pair<int,int>> reachList;
        int idx = 0;
        for (auto [orig, reach] : ranges) {
            if (orig < mex) {
                numberStore[orig] += 1;
            }
            reachList.insert({reach, idx});
            idx += 1;
        }

        for (int x = mex - 1; x >= 0; x--) {
            // if we have this in the number store, just use it and lose the reach
            if (numberStore[x] > 0) {
                numberStore[x] -= 1;
                int r = getReach(x);
                auto it = reachList.lower_bound({r, 0});
                reachList.erase(it);
                continue;
            }
            // if we have no reach list or the last is too small we fail
            if ((int)reachList.size() == 0 || reachList.find_by_order(reachList.size() - 1)->first < x) {
                return false;
            }

            reachList.erase(prev(reachList.end()));
        }

        return true;
    };

    // what is the largest mex we can get
    int l = 0;
    int r = n + 1;
    int res = 0;
    while (l <= r) {
        int m = (r + l) / 2;
        if (canMex(m)) {
            res = m;
            l = m + 1;
        } else {
            r = m - 1;
        }
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