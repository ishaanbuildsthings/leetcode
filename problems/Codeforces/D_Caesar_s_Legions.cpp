#include <bits/stdc++.h>
using namespace std;

// Gaius Julius Caesar, a famous general, loved to line up his soldiers. Overall the army had n1 footmen and n2 horsemen. Caesar thought that an arrangement is not beautiful if somewhere in the line there are strictly more that k1 footmen standing successively one after another, or there are strictly more than k2 horsemen standing successively one after another. Find the number of beautiful arrangements of the soldiers.

// Note that all n1 + n2 warriors should be present at each arrangement. All footmen are considered indistinguishable among themselves. Similarly, all horsemen are considered indistinguishable among themselves.

// Input
// The only line contains four space-separated integers n1, n2, k1, k2 (1 ≤ n1, n2 ≤ 100, 1 ≤ k1, k2 ≤ 10) which represent how many footmen and horsemen there are and the largest acceptable number of footmen and horsemen standing in succession, correspondingly.

// Output
// Print the number of beautiful arrangements of the army modulo 100000000 (108). That is, print the number of such ways to line up the soldiers, that no more than k1 footmen stand successively, and no more than k2 horsemen stand successively.

int n1, n2, k1, k2;
const int MOD = 100000000;

int memo[101][101][2]; // memo[horsesLeft][footmenLeft][horsemanTurn] is the answer

int dp(int hLeft, int fLeft, int hTurn) {
  // cout << "--------\n";
  // cout << "dp called on:\n";
  // cout << hLeft << ' ' << fLeft << ' ' << hTurn << '\n';
  if (hLeft == 0 && fLeft == 0) {
    return 1;
  }
  // bad case
  if (hLeft == 0 and hTurn == 1) {
    return 0;
  }
  if (fLeft == 0 and hTurn == 0) {
    return 0;
  }

  if (memo[hLeft][fLeft][hTurn] != -1) {
    return memo[hLeft][fLeft][hTurn];
  }

  int resHere = 0;
  if (hTurn) {
    for (int placeHere = 1; placeHere <= min(k2, hLeft); placeHere++) {
      int resPlaceHere = dp(hLeft - placeHere, fLeft, 0);
      resHere += resPlaceHere;
      resHere %= MOD;
    }
  }
  if (hTurn == 0) {
    for (int placeHere = 1; placeHere <= min(fLeft, k1); placeHere++) {
      int resPlaceHere = dp(hLeft, fLeft - placeHere, 1);
      resHere += resPlaceHere;
      resHere %= MOD;
    }
  }
  memo[hLeft][fLeft][hTurn] = resHere;
  return memo[hLeft][fLeft][hTurn];
}


int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    cin >> n1 >> n2 >> k1 >> k2;
    memset(memo, -1, sizeof(memo));
    int ans1 = dp(n2, n1, 0);
    int ans2 = dp(n2, n1, 1);
    cout << (ans1 + ans2) % MOD;
}