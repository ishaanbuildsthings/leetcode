#include <bits/stdc++.h>
using namespace std;
using ll = long long;


inline int readInt() {
    int x = 0; char c = getchar();
    while (c < '0' || c > '9') c = getchar();
    while (c >= '0' && c <= '9') { x = x * 10 + (c - '0'); c = getchar(); }
    return x;
}
struct FW {
    int n;
    vector<int> bit;
    int total = 0;

    void init(int sz) {
        n = sz;
        bit.assign(n + 1, 0);
        total = 0;
    }

    void add(int x) {
        total++;
        for (int i = x; i <= n; i += i & -i) bit[i]++;
    }

    void remove(int x) {
        total--;
        for (int i = x; i <= n; i += i & -i) bit[i]--;
    }

    int kth(int k) const {
        int idx = 0, pw = 1;
        while ((pw << 1) <= n) pw <<= 1;
        for (; pw; pw >>= 1) {
            int nxt = idx + pw;
            if (nxt <= n && bit[nxt] < k) { k -= bit[nxt]; idx = nxt; }
        }
        return idx + 1;
    }
};



int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int t = readInt();
    while (t--) {
        int n = readInt();
        vector<pair<int,int>> points;
        for (int i = 0; i < n; i++) {
            int x = readInt();
            int y = readInt();
            points.push_back({x, y});
        }

        // vector<vector<int>> byX(n + 1);
        vector<vector<int>> byY(n + 1);
        for (auto [x, y] : points) {
            // byX[x].push_back(y);
            byY[y].push_back(x);
        }
        for (int i = 0; i <= n; i++) {
            // sort(byX[i].begin(), byX[i].end());
            sort(byY[i].begin(), byY[i].end());
        }
        vector<int> allX;
        for (auto [x, y] : points) {
            allX.push_back(x);
        }
        sort(allX.begin(), allX.end());
        allX.erase(unique(allX.begin(), allX.end()), allX.end());
        // for (int x = 0; x <= n; x++) {
        //     if (byX[x].size()) {
        //         allX.push_back(x);
        //     }
        // }

        auto cnt = [&](int L, int R) -> int {
            auto lo = upper_bound(allX.begin(), allX.end(), L);
            auto hi = lower_bound(allX.begin(), allX.end(), R);
            return hi - lo;
        };

        // FW above;
        // FW below;
        // above.init(n + 10);
        // below.init(n + 10);
        // int aboveCnt = 0;
        // int belowCnt = 0;
        // for (auto [x, y] : points) {
        //     above.add(x);
        //     aboveCnt++;
        // }

        ll out = 0;
        vector<int> ys;
        for (int y = 0; y <= n; y++) {
            if (byY[y].size()) {
                ys.push_back(y);
            }
        }

        vector<int> belowMinL(n + 5), belowMaxL(n + 5);
        int currMin = INT_MAX;
        int currMax = INT_MIN;
        for (int i = 0; i < (int)ys.size(); i++) {
            int y = ys[i];
            currMin = min(currMin, byY[y][0]);
            currMax = max(currMax, byY[y].back());
            belowMinL[y] = currMin;
            belowMaxL[y] = currMax;
        }

        vector<int> aboveMinL(n + 5), aboveMaxL(n + 5);
        currMin = INT_MAX;
        currMax = INT_MIN;
        for (int i = ys.size() - 1; i >= 0; i--) {
            int y = ys[i];
            aboveMinL[y] = currMin;
            aboveMaxL[y] = currMax;
            currMin = min(currMin, byY[y][0]);
            currMax = max(currMax, byY[y].back());
        }

        for (int i = 0; i < ys.size() - 1; i++) {
            int y = ys[i];
            // for (auto x : byY[y]) {
            //     above.remove(x);
            //     aboveCnt--;
            //     below.add(x);
            //     belowCnt++;
            // }

            int bigL = max(aboveMinL[y], belowMinL[y]);
            int smallR = min(aboveMaxL[y], belowMaxL[y]);
            
            if (bigL < smallR) {
                out += cnt(bigL, smallR) + 1;
            }
        }

        cout << out << '\n';

    }
}