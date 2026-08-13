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
            // If we can absorb everything here, bubble this up
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


// SOLUTION 2, SLIDING WINDOW + cost(l, r) function
// # TEMPLATE BY https://github.com/agrawalishaan
// # You are welcome to use this template. Please keep the link in your contest code to prevent automatic detection of copied content. Templates are allowed. Thanks!

// # Complexities:
// # Build: O(n)
// # Space: O(n)
// # Query/Update: O(log N)

// # baseFn: (val, i) => ...
// # combineFn: (leftVal, rightVal, leftLeftIdx, leftRightIdx, rightLeftIdx, rightRightIdx) => ...
// # tupleNametags: If baseFn returns a tuple, we can supply nametags for each value, like ('min', 'max'), used for debugging
// def baseFn(v, i):
//     return v, i
// def agg(l, r):
//     if l[0] >= r[0]:
//         return l
//     return r
// class SegmentTree:
//     def __init__(self, arr, baseFn, combine, tupleNametags=None):
//         self.n = len(arr)
//         self.arr = arr
//         self.tree = [None] * (4 * self.n)
//         self._combine = combine
//         self._baseFn = baseFn
//         self.tupleNametags = tupleNametags
//         self._build(1, 0, self.n - 1)

//     def _build(self, i, tl, tr):
//         if tl == tr:
//             self.tree[i] = self._baseFn(self.arr[tl], tl)
//             return
//         tm = (tr + tl) // 2
//         self._build(2 * i, tl, tm)
//         self._build(2 * i + 1, tm + 1, tr)
//         self.tree[i] = self._combine(self.tree[2 * i], self.tree[2 * i + 1])

//     def _queryRecurse(self, i, tl, tr, l, r):
//         # print(f"Getting useful intersection from [{tl},{tr}] for query [{l},{r}]")
//         if l <= tl and tr <= r:
//             # print(f'Fully in bounds, returning node value:')
//             # print(f'{self._getPrintFormattedVal(self.tree[i], tl, tr)}\n')
//             return self.tree[i]

//         tm = (tl + tr) // 2
//         # print(f'left child: [{tl},{tm}], right child: [{tm + 1},{tr}]\n')

//         if l > tm:
//             # print(f'Left child [{tl},{tm}] would have no overlap, so only using right\n')
//             return self._queryRecurse(2 * i + 1, tm + 1, tr, l, r)
//         elif r < tm + 1:
//             # print(f'Right child [{tm+1},{tr}] would have no overlap, so only using left\n')
//             return self._queryRecurse(2 * i, tl, tm, l, r)

//         leftResult = self._queryRecurse(2 * i, tl, tm, l, r)
//         rightResult = self._queryRecurse(2 * i + 1, tm + 1, tr, l, r)
//         combinedResult = self._combine(leftResult, rightResult)
//         # print(f"Combining results for parent [{tl},{tr}] for query [{l},{r}]:\n"
//         #       f"  left useful: {self._getPrintFormattedVal(leftResult, max(l, tl), min(tm, r))}\n"
//         #       f"  right useful: {self._getPrintFormattedVal(rightResult, max(l, tm + 1), min(r, tr))}\n"
//         #       f"  -> combined useful: {self._getPrintFormattedVal(combinedResult, max(l, tl), min(r, tr))}\n")
//         return combinedResult

//     def _updateRecurse(self, i, tl, tr, posToBeUpdated):
//         # print(f'descending down to update, pos to be updated: {posToBeUpdated}, current node tl={tl}, tr={tr}')
//         if tl == tr:
//             # print(f'reached leaf node, updating then going back up and combining')
//             self.tree[i] = self._baseFn(self.arr[tl], tl)
//             return
//         tm = (tl + tr) // 2
//         if posToBeUpdated <= tm:
//             self._updateRecurse(2 * i, tl, tm, posToBeUpdated)
//         else:
//             self._updateRecurse(2 * i + 1, tm + 1, tr, posToBeUpdated)
//         self.tree[i] = self._combine(self.tree[2 * i], self.tree[2 * i + 1])

