// Time limit: 1.00 s
// Memory limit: 512 MB

// Your company has n coders, and each of them has a skill level between 0 and 100. Your task is to divide the coders into teams that work together.
// Based on your experience, you know that teams work well when the skill levels of the coders are about the same. For this reason, the penalty for creating a team is the skill level difference between the best and the worst coder.
// In how many ways can you divide the coders into teams such that the sum of the penalties is at most x?
// Input
// The first input line has two integers n and x: the number of coders and the maximum allowed penalty sum.
// The next line has n integers t_1,t_2,\dots,t_n: the skill level of each coder.
// Output
// Print one integer: the number of valid divisions modulo 10^9+7.
// Constraints

// 1 \le n \le 100
// 0 \le x \le 5000
// 0 \le t_i \le 100

#include <bits/stdc++.h>
using namespace std;
const int MOD = 1000000000 + 7;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int numCoders, maxPenalty; cin >> numCoders >> maxPenalty;
    vector<int> skills(numCoders);
    for (int i = 0; i < numCoders; i++) cin >> skills[i];
    sort(skills.begin(), skills.end());

    // dp(index, openCoders, currPenalty) and we can choose how many intervals to open in the new case or not
    // stores the # of ways to form a valid division
    // Our inner loop of size 100 amortizes I think
    // 100 * 100 * 5000 = 5e7
    // Want 100 * 500 states

    // dp[openCoders][currPenalty] is the # of ways after processing the first ...i coders and penalty refers to the sum of closed interval penalties + all ongoing open ones
    // for each coder we loop over the old state and over all of the options we can do for this new coder and update a new state

    vector<vector<int>> dp(numCoders + 1, vector<int>(maxPenalty + 1, 0));
    dp[0][0] = 1;
    for (int i = 0; i < skills.size(); i++) {

        vector<vector<int>> ndp(numCoders + 1, vector<int>(maxPenalty + 1, 0));

        int skill = skills[i];
        int diff = i + 1 < numCoders ? skills[i + 1] - skills[i] : 0; // 0 diff won't matter because we only read values with no open coders at the very end
        // loop over old states
        for (int oldOpenCoders = 0; oldOpenCoders <= i; oldOpenCoders++) {
            for (int oldPenalty = 0; oldPenalty <= maxPenalty; oldPenalty++) {
                int oldDpVal = dp[oldOpenCoders][oldPenalty];

                // open and close a group immediately
                int pgained = oldOpenCoders * diff;
                int newp = oldPenalty + pgained;
                if (newp <= maxPenalty) {
                    ndp[oldOpenCoders][newp] += oldDpVal;
                    ndp[oldOpenCoders][newp] %= MOD;
                }
                // open a new one
                int pgained2 = (oldOpenCoders + 1) * diff;
                int newp2 = oldPenalty + pgained2;
                if (newp2 <= maxPenalty) {
                    ndp[oldOpenCoders + 1][newp2] += oldDpVal;
                    ndp[oldOpenCoders + 1][newp2] %= MOD;
                }
                
                // close an existing one
                if (oldOpenCoders) {
                    int pgained3 = (oldOpenCoders - 1) * diff;
                    int newp3 = oldPenalty + pgained3;
                    if (newp3 <= maxPenalty) {
                        ndp[oldOpenCoders - 1][newp3] += (1LL * oldDpVal * oldOpenCoders) % MOD; // pick which one to close
                        ndp[oldOpenCoders - 1][newp3] %= MOD;
                    }
                }
                // add to an existing one but don't close
                int pgained4 = oldOpenCoders * diff;
                int newp4 = oldPenalty + pgained4;
                // Don't need to verify is oldOpenCoders > 0 because otherwise we would just add 0
                if (newp4 <= maxPenalty) {
                    ndp[oldOpenCoders][newp4] += (1LL * oldDpVal * oldOpenCoders) % MOD; // pick which one to close
                    ndp[oldOpenCoders][newp4] %= MOD;
                }
                
            }
        }
        dp = ndp;
    }

    long long out = 0;
    for (int penalty = 0; penalty <= maxPenalty; penalty++) {
        out += dp[0][penalty];
        out %= MOD;
    }
    cout << out;
}