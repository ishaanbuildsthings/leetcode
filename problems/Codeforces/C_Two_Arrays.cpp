#include <bits/stdc++.h>
using namespace std;
#define LOCAL_DEBUG
#define print_op(...) ostream& operator<<(ostream& out, const __VA_ARGS__& u)
#define db(val) "["#val" = "<<(val)<<"] "
#define CONCAT_(x, y) x##y
#define CONCAT(x, y) CONCAT_(x, y)
#ifdef LOCAL_DEBUG
#   define clog cerr << setw(__db_level * 2) << setfill(' ') << "" << setw(0)
#   define DB() debug_block CONCAT(dbbl, __LINE__)
    int __db_level = 0;
    struct debug_block {
        debug_block() { clog << "{" << endl; ++__db_level; }
        ~debug_block() { --__db_level; clog << "}" << endl; }
    };
#else
#   define clog if (0) cerr
#   define DB(...)
#endif

constexpr int MOD = 1000000007;
using ll = long long;

// SOLUTION 1, prefix dp for pf[prevA][prevB], O(m * n^2) time and the prefix is very trippy
// int main() {
//     ios::sync_with_stdio(false);
//     cin.tie(nullptr);
//     int n, m; cin >> n >> m;
//     vector<vector<ll>> cache(n + 1, vector<ll>(n + 1, 0)); // cache[prevA][prevB]

//     // seed the first elements placed
//     for (int a = 1; a <= n; a++)
//         for (int b = n; b >= a; b--)
//             cache[a][b] = 1;

//     for (int i = 1; i < m; i++) {
//         vector<vector<ll>> pf(n + 2, vector<ll>(n + 2, 0)); // pf[prevA][prevB] is the answer for all 1...prevA and m...prevB options

//         for (int a = 1; a <= n; a++) {
//             for (int b = n; b >= a; b--) {
//                 pf[a][b] = (cache[a][b] + pf[a - 1][b] + pf[a][b + 1] - pf[a - 1][b + 1]) % MOD;
//                 if (pf[a][b] < 0) pf[a][b] += MOD;
//             }
//         }
//         for (int a = 1; a <= n; a++) {
//             for (int b = n; b >= a; b--) {
//                 cache[a][b] = pf[a][b];
//             }
//         }
//     }

//     long long out = 0;
//     for (int a = 1; a <= n; a++) {
//         for (int b = 1; b <= n; b++) {
//             out += cache[a][b];
//             out %= MOD;
//         }
//     }

//     cout << out << endl;
// }


// SOLUTION 2
// A is basically going up, B is going down, and A never crosses B, so if we reverse B it's like forming a 2*m length chain going up
// Now dp is just dp(i, prevNum) which is 2*m*n states and an inner n loop
// int main() {
//     ios::sync_with_stdio(false);
//     cin.tie(nullptr);
//     int n, m; cin >> n >> m;
//     int MOD = 1000000007;
//     vector<int> dp(n + 1, 0); // dp[prevNum]
//     dp[1] = 1;
//     for (int i = 0; i < 2 * m; i++) {
//         vector<int> ndp(n + 1, 0);
//         for (int prevNum = 1; prevNum <= n; prevNum++) {
//             for (int newNum = prevNum; newNum <= n; newNum++) {
//                 ndp[newNum] += dp[prevNum];
//                 ndp[newNum] %= MOD;
//             }
//         }
//         dp = move(ndp);
//     }
//     long long out = 0;
//     for (auto v : dp) {
//         out += v;
//         out %= MOD;
//     }
//     cout << out << '\n';
// }


// SOLUTION 3
// The above, but we use a prefix dp to drop a loop
// O(2 * m * n)
// int main() {
//     ios::sync_with_stdio(false);
//     cin.tie(nullptr);
//     int n, m; cin >> n >> m;
//     int MOD = 1000000007;
//     vector<int> dp(n + 1, 0); // dp[prevNum]
//     dp[1] = 1;
//     for (int i = 0; i < 2 * m; i++) {
//         vector<int> pf(n + 1, 0);
//         int curr = 0;
//         for (int z = 0; z < n + 1; z++) {
//             int v = dp[z];
//             curr += v;
//             curr %= MOD;
//             pf[z] = curr;
//         }

//         for (int newNum = 1; newNum <= n; newNum++) {
//             dp[newNum] = pf[newNum];
//         }
//     }
//     long long out = 0;
//     for (auto v : dp) {
//         out += v;
//         out %= MOD;
//     }
//     cout << out << '\n';
// }