//     def _getPrintFormattedVal(self, val, tl, tr):
//         subarray = self.arr[tl:tr + 1]
//         prefix = f'[{tl},{tr}] subarray: {subarray} '
//         if self.tupleNametags is None:
//             if isinstance(val, tuple):
//                 return prefix + f"({', '.join(str(v) for v in val)})"
//             return prefix + str(val)
//         return f'{prefix}({", ".join(f"{tag}: {v}" for tag, v in zip(self.tupleNametags, val))})'

//     def _line(self):
//         return '________________________________________'

//     ################ PUBLIC METHODS START HERE ################

//     def updateAndMutateArray(self, index, newVal):
//         # print(f'{self._line()} UPDATE CALLED, index={index}, newVal={newVal} {self._line()}')
//         self.arr[index] = newVal
//         self._updateRecurse(1, 0, self.n - 1, index)
//         # print(f'new array: {self.arr}')

//     def query(self, l, r):
//         # print(f'{self._line()} QUERY CALLED, l={l} r={r} {self._line()}')
//         # print(f'array: {self.arr}\n')
//         queryResult = self._queryRecurse(1, 0, self.n - 1, l, r)
//         # print(f'query result: {queryResult}')
//         return queryResult

//     def __str__(self):
//         result = []
//         def _printTree(i, tl, tr, indent):
//             if tl == tr:
//                 result.append(f'{" " * indent}{self._getPrintFormattedVal(self.tree[i], tl, tr)}')
//                 return
//             tm = (tl + tr) // 2
//             result.append(f'{" " * indent}{self._getPrintFormattedVal(self.tree[i], tl, tr)}')
//             _printTree(2 * i, tl, tm, indent + 4)
//             _printTree(2 * i + 1, tm + 1, tr, indent + 4)
//         _printTree(1, 0, self.n - 1, 0)
//         return f'{self._line()} SEGMENT TREE VISUALIZATION {self._line()}\n' + "\n".join(result)


// class Solution:
//     def countNonDecreasingSubarrays(self, nums: List[int], k: int) -> int:
        
//         pf = []
//         curr = 0
//         for v in nums:
//             curr += v
//             pf.append(curr)
        
//         def querySum(l, r):
//             return pf[r] - (pf[l - 1] if l else 0)
        
//         # we will compute suffix values kind of complex
//         # suff[i] means we make i... all mono-increasing, what is the sum of all of these terms?
//         # [5, 3, 9] has 3 suffixes that become mono-increasing:
//         # [      9] -> sum is 9
//         # [   3  9] -> sum is 12
//         # [5  5  9] -> sum is 19

//         # we want a suffix array because we can compute this easily once
//         # if we tried to make a prefix array, we need one for each starting index L
        
//         # nearest index to the right that is strictly greater than arr[i]
//         # n if none, pop while arr[st[-1]] <= arr[i]
//         def leftmostOnRightGtNum(arr):
//             n = len(arr)
//             st = []
//             res = [n] * n
//             for i in range(n - 1, -1, -1):
//                 while st and arr[st[-1]] <= arr[i]:
//                     st.pop()
//                 res[i] = st[-1] if st else n
//                 st.append(i)
//             return res
        
//         stack = leftmostOnRightGtNum(nums)

//         suff = [0] * len(nums)
//         suff[-1] = nums[-1]
//         for i in range(len(nums) - 2, -1, -1):
//             right = stack[i] # we go up to but not including this
//             width = right - i
//             leftSum = width * nums[i]
//             rightSum = suff[right] if right < len(nums) else 0
//             suff[i] = leftSum + rightSum
        
//         st = SegmentTree(nums, baseFn, agg)

//         def cost(l, r):
//             mx, i = st.query(l, r)
//             rightWidth = r - i + 1
//             rightReq = rightWidth * mx
//             payRight = rightReq - querySum(i, r)

//             leftCost = (suff[l] - suff[i]) - querySum(l, i - 1) if i > l else 0

//             return payRight + leftCost

//         l = r = res = 0
//         while l < len(nums):
//             while r < len(nums) and cost(l, r) <= k:
//                 r += 1
//                 res += r - l
//             l += 1

//         return res