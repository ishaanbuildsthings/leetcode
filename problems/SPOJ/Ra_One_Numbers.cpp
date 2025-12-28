#include <bits/stdc++.h>
using namespace std;

using ll = long long;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int T = 0;
    cin >> T;
    for (int _ = 0; _ < T; _++) {
        ll L, R;
        cin >> L >> R;

        string strR = to_string(R);
        string strL = to_string(L);
        int diff = (int)strR.size() - (int)strL.size();
        strL = string(diff, '0') + strL;
        int n = (int)strR.size();

        int maxSurplus = 9 * n;
        int offset = maxSurplus;

        vector<vector<vector<vector<ll>>>> cache(
            n + 1,
            vector<vector<vector<ll>>>(
                2,
                vector<vector<ll>>(
                    2,
                    vector<ll>(2 * maxSurplus + 1, -1)
                )
            )
        );

        auto dp = [&](auto&& self, int i, int th, int tl, int evenSurplus) -> ll {
            if (i == (int)strR.size()) {
                return (evenSurplus == 1) ? 1LL : 0LL;
            }

            ll &memo = cache[i][th][tl][evenSurplus + offset];
            if (memo != -1) return memo;

            int ub = (!th) ? 9 : (strR[i] - '0');
            int lb = (!tl) ? 0 : (strL[i] - '0');
            ll resHere = 0;

            for (int d = lb; d <= ub; d++) {
                int nth = th && d == ub;
                int ntl = tl && d == lb;

                // 0 1 2 3 4
                // ^

                int sign = ((n - i) % 2 == 0) ? 1 : -1;
                int nEvenSurplus = evenSurplus + sign * d;
                resHere += self(self, i + 1, nth, ntl, nEvenSurplus);
            }

            memo = resHere;
            return memo;
        };

        cout << dp(dp, 0, 1, 1, 0) << "\n";
    }

    // 0 0 0 0 1 2 3 4
    // 0 1 2 3 4 5 6 7 X X
    return 0;
}


// TLE in python
// import functools
// T = int(input())
// for _ in range(T):
//     L, R = map(int, input().split())
//     strR = str(R)
//     strL = str(L)
//     diff = len(strR) - len(strL)
//     strL = '0' * diff + strL
//     n = len(strR)
//     @functools.lru_cache(maxsize=None)
//     def dp(i, th, tl, evenSurplus):
//         if i == len(strR):
//             return 1 if evenSurplus == 1 else 0
//         ub = 9 if not th else int(strR[i])
//         lb = 0 if not tl else int(strL[i])
//         resHere = 0
//         for d in range(lb, ub + 1):
//             nth = th and d == ub
//             ntl = tl and d == lb

//             # 0 1 2 3 4
//             # ^

//             sign = 1 if ((n - i) % 2 == 0) else -1
//             nEvenSurplus = evenSurplus + sign * d
//             resHere += dp(i + 1, nth, ntl, nEvenSurplus)
//         return resHere
//     print(dp(0,1,1,0,0))

// # 0 0 0 0 1 2 3 4
// # 0 1 2 3 4 5 6 7 X X