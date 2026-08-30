// using ll = long long;
const int INF = INT_MAX / 4;
const int MAX_SUM = 5000;
int dp[MAX_SUM + 1];
int ndp[MAX_SUM + 1];
class Solution {
public:
    int minOperations(vector<int>& nums, int sum) {
        int n = nums.size();

        for (int s = 0; s <= sum; s++) {
            dp[s] = INF;
            ndp[s] = INF;
        }


        // 51 -> 25 start doubling 25
        // 25 -> 12 start doubling 12
        // 12 -> 6 no need to double
        // 6 -> 3 no need to double

        // n * sum * 32 * 32
        // 900 * 100 * 5000
        // 5e8

        // vector<int> dp(sum + 1, INF);
        // vector<int> ndp(sum + 1, INF);
        dp[0] = 0;
        for (int i = 0; i < n; i++) {
            int v = nums[i];
            for (int oldSum = 0; oldSum <= sum; oldSum++) {
                ndp[oldSum] = min(ndp[oldSum], dp[oldSum]);
                vector<pair<int,int>> options;
                int doubled = v;
                for (int j = 0; j < 32; j++) {
                    if (doubled + oldSum > sum) {
                        break;
                    }
                    // options.push_back({doubled, j});
                     ndp[oldSum + doubled] = min(ndp[oldSum + doubled], dp[oldSum] + j);
                    doubled *= 2;
                }

                // unordered_set<int> seen;
                int half = v;
                for (int j = 0; j < 32; j++) {
                    if (half == 0) {
                        break;
                    }
                    bool isOdd = half % 2 == 1;
                    half /= 2;
                    if (half + oldSum > sum) continue;
                    // options.push_back({half, j + 1});
                     ndp[oldSum + half] = min(ndp[oldSum + half], dp[oldSum] + j + 1);

                    if (isOdd && half != 0) {
                        int curr = 2 * half;
                        int ops = 1;
                        while (curr + oldSum <= sum) {
                            ndp[oldSum + curr] = min(ndp[oldSum + curr], dp[oldSum] + j + 1 + ops);
                            // options.push_back({curr, j + 1 + ops});
                            // cout << "curr is: " << curr << endl;
                            // seen.insert(curr);
                            ops++;
                            curr *= 2;
                        }
                    }
                }

                // for (auto [diff, ops] : options) {
                //     int nsum = oldSum + diff;
                //     if (nsum > sum) continue;
                //     ndp[nsum] = min(ndp[nsum], dp[oldSum] + ops);
                // }
            
            }
            swap(dp,ndp);
        }
        int answer = dp[sum];
        if (answer == INF) {
            return -1;
        }
        return answer;
    }
};