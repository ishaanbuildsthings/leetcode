#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, k; cin >> n >> k;
    vector<pair<int,int>> movies;
    for (int i = 0; i < n; i++) {
        int a, b; cin >> a >> b;
        movies.push_back({a, b});
    }
    multiset<int> last; for (int i = 0; i < k; i++) last.insert(0);
    sort(movies.begin(), movies.end(), [&](const pair<int,int>& a, const pair<int,int>& b) {
        if (a.second <= b.second) {
            return true;
        }
        return false;
    });
    int res = 0;
    for (auto p : movies) {
        // find largest ending <= our start
        auto it = last.upper_bound(p.first); // first element >= start
        if (it == last.begin()) continue;
        auto prevVal = *prev(it);
        last.extract(prevVal);
        last.insert(p.second);
        res++;
    }
    cout << res;
}