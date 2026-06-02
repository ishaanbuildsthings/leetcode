class Solution {
    public:
        int subtreeInversionSum(vector<vector<int>>& edges, vector<int>& nums, int k) {
            int n = nums.size();
            const long long NEG = -1e18;
    
            vector<vector<int>> g(n);
            for (auto& e : edges) {
                g[e[0]].push_back(e[1]);
                g[e[1]].push_back(e[0]);
            }
    
            vector<vector<int>> children(n);
            auto buildTree = [&](auto&& self, int node, int parent) -> void {
                for (auto adj : g[node]) {
                    if (adj == parent) continue;
                    children[node].push_back(adj);
                    self(self, adj, node);
                }
            };
            buildTree(buildTree, 0, -1);
    
            // dp[node][invertedAbove] = vector of size k+1
            vector<array<vector<long long>, 2>> memo(n);
            vector<array<bool, 2>> done(n, {false, false});
    
            auto dp = [&](auto&& self, int node, int invertedAbove) -> vector<long long>& {
                if (done[node][invertedAbove]) return memo[node][invertedAbove];
                done[node][invertedAbove] = true;
    
                long long val = invertedAbove ? -nums[node] : nums[node];
    
                if (children[node].empty()) {
                    vector<long long> ans(k + 1);
                    if (val < 0) {
                        ans[0] = llabs(val);
                        for (int dist = 1; dist <= k; dist++) ans[dist] = val;
                    } else {
                        for (int dist = 0; dist <= k; dist++) ans[dist] = val;
                    }
                    memo[node][invertedAbove] = move(ans);
                    return memo[node][invertedAbove];
                }
    
                // if we do not invert this node
                vector<long long> before(k + 1, val);
                vector<long long> after(k + 1, NEG);
    
                for (auto child : children[node]) {
                    for (int i = 0; i <= k; i++) after[i] = NEG;
                    auto& childVec = self(self, child, invertedAbove);
                    for (int childSz = 0; childSz < k; childSz++) {
                        if (childVec[childSz] == NEG) continue;
                        int trueChild = childSz + 1;
                        for (int beforeSz = 0; beforeSz <= k; beforeSz++) {
                            int nsize = min(trueChild, beforeSz);
                            if (trueChild + beforeSz < k) continue;
                            if (before[beforeSz] == NEG) continue;
                            after[nsize] = max(after[nsize], before[beforeSz] + childVec[childSz]);
                        }
                    }
                    swap(before, after);
                }
    
                // if we do invert this node
                long long withInvert = -val;
                for (auto child : children[node]) {
                    auto& childVec = self(self, child, !invertedAbove);
                    withInvert += childVec[k - 1];
                }
    
                before[0] = max(before[0], withInvert);
    
                memo[node][invertedAbove] = move(before);
                return memo[node][invertedAbove];
            };
    
            auto& rt = dp(dp, 0, false);
            long long res = NEG;
            for (int i = 0; i <= k; i++) res = max(res, rt[i]);
            return (int)res;
        }
    };