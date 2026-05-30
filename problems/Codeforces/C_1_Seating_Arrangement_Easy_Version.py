# SOLUTION 1, enumerate all possible counts of introverts used, O(n^2)
# def solve():
#     # print('=========================')
#     n, tables, seats = map(int, input().split())
#     s = input()
#     # print(f'{s=}')
#     iCount = s.count('I')
#     # print(f'{iCount=}')

#     def forI(I):
#         full = 0
#         empty = tables
#         partials = []
#         iStarted = 0
#         for i, v in enumerate(s):
#             if v == 'E':
#                 if partials:
#                     partials[-1] += 1
#                     if partials[-1] == seats:
#                         partials.pop()
#                         full += 1
#             elif v == 'I':
#                 if iStarted < I and empty:
#                     empty -= 1
#                     iStarted += 1
#                     partials.append(1)
#                     if seats == 1:
#                         partials.pop()
#                         full += 1
#             else:
#                 iReserved = I - iStarted
#                 remainEmpty = empty - iReserved
#                 if remainEmpty > 0:
#                     empty -= 1
#                     partials.append(1)
#                     if seats == 1:
#                         partials.pop()
#                         full += 1
#                 else:
#                     if partials:
#                         partials[-1] += 1
#                         if partials[-1] == seats:
#                             partials.pop()
#                             full += 1
#         placed = full * seats
#         for part in partials:
#             placed += part
#         return placed


#     res = 0
#     for tryI in range(iCount + 1):
#         res = max(res, forI(tryI))
    
#     print(res)




# t = int(input())
# for _ in range(t):
#     solve()



# SOLUTION 2, pull knapsack dp
# #include <bits/stdc++.h>
# using namespace std;
# using ll = long long;

# const int NINF = -1 * (INT_MAX / 4);

# void solve() {
#     int n, tables, seats; cin >> n >> tables >> seats;
#     string s; cin >> s;

#     vector<vector<int>> memo(n, vector<int>(tables + 1, NINF));

#     auto dp = [&](auto&& self, int i, int open) -> int {
#         if (i == 0) {
#             char c = s[0];
#             if (open > 1) return NINF;
#             if (open == 1) {
#                 if (c == 'A' || c == 'I') return 1;
#                 return NINF;
#             }
#             return 0;
#         }
#         int& res = memo[i][open];
#         if (res != NINF) return res;

#         char c = s[i];

#         // always an option: kick person i
#         res = self(self, i - 1, open);

#         if (c == 'I') {
#             if (open >= 1) {
#                 int ifOpen = self(self, i - 1, open - 1) + 1;
#                 res = max(res, ifOpen);
#             }
#         } else if (c == 'E') {
#             int prev = self(self, i - 1, open);
#             if (prev < open * seats) {
#                 res = max(res, prev + 1);
#             }
#         } else {
#             if (open >= 1) {
#                 int ifOpen = self(self, i - 1, open - 1) + 1;
#                 res = max(res, ifOpen);
#             }
#             int prev = self(self, i - 1, open);
#             if (prev < open * seats) {
#                 res = max(res, prev + 1);
#             }
#         }
#         return res;
#     };

#     int ans = 0;
#     for (int open = 0; open <= tables; open++) {
#         ans = max(ans, dp(dp, n - 1, open));
#     }
#     cout << ans << '\n';
# }

# int main() {
#     ios::sync_with_stdio(false);
#     cin.tie(nullptr);
#     int t; cin >> t;
#     while (t--) solve();
# }