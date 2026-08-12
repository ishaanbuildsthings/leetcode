static const int OUT_OF_RANGE = -2; // no overlap with [ql, qr], keep sweeping
static const int DIED = -1; // in range but couldn't afford even tl, sweep is over
class Solution {
public:
    struct Node { vector<long long> pfMax, pfSum; }; // pfSum is the pf sum OF pf max
    int n;
    vector<Node> tree;
    vector<long long> pf;
    long long querySum(int l, int r) {
        if (r < l) return 0;
        return pf[r] - (l ? pf[l - 1] : 0LL);
    }
    void build(int nodeI, int tl, int tr, vector<int>& nums) {
        if (tl == tr) {
            tree[nodeI].pfMax = {(long long)nums[tl]};
            tree[nodeI].pfSum = {(long long)nums[tl]};
            return;
        }
        int tm = (tl + tr) / 2;
        build(2 * nodeI, tl, tm, nums);
        build(2 * nodeI + 1, tm + 1, tr, nums);
        auto& nm = tree[nodeI].pfMax;
        auto& ns = tree[nodeI].pfSum;
        auto& lMax = tree[2 * nodeI].pfMax;
        auto& lSum = tree[2 * nodeI].pfSum;
        auto& rMax = tree[2 * nodeI + 1].pfMax;
        int lLen = tm - tl + 1, rLen = tr - tm;
        nm.resize(lLen + rLen);
        ns.resize(lLen + rLen);
        memcpy(nm.data(), lMax.data(), lLen * sizeof(long long));
        memcpy(ns.data(), lSum.data(), lLen * sizeof(long long));
        long long run = nm[lLen - 1], acc = ns[lLen - 1];
        const long long* rp = rMax.data();
        for (int i = 0; i < rLen; i++) {
            long long v = rp[i];
            if (v < run) v = run; else run = v;
            acc += v;
            nm[lLen + i] = v;
            ns[lLen + i] = acc;
        }
    }
    struct Res { int foundI; long long spent; long long leftMax; };
    Res walk(int nodeI, int tl, int tr, int ql, int qr, long long budgetLeft, long long leftMax) {
        // not in range, just send up the sentinel
        if (tl > qr || tr < ql) return {OUT_OF_RANGE, 0, leftMax};
        // fully in range
        if (ql <= tl && qr >= tr) {
            auto& nodeMax = tree[nodeI].pfMax;
            auto& nodeSum = tree[nodeI].pfSum;
            // find rightmost index still <= the incoming max
            int l = tl;
            int r = tr;
            int resI = tl - 1;
            while (l <= r) {
                int m = (l + r) / 2;
                if (nodeMax[m - tl] <= leftMax) { resI = m; l = m + 1; }
                else r = m - 1;
            }
            // cost to take the whole node, floored stretch plus the rest
            long long floorWidth = resI - tl + 1;
            long long sumValuesBelowFloor = resI >= tl ? nodeSum[resI - tl] : 0LL;
            // sum to match floor is the floorWidth * leftMax - sumOfRawValuesBelowFloor
            long long costToMatchFloor = floorWidth > 0
                ? floorWidth * leftMax - querySum(tl, resI) : 0LL;
            // sum for the cost above the floor is the sum using pfSum (sum of pf maxes) minus its raw values
            long long costAboveFloor = tr > resI
                ? (nodeSum[tr - tl] - sumValuesBelowFloor) - querySum(resI + 1, tr) : 0LL;
            long long cost = costToMatchFloor + costAboveFloor;
            // If we can sborn everything here, bubble this up
            if (cost <= budgetLeft) return {tr, cost, max(leftMax, nodeMax[tr - tl])};
            if (tl == tr) return {DIED, 0, leftMax};
            // too expensive, the answer is inside, fork below
        }
        int tm = (tl + tr) / 2;
        Res L = walk(2 * nodeI, tl, tm, ql, qr, budgetLeft, leftMax);
        // left had nothing to say, whatever the right returns is the answer
        if (L.foundI == OUT_OF_RANGE) return walk(2 * nodeI + 1, tm + 1, tr, ql, qr, budgetLeft, leftMax);
        // left died or found the answer inside it via a descent, we are done
        if (L.foundI != tm) return L;
        // we instantly absorbed the left, look right
        Res R = walk(2 * nodeI + 1, tm + 1, tr, ql, qr, budgetLeft - L.spent, L.leftMax);
        if (R.foundI < 0) return L;
        return {R.foundI, L.spent + R.spent, R.leftMax};
    }
    long long countNonDecreasingSubarrays(vector<int>& nums, int k) {
        n = nums.size();
        tree.assign(4 * n, Node());
        build(1, 0, n - 1, nums);
        pf.assign(n, 0);
        long long acc = 0;
        for (int i = 0; i < n; i++) { acc += nums[i]; pf[i] = acc; }
        long long res = 0;
        const long long NEG = LLONG_MIN / 4;
        for (int l = 0; l < n; l++) {
            Res r = walk(1, 0, n - 1, l, n - 1, (long long)k, NEG);
            if (r.foundI >= 0) res += r.foundI - l + 1;
        }
        return res;
    }
};