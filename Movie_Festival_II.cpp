#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, k;
    cin >> n >> k;

    vector<pair<int,int>> movies(n); // (end, start)
    for (int i = 0; i < n; i++) {
        int a, b;
        cin >> a >> b;
        movies[i] = {b, a};
    }
    sort(movies.begin(), movies.end());

    multiset<int> endTimes;
    for (int i = 0; i < k; i++) endTimes.insert(0); // everyone is available at time 0

    int ans = 0;
    for (auto [end, start] : movies) {
        auto it = endTimes.upper_bound(start); // first > start
        if (it == endTimes.begin()) continue;  // nobody free we cannot take this movie
        --it; // now *it is max <= start
        endTimes.erase(it);
        endTimes.insert(end);
        ans++;
    }

    cout << ans << "\n";
    return 0;
}


// (1, 50)
// (1, 60)
// (100, 150)
// (40, 200)