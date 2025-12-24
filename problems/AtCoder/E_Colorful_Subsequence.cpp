#include <bits/stdc++.h>
using namespace std;

using ll = long long;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, k;
    cin >> n >> k;
    vector<int> colors;
    vector<ll> values;
    colors.reserve(n);
    values.reserve(n);
    for (int i = 0; i < n; i++) {
        int c;
        ll v;
        cin >> c >> v;
        colors.push_back(c);
        values.push_back(v);
    }

    ll NINF = -(4LL * (ll)1e18);

    vector<pair<ll,int>> best1(k + 1, {NINF, -1}); // best1[removed] is the current best (keptBallsScore, lastBallColor)
    vector<pair<ll,int>> best2(k + 1, {NINF, -1}); // best1[removed] is the current second best (keptBallsScore, lastBallWithDifferentColor)
    best1[0] = {0, -1};

    for (int i = 0; i < n; i++) {
        int color = colors[i];
        ll value = values[i];

        for (int removed = k; removed >= 0; removed--) {
            // If we keep this ball, we need to look at the previous values where we removed the same amount, and add our ball score
            ll prevBest1Score = best1[removed].first;
            int prevBest1LastColor = best1[removed].second;
            ll prevBest2Score = best2[removed].first;

            pair<ll,int> newOption;
            if (color != prevBest1LastColor) {
                ll s = (prevBest1Score == NINF ? NINF : prevBest1Score + value);
                newOption = {s, color};
            } else {
                ll s = (prevBest2Score == NINF ? NINF : prevBest2Score + value);
                newOption = {s, color};
            }

            vector<pair<ll,int>> options;
            options.push_back(newOption);

            if (removed) {
                // If we remove this ball, we need to look at previous values where we had removed 1 fewer
                options.push_back(best1[removed - 1]);
                options.push_back(best2[removed - 1]);
            }

            sort(options.begin(), options.end(), greater<pair<ll,int>>());

            best1[removed] = options[0];
            // We don't need to do best2[removed] = {NINF, -1} here, would need to think about why
            for (int i = 1; i < (int)options.size(); i++) {
                auto opt = options[i];
                if (opt.second == options[0].second) {
                    continue;
                }
                best2[removed] = opt;
                break;
            }
        }
    }

    ll ans = best1[k].first;
    if (ans == NINF) {
        cout << -1 << "\n";
    } else {
        cout << ans << "\n";
    }

    return 0;
}


// # Python version (TLE)

// n, k = map(int, input().split())
// colors = []
// values = []
// for i in range(n):
//     c, v = map(int, input().split())
//     colors.append(c)
//     values.append(v)

// NINF = -float('inf')

// best1 = [(NINF, -1)] * (k + 1) # best1[removed] is the current best (keptBallsScore, lastBallColor)
// best2 = [(NINF, -1)] * (k + 1) # best1[removed] is the current second best (keptBallsScore, lastBallWithDifferentColor)
// best1[0] = (0, -1)

// for i in range(n):
//     color = colors[i]
//     value = values[i]

//     for removed in range(k, -1, -1):
//         # If we keep this ball, we need to look at the previous values where we removed the same amount, and add our ball score
//         prevBest1Score, prevBest1LastColor = best1[removed]
//         prevBest2Score, prevBest2LastColor = best2[removed]
//         newOption = (prevBest1Score + value, color) if color != prevBest1LastColor else (prevBest2Score + value, color)

//         options = [newOption]

//         # print(f'current options with keeping this ball: {options}')

//         if removed:
//             # If we remove this ball, we need to look at previous values where we had removed 1 fewer
//             options.extend([best1[removed - 1], best2[removed - 1]])

//         options.sort(reverse=True)
//         best1[removed] = options[0]
//         # We don't need to do best2[removed] = (NINF, -1)
//         for i in range(1, len(options)):
//             opt = options[i]
//             if opt[-1] == options[0][-1]:
//                 continue
//             best2[removed] = opt
//             break

// ans = best1[k][0]
// if ans == NINF:
//     print(-1)
// else:
//     print(ans)

    

        
