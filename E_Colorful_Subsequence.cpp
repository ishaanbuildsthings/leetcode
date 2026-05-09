
// bottom up version
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, k; cin >> n >> k;
    vector<int> C(n);
    vector<int> V(n);
    for (int i = 0; i < n; i++) {
        cin >> C[i] >> V[i];
    }
    const ll NEG = LLONG_MIN / 4;
    vector<ll> score1(k + 1, NEG), score2(k + 1, NEG);
    vector<int> color1(k + 1, -1), color2(k + 1, -2);
    vector<ll> nscore1(k + 1, NEG), nscore2(k + 1, NEG);
    vector<int> ncolor1(k + 1, -1), ncolor2(k + 1, -2);
    score1[0] = 0;
    score2[0] = 0;

    for (int i = 0; i < n; i++) {
        int c = C[i];
        int v = V[i];
        fill(nscore1.begin(), nscore1.end(), NEG);
        fill(nscore2.begin(), nscore2.end(), NEG);
        fill(ncolor1.begin(), ncolor1.end(), -1);
        fill(ncolor2.begin(), ncolor2.end(), -2);
        for (int nremoved = 0; nremoved <= k; nremoved++) {
            vector<pair<ll,int>> options; // holds (score, color)
            // we could remove this ball, forwarding the previous options
            if (nremoved) {
                options.push_back({score1[nremoved - 1], color1[nremoved - 1]});
                options.push_back({score2[nremoved - 1], color2[nremoved - 1]});
            }
            // we could keep this ball
            if (c != color1[nremoved]) {
                options.push_back({score1[nremoved] == NEG ? score1[nremoved] : score1[nremoved] + v, c});
            }
            if (c != color2[nremoved]) {
                options.push_back({score2[nremoved] == NEG ? score2[nremoved] : score2[nremoved] + v, c});
            }

            // sort(options.begin(), options.end(), greater<>());
            ll bestScore = NEG;
            int bestColor = -1;
            for (auto& [scr, col] : options) {
                if (scr > bestScore) {
                    bestScore = scr;
                    bestColor = col;
                }
            }

            ll bestScore2 = NEG;
            int bestColor2 = -2;
            for (auto& [scr, col] : options) {
                if (col != bestColor) {
                    if (scr > bestScore2) {
                        bestScore2 = scr;
                        bestColor2 = col;
                    }
                }
            }
            
            nscore1[nremoved] = bestScore;
            ncolor1[nremoved] = bestColor;
            nscore2[nremoved] = bestScore2;
            ncolor2[nremoved] = bestColor2;
        }
        swap(score1, nscore1);
        swap(score2, nscore2);
        swap(color1, ncolor1);
        swap(color2, ncolor2);
    }
    ll ans = score1[k];
    if (ans == NEG) {
        cout << -1 << endl;
    } else {
        cout << ans << endl;
    }

}



// top down version, failed because i used like 3gb of memory lol
// #include <bits/stdc++.h>
// using namespace std;
// using ll = long long;

// const int MAX_N = 200000;
// const int MAX_K = 500;
// tuple<ll,ll,ll,ll> cache[MAX_N + 20][MAX_K + 20]; // cache[i][removed] -> (bestScore, nextColorForThatScore), (bestScore2, nextColorForSecondScore)
// bool valid[MAX_N + 20][MAX_K + 20];

// int main() {
//     ios::sync_with_stdio(false);
//     cin.tie(nullptr);
//     int n, k; cin >> n >> k;
    // vector<int> C(n);
    // vector<int> V(n);
    // for (int i = 0; i < n; i++) {
    //     cin >> C[i] >> V[i];
    // }
//     for (int i = 0; i < n + 5; i++)
//         for (int j = 0; j < k + 5; j++)
//         valid[i][j] = false;

//     auto dp = [&](auto&& self, int i, int removed) -> tuple<ll,ll,ll,ll> {
//         // base case
//         if (i == n) {
//             if (removed == k) return {0, -1, 0, -2};
//             return {LLONG_MIN, 0, LLONG_MIN, 0};
//         }
        
//         if (valid[i][removed]) return cache[i][removed];

//         vector<pair<ll,ll>> options;

//         // if we can remove, then it would just be the next indices' answers with 1 removal gained
//         if (removed < k) {
//             auto [s1, c1, s2, c2] = self(self, i + 1, removed + 1);
//             options.push_back({s1, c1});
//             options.push_back({s2, c2});
//         }

//         // if we keep this, we need to inspect the next state and see what to use
//         auto [s1, c1, s2, c2] = self(self, i + 1, removed);
//         // if the next best state wants to use our color, we fall back to second best
//         if (C[i] == c1) {
//             options.push_back({s2 == LLONG_MIN ? LLONG_MIN : s2 + V[i], (ll)C[i]});
//         } else {
//             options.push_back({s1 == LLONG_MIN ? LLONG_MIN : s1 + V[i], (ll)C[i]});
//         }

//         sort(options.begin(), options.end(), greater<pair<ll,ll>>());

//         pair<ll,ll> best2 = {LLONG_MIN, 0};
//         for (int j = 1; j < options.size(); j++) {
//             if (options[j].second != options[0].second) {
//                 best2 = options[j];
//                 break;
//             }
//         }
//         valid[i][removed] = true;
//         cache[i][removed] = {options[0].first, options[0].second, best2.first, best2.second};

//         return cache[i][removed];
//     };

//     auto ans = dp(dp, 0, 0);
//     if (get<0>(ans) < 0) {
//         cout << -1 << endl;
//     } else {
//         cout << get<0>(ans) << endl;
//     }
// }