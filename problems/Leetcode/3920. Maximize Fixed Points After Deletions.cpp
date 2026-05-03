struct BIT2DMax {
    int n, m;
    vector<vector<int>> rowY;
    vector<vector<int>> bit;

    BIT2DMax(int n_, int m_) : n(n_), m(m_), rowY(n_ + 1), bit(n_ + 1) {}

    void touch(int x, int y) {
        for (int i = x; i <= n; i += i & -i)
            rowY[i].push_back(y);
    }

    void prepare() {
        for (int i = 1; i <= n; i++) {
            sort(rowY[i].begin(), rowY[i].end());
            rowY[i].erase(unique(rowY[i].begin(), rowY[i].end()), rowY[i].end());
            bit[i].assign(rowY[i].size() + 1, 0);
        }
    }

    void update(int x, int y, int val) {
        for (int i = x; i <= n; i += i & -i) {
            auto& row = rowY[i];
            int pos = (int)(lower_bound(row.begin(), row.end(), y) - row.begin()) + 1;
            int sz = (int)row.size();
            auto& b = bit[i];
            for (int j = pos; j <= sz; j += j & -j)
                if (b[j] < val) b[j] = val;
        }
    }

    int query(int x, int y) const {
        int res = 0;
        for (int i = x; i > 0; i -= i & -i) {
            auto& row = rowY[i];
            int pos = (int)(upper_bound(row.begin(), row.end(), y) - row.begin());
            auto& b = bit[i];
            for (int j = pos; j > 0; j -= j & -j)
                if (b[j] > res) res = b[j];
        }
        return res;
    }
};

class Solution {
public:
    int maxFixedPoints(vector<int>& nums) {
        int n = nums.size();
        int M = *max_element(nums.begin(), nums.end());
        if (M == 0) return n == 0 ? 0 : 1;

        BIT2DMax bit(M + 1, n);

        for (int i = 0; i < n; i++) {
            int v = nums[i], tf = i - v;
            if (tf < 0) continue;
            bit.touch(v + 1, tf + 1);
        }
        bit.prepare();

        int ans = 0;
        for (int i = 0; i < n; i++) {
            int v = nums[i], tf = i - v;
            if (tf < 0) continue;
            int prevMax = bit.query(v, tf + 1);
            int newVal = prevMax + 1;
            ans = max(ans, newVal);
            bit.update(v + 1, tf + 1, newVal);
        }
        return ans;
    }
};