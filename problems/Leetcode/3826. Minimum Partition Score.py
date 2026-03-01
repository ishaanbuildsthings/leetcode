# # Solution 1, dnc dp O(n log n * k)
# class Solution:
#     def minPartitionScore(self, nums: List[int], k: int) -> int:
#         n = len(nums)

#         dp =  [[inf] * (n + 1) for _ in range(k + 1)] # dp[partitions][i] is the min cost to split the array into that many PARTITIONS (not cuts) for 0...i

#         currSum = 0
#         for i in range(n):
#             currSum += nums[i]
#             dp[1][i] = currSum * (currSum + 1) // 2
#             # we are setting up 0...i into a single partition
                
#         # leaving dp[0 paritions][...] unused as we start loop on partitions = 2

#         pf = []
#         curr = 0
#         for v in nums:
#             curr += v
#             pf.append(curr)

#         def cost(l, r):
#             tot = (pf[r] - (pf[l - 1] if l else 0))
#             return tot * (tot + 1) // 2


#         for partitions in range(2, k + 1):

#             # we need to fill out the dp for all indices fillL...fillR
#             # and the optimal j < i for the previous partition, we have some boundary on that range
#             # j...i is the partition we will form
#             def solve(fillL, fillR, leftJ, rightJ):
#                 if fillL > fillR:
#                     return
                
#                 mid = (fillR + fillL) // 2 # solving for this index, so 0...mid

#                 bestCost = inf
#                 bestJ = None

#                 # find some j < i that works by checking all
#                 for j in range(leftJ, min(rightJ + 1, mid + 1)):
#                     costHere = dp[partitions - 1][j] + cost(j + 1, mid)
#                     if costHere < bestCost:
#                         bestCost = costHere
#                         bestJ = j
                
#                 dp[partitions][mid] = bestCost

#                 solve(fillL, mid - 1, leftJ, bestJ)
#                 solve(mid + 1, fillR, bestJ, rightJ)
            
#             solve(0, len(nums) - 1, 0, len(nums) - 1)
        
#         return dp[k][len(nums) - 1]


                




# solution 2, n*k log(max) alien trick, 
class Solution:
    def minPartitionScore(self, nums: List[int], k: int) -> int:
        n = len(nums)

        pf = []
        curr = 0
        for v in nums:
            curr += v
            pf.append(curr)
        
        def squery(l, r):
            return pf[r] - (pf[l - 1] if l else 0)
        
        def cost(l, r):
            tot = squery(l, r)
            return tot * (tot + 1) // 2

        def withPenalty(y):

            # TLE top down dp lol
            # # gives us the minimum score and the # of partitions naturally made
            # cache = [None] * n
            # def dp(i):
            #     if i == n:
            #         return 0, 0
            #     if cache[i] is not None:
            #         return cache[i]
            #     minScore = inf
            #     tot = 0
            #     minScoreParts = None
            #     for j in range(i, n):
            #         tot += nums[j]
            #         nxtMin, nxtParts = dp(j + 1)
            #         ifEndHere = y + (tot * (tot+1)//2) + nxtMin
            #         if ifEndHere < minScore:
            #             minScore = ifEndHere
            #             minScoreParts = nxtParts + 1
            #     cache[i] = minScore, minScoreParts
            #     return cache[i]

            # bestScore, bestParts = dp(0)
            # return bestScore, bestParts     

            # guh also TLEs bottom up
            dp = [inf] * n # best cost to partition 0...i
            cnt = [None] * n # optimal count of partitions for that
            cnt[0] = 1
            dp[0] = y + (nums[0] * (nums[0] + 1) // 2)
            for i in range(1, n):
                bestCost = inf # for ...i
                bestCount = None
                for j in range(i + 1):
                    costHere = cost(j, i)
                    prevCost = dp[j - 1] if j else 0
                    totCost = costHere + prevCost + y
                    if totCost < bestCost:
                        bestCost = totCost
                        bestCount = (cnt[j - 1] if j else 0) + 1
                dp[i] = bestCost
                cnt[j] = bestCount
            
            return dp[-1], cnt[-1]
            

        l = 0
        r = sum(nums) * (sum(nums) + 1) // 2 # max penalty is the most expensive partition
        res = None
        while l <= r:
            y = (r + l) // 2 # lambda we will try
            bestScore, bestParts = withPenalty(y)
            # didnt get enough divisions, y too high
            if bestParts <= k:
                r = y - 1
                res = bestScore - (y * k)
            else:
                l = y + 1
    
        return res
        



# alien trick in C++ which barely passed

class Solution {
public:
    long long minPartitionScore(vector<int>& nums, int k) {
        int n = nums.size();
        using ll = long long;

        vector<ll> pf(n);
        ll curr = 0;
        for (int i = 0; i < n; i++) {
            curr += nums[i];
            pf[i] = curr;
        }

        auto squery = [&](int l, int r) -> ll {
            return pf[r] - (l > 0 ? pf[l - 1] : 0);
        };

        vector<vector<ll>> costTable(n, vector<ll>(n));
        for (int i = 0; i < n; i++) {
            for (int j = i; j < n; j++) {
                ll tot = pf[j] - (i > 0 ? pf[i - 1] : 0);
                costTable[i][j] = tot * (tot + 1) / 2;
            }
        }

        vector<ll> dp(n);
        vector<int> cnt(n);

        auto withPenalty = [&](ll y) -> pair<ll, int> {


            dp[0] = y + ((ll)nums[0] * (nums[0] + 1) / 2);
            cnt[0] = 1;

            for (int i = 1; i < n; i++) {
                ll bestCost = LLONG_MAX;
                int bestCount = -1;
                for (int j = 0; j <= i; j++) {
                    ll costHere = costTable[j][i];
                    ll prevCost = (j > 0) ? dp[j - 1] : 0;
                    ll totCost = costHere + prevCost + y;
                    if (totCost < bestCost) {
                        bestCost = totCost;
                        bestCount = (j > 0 ? cnt[j - 1] : 0) + 1;
                    }
                }
                dp[i] = bestCost;
                cnt[i] = bestCount;
            }

            return {dp[n - 1], cnt[n - 1]};
        };

        ll l = 0;
        ll r = costTable[0][n - 1];
        ll res = -1;
        while (l <= r) {
            ll y = l + (r - l) / 2;
            auto [bestScore, bestParts] = withPenalty(y);
            if (bestParts <= k) {
                r = y - 1;
                res = bestScore - y * k;
            } else {
                l = y + 1;
            }
        }

        return res;
    }
};