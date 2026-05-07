// width, height = map(int, input().split())
 
// INF = 10**5
 
// dp = [[INF] * (height+1) for _ in range(width + 1)] # dp[width][height] is the answer
 
// for sideLength in range(1, min(width, height) + 1):
//   dp[sideLength][sideLength] = 0
 
// for w in range(1, width + 1):
//     for h in range(1, height + 1):
//         resHere = dp[w][h]
//         for allLeftSize in range(1, w):
//             rightWidth = w - allLeftSize
//             ifCut = 1 + dp[allLeftSize][h] + dp[rightWidth][h]
//             resHere = min(resHere, ifCut)
//         for allUpSize in range(1, h):
//             downWidth = h - allUpSize
//             ifCut = 1 + dp[w][allUpSize] + dp[w][downWidth]
//             resHere = min(resHere, ifCut)
//         dp[w][h] = resHere
 
// print(dp[width][height])
 
#include <iostream>
#include <vector>
using namespace std;
 
int main() {
    int width, height;
    cin >> width >> height;
 
    const int INF = 1e5;
 
    vector<vector<int>> dp(width + 1, vector<int>(height + 1, INF));
 
    for (int sideLength = 1; sideLength <= min(width, height); sideLength++) {
        dp[sideLength][sideLength] = 0;
    }
 
    for (int w = 1; w <= width; w++) {
        for (int h = 1; h <= height; h++) {
            int resHere = dp[w][h];
            for (int allLeftSize = 1; allLeftSize < w; allLeftSize++) {
                int rightWidth = w - allLeftSize;
                int ifCut = 1 + dp[allLeftSize][h] + dp[rightWidth][h];
                resHere = min(resHere, ifCut);
            }
            for (int allUpSize = 1; allUpSize < h; allUpSize++) {
                int downWidth = h - allUpSize;
                int ifCut = 1 + dp[w][allUpSize] + dp[w][downWidth];
                resHere = min(resHere, ifCut);
            }
            dp[w][h] = resHere;
        }
    }
 
    cout << dp[width][height] << endl;
    return 0;
}