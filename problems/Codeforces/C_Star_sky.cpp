#include <bits/stdc++.h>
using namespace std;

// struct Star {
//     int x, y, s;
// };

struct Query {
    int t, x1, y1, x2, y2;
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, q, c; cin >> n >> q >> c;
    // vector<Star> stars(n);
    int cnt[101][101][11] = {}; // cnt[x][y][ctype]
    for (int i = 0; i < n; i++) {
        int x, y, s; cin >> x >> y >> s;
        cnt[x][y][s]++;
        // cin >> stars[i].x >> stars[i].y >> stars[i].s;
    }
    vector<Query> queries(q);
    
    for (int i = 0; i < q; i++) {
        cin >> queries[i].t >> queries[i].x1 >> queries[i].y1 >> queries[i].x2 >> queries[i].y2;
    }
    // unordered_map<tuple<int,int,int>,int> cnt; // maps (x, y, c) -> count in that space
    // for (Star star : stars) {
    //     cnt[{star.x, star.y, star.s}]++;
    // }

    // pf[x][y][c] is the # of stars with that brightness from 1...x 1...y
    vector<vector<vector<int>>> pf(101, vector<vector<int>>(101, vector<int>(11, 0)));
    for (int ctype = 0; ctype <= c; ctype++) {
        for (int y = 1; y <= 100; y++) {
            for (int x = 1; x <= 100; x++) {
                int cntHere = cnt[x][y][ctype];
                int below = y > 1 ? pf[x][y-1][ctype] : 0;
                int left = x > 1 ? pf[x-1][y][ctype] : 0;
                int belowLeft = (x > 1 && y > 1) ? pf[x-1][y-1][ctype] : 0;
                int finalValue = cntHere + below + left - belowLeft;
                pf[x][y][ctype] = finalValue;
            }
        }
    }


    for (auto& q : queries) {
        int res = 0;
        for (int initC = 0; initC <= c; initC++) {
            int newC = (initC + q.t) % (c + 1);
            // cerr << "init c: " << initC << " newC: " << newC << " at time: " << q.t << endl;
            int amount = pf[q.x2][q.y2][initC];
            // cerr << "init amount: " << amount << endl;
            if (q.x1 > 1) {
                int left = pf[q.x1-1][q.y2][initC];
                amount -= left;
            }
            if (q.y1 > 1) {
                int below = pf[q.x2][q.y1-1][initC];
                amount -= below;
            }
            if (q.x1 > 1 && q.y1 > 1) {
                int belowLeft = pf[q.x1-1][q.y1-1][initC];
                amount += belowLeft;
            }
            // cerr << "amount: " << amount << endl;
            res += amount * newC;
        }
        cout << res << endl;
    }


}