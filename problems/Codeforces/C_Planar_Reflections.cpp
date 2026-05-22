#include <bits/stdc++.h>
using namespace std;

// I want dp[index][incomingSize][incomingDirection] to be the # of particles produced
const int MAXN = 1000;
const int MAX_PARTICLE = 1000;
const int MOD = 1000000007;
int cache[MAXN+1][MAX_PARTICLE+1][2];
int n, k;

int dp(int currPlane, int partSize, int comingDir) {
  // Base cases
  if (partSize == 0) return 0;
  if (currPlane == n + 1) return 1;
  if (currPlane <= 0) return 1;
  if (partSize == 1) return 1;

  // Caching
  if (cache[currPlane][partSize][comingDir] != -1) {
    return cache[currPlane][partSize][comingDir];
  }

  int ans;

  // if going right
  if (comingDir == 0) {
    int reflect = dp(currPlane - 1, partSize - 1, 1);
    int passThrough = dp(currPlane + 1, partSize, 0);
    ans = (reflect + passThrough) % MOD;
  } else {
    // if going left
    int reflect = dp(currPlane + 1, partSize - 1, 0);
    int passThrough = dp(currPlane - 1, partSize, 1);
    ans = (reflect + passThrough) % MOD;
  }

  cache[currPlane][partSize][comingDir] = ans;
  return ans;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int t;
    cin >> t;

    while (t--) {
      cin >> n >> k;
      memset(cache, -1, sizeof(cache));
      cout << dp(1, k, 0) << '\n';
    }
    return 0;
}