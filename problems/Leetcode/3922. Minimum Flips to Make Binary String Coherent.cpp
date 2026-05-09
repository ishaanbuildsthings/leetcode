using ll = long long;
class Solution {
public:
    int minFlips(string s) {
        vector<int> one = {0, 1, 1};
        vector<int> two = {1, 1, 0};
        int n = s.size();

        vector<vector<vector<ll>>> cache(n, vector<vector<ll>>(3, vector<ll>(3, -1)));

        auto dp = [&](auto&& self, int i, int j, int idx) -> long long {
            if (i == 3 || j == 3) return 10000000000;
            if (idx == n) {
                return 0;
            } 
            auto& cval = cache[idx][i][j];
            if (cval != -1) return cval;
            long long res = 10000000000;
            int v = s[idx] - '0';
            // if we place the same
            bool iGoesUp = one[i] == v;
            bool jGoesUp = two[j] == v;
            ll staySame = self(self, iGoesUp ? i + 1 : i, jGoesUp ? j + 1 : j, idx + 1);

            // if we change
            iGoesUp = one[i] != v;
            jGoesUp = two[j] != v;
            ll change = 1 + self(self, iGoesUp ? i + 1 : i, jGoesUp ? j + 1 : j, idx + 1);

            cval = min(staySame, change);
            return cval;

        };

        return dp(dp, 0, 0, 0);
    }
};