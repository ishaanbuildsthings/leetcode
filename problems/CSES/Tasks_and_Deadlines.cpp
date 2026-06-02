#include <bits/stdc++.h>
using namespace std;
using ll = long long;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n; cin >> n;
    ll res = 0;
    vector<pair<int,int>> tasks; // duration, deadline
    for (int i = 0; i < n; i++) {
        int dur, dead; cin >> dur >> dead;
        tasks.push_back({dur, dead});
        res += dead;
    }
    sort(tasks.begin(), tasks.end());
    ll finishTime = 0;
    for (auto [dur, dead] : tasks) {
        finishTime += dur;
        res -= finishTime;
    }
    cout << res;
}