# #include <bits/stdc++.h>
# using namespace std;
# using ll = long long;

# const ll INF = LLONG_MAX / 4;

# void solve() {
#     // cerr << "===============" << endl;
#     int n; cin >> n;
#     vector<int> A(n); for (int i = 0; i < n; i++) cin >> A[i];

#     vector<pair<ll,ll>> cache(n, {INF,INF}); // holds (largestPf, smallestPf)
#     vector<int> choiceMax(n, -100);
#     vector<int> choiceMin(n, -100);
#     // returns max sum
#     auto dp = [&](auto&& self, int i) -> pair<ll,ll> {
#         if (i == -1) return {0,0};

#         if (cache[i].first != INF) return cache[i];

#         int val = A[i];
#         // if this is negative, we have no option

#         if (val < 0) {
#             pair<ll,ll> prev = self(self, i - 1);
#             ll nmax = prev.first + val;
#             ll nmin = prev.second + val;
#             cache[i] = {nmax, nmin};
#             choiceMax[i] = 0;
#             choiceMin[i] = 0;
#             return cache[i];
#         }

#         pair<ll,ll> prev = self(self, i - 1);
#         ll nmaxNoFlip = prev.first + val;
#         ll nmaxWithFlip = (-1LL * prev.second) - val;
#         if (nmaxNoFlip >= nmaxWithFlip) {
#             choiceMax[i] = 0;
#         } else {
#             choiceMax[i] = 1;
#         }
#         ll nmax = max(nmaxNoFlip, nmaxWithFlip);

#         ll nminNoFlip = prev.second + val;
#         ll nminWithFlip = (-1LL * prev.first) - val;
#         if (nminNoFlip <= nminWithFlip) {
#             choiceMin[i] = 0;
#         } else {
#             choiceMin[i] = 1;
#         }
#         ll nmin = min(nminNoFlip, nminWithFlip);

#         cache[i] = {nmax, nmin};
#         return cache[i];
#     };

#     dp(dp, n - 1);
#     cout << "=========" << endl;
#     for (int i = 0; i < n; i++) {
#         cout << "i=" << i << endl;
#         cout << dp(dp, i).first << " " << dp(dp, i).second << endl;
#     }
    
#     // cout << "max sum: " << maxSum << '\n';

#     // cerr << "max sum: " << dp(dp,n-1).first << endl;

#     int goingForMax = 1; // we are currently going for the max
#     int currI = n - 1;
#     vector<int> flippedPos;
#     while (currI >= 0) {
#         if (goingForMax) {
#             int choice = choiceMax[currI];
#             if (choice) {
#                 flippedPos.push_back(currI);
#                 goingForMax ^= 1;
#             }
#         } else {
#             int choice = choiceMin[currI];
#             if (choice) {
#                 flippedPos.push_back(currI);
#                 goingForMax ^= 1; 
#             }
#         }
#         currI--;
#     }
#     cout << flippedPos.size() << endl;
#     for (auto x : flippedPos) cout << x + 1 << " ";
#     cout << endl;

#     // int currI = n - 1;
#     // int currFlip = 0;
#     // vector<int> flippedPos;
#     // while (currI >= 0) {
#     //     cerr << "currI: " << currI << endl;
#     //     cerr << "curr flip: " << currFlip << endl;
#     //     int didFlip = flipChoice[currI][currFlip];
#     //     if (didFlip) {
#     //         flippedPos.push_back(currI);
#     //     }
#     //     int flip = currFlip ^ didFlip;
#     //     int ncurrI = currI - 1;
#     //     currI = ncurrI;
#     //     currFlip = flip;
#     // }
#     // cout << flippedPos.size() << "\n";
#     // for (auto x : flippedPos) cout << x + 1 << " ";

#     // cout << endl;
# }

# int main() {
#     ios::sync_with_stdio(false);
#     cin.tie(nullptr);
#     int t; cin >> t;
#     while (t--) {
#         solve();
#     }
# }
































# // #include <bits/stdc++.h>
# // using namespace std;
# // using ll = long long;

# // const ll INF = LLONG_MAX / 4;

# // void solve() {
# //     cerr << "===============" << endl;
# //     int n; cin >> n;
# //     vector<int> A(n); for (int i = 0; i < n; i++) cin >> A[i];

# //     vector<vector<ll>> cache(n, vector<ll>(2, INF));
# //     vector<vector<int>> flipChoice(n, vector<int>(2, -100));

# //     // returns min sum
# //     auto dp = [&](auto&& self, int i, int flipped) -> ll {
# //         if (i == -1) return 0;

# //         if (cache[i][flipped] != INF) return cache[i][flipped];

# //         int val = flipped ? (-1 * A[i]) : A[i];
# //         // if this is negative, we have no option

# //         if (val < 0) {
# //             ll ans = val + self(self, i - 1, flipped);
# //             flipChoice[i][flipped] = 0;
# //             cache[i][flipped] = ans;
# //             return ans;
# //         }

# //         ll ifSkip = val + self(self, i - 1, flipped);
# //         ll ifFlip = (-1LL * val) + self(self, i - 1, flipped ^ 1);
# //         if (ifSkip >= ifFlip) {
# //             flipChoice[i][flipped] = 0;
# //         } else {
# //             flipChoice[i][flipped] = 1;
# //         }
# //         ll ans = max(ifSkip, ifFlip);
# //         cache[i][flipped] = ans;
# //         return ans;
# //     };

# //     ll maxSum = dp(dp, n - 1, 0);

# //     // cout << "max sum: " << maxSum << '\n';

# //     cerr << "max sum: " << maxSum << endl;

# //     int currI = n - 1;
# //     int currFlip = 0;
# //     vector<int> flippedPos;
# //     while (currI >= 0) {
# //         cerr << "currI: " << currI << endl;
# //         cerr << "curr flip: " << currFlip << endl;
# //         int didFlip = flipChoice[currI][currFlip];
# //         if (didFlip) {
# //             flippedPos.push_back(currI);
# //         }
# //         int flip = currFlip ^ didFlip;
# //         int ncurrI = currI - 1;
# //         currI = ncurrI;
# //         currFlip = flip;
# //     }
# //     cout << flippedPos.size() << "\n";
# //     for (auto x : flippedPos) cout << x + 1 << " ";

# //     cout << endl;
# // }

# // int main() {
# //     ios::sync_with_stdio(false);
# //     cin.tie(nullptr);
# //     int t; cin >> t;
# //     while (t--) {
# //         solve();
# //     }
# // }