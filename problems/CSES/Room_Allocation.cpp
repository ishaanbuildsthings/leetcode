#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;

    vector<tuple<int,int,int>> segs; // holds (l, r, originalI)
    for (int i = 0; i < n; i++) {
        int l, r;
        cin >> l >> r;
        segs.push_back({l, r, i});
    }
    sort(segs.begin(), segs.end());

    priority_queue<pair<int,int>, vector<pair<int,int>>, greater<pair<int,int>>> rights; // holds (departure, roomUsed)
    vector<int> rooms;

    vector<int> res2(n);
    int res = 0;

    for (auto [l, r, i] : segs) {
        while (!rights.empty() && rights.top().first < l) {
            rooms.push_back(rights.top().second);
            rights.pop();
        }

        int nextRoom;
        if (rooms.empty()) {
            nextRoom = res + 1;
        } else {
            nextRoom = rooms.back();
            rooms.pop_back();
        }

        rights.push({r, nextRoom});
        res2[i] = nextRoom;
        res = max(res, (int)rights.size());
    }

    cout << res << endl;
    for (int i = 0; i < n; i++) {
        if (i) cout << ' ';
        cout << res2[i];
    }
    return 0;
}
