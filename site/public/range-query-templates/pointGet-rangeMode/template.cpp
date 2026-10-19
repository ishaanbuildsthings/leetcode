// @operations: pointGet rangeMode
// @data-structure-type: sqrt
// @complexities:
//   pointGet: 1
//   rangeMode: sqrt(N)
//   build: N*sqrt(N)
// @memory:
//   layout: none
//   node: blockMode[1*N] blockCnt[1*N]
//   tags: none
//   other: comp[1*N] positions[1*N] posIdx[1*N] vals[1*N]
//   note: blockMode/blockCnt are (N/B)^2 = N tables with B = sqrt(N); vals is the distinct values
// @original-file-url: https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/segment-trees/other-range-queries/rangeMode-online.cpp

// Online range mode in O(sqrt N) per query, O(N sqrt N) build, O(N) memory beyond the block table.
// Split into ~sqrt N blocks and precompute the mode of every run of whole blocks. For a query, the answer is either
// the mode of the whole middle blocks or one of the O(sqrt N) edge elements. For an edge element, positions[val]
// and posIdx let us test in O(1) whether it occurs best + 1 times inside [l, r], so best only ever climbs.
// All indices 0-based, ranges inclusive. Ties return any one of the tied values. T: any type with < and ==.
template <typename T>
struct RangeMode {
    int n, B, numBlocks;
    vector<T> arr, vals;               // vals: sorted distinct values
    vector<int> comp, posIdx;          // comp[i] = compressed a[i]; posIdx[i] = where i sits in positions[comp[i]]
    vector<vector<int>> positions;     // positions[v] = sorted indices holding compressed value v
    vector<int> blockMode, blockCnt;   // [startBlock * numBlocks + endBlock] = mode of those blocks / its frequency

    // O(N sqrt N)
    explicit RangeMode(const vector<T>& a) : n((int)a.size()), arr(a), vals(a), comp(n), posIdx(n) {
        B = max(1, (int)sqrtl(n));
        while ((long long)(B + 1) * (B + 1) <= n) B++;
        while ((long long)B * B > n && B > 1) B--;
        numBlocks = (n + B - 1) / B;
        sort(vals.begin(), vals.end());
        vals.erase(unique(vals.begin(), vals.end()), vals.end());
        positions.assign(vals.size(), {});
        for (int i = 0; i < n; i++) {
            comp[i] = int(lower_bound(vals.begin(), vals.end(), a[i]) - vals.begin());
            posIdx[i] = (int)positions[comp[i]].size();
            positions[comp[i]].push_back(i);
        }
        blockMode.assign((size_t)numBlocks * numBlocks, 0), blockCnt.assign((size_t)numBlocks * numBlocks, 0);
        vector<int> cnt(vals.size());
        for (int sb = 0; sb < numBlocks; sb++) {
            int best = 0, bestVal = 0;
            for (int eb = sb; eb < numBlocks; eb++) {
                for (int i = eb * B; i < min(n, (eb + 1) * B); i++)
                    if (++cnt[comp[i]] > best) best = cnt[comp[i]], bestVal = comp[i];
                blockMode[sb * numBlocks + eb] = bestVal, blockCnt[sb * numBlocks + eb] = best;
            }
            for (int i = sb * B; i < n; i++) cnt[comp[i]] = 0;
        }
    }

    // O(sqrt N) -- (mode of a[l..r], its frequency); requires 0 <= l <= r < n
    pair<T, int> rangeMode(int l, int r) const {
        int lb = l / B, rb = r / B, best, bestVal, leftEdgeEnd, rightEdgeStart;
        if (rb - lb <= 1) {
            best = 0, bestVal = comp[l], leftEdgeEnd = r, rightEdgeStart = r + 1;  // no whole middle block
        } else {
            int idx = (lb + 1) * numBlocks + (rb - 1);
            best = blockCnt[idx], bestVal = blockMode[idx];
            leftEdgeEnd = (lb + 1) * B - 1, rightEdgeStart = rb * B;
        }
        // left edge: is the (best + 1)-th copy counting forward from here still <= r?
        for (int i = l; i <= leftEdgeEnd; i++) {
            const vector<int>& p = positions[comp[i]];
            for (int k = posIdx[i]; k + best < (int)p.size() && p[k + best] <= r;) best++, bestVal = comp[i];
        }
        // right edge: is the (best + 1)-th copy counting backward from here still >= l?
        for (int i = rightEdgeStart; i <= r; i++) {
            const vector<int>& p = positions[comp[i]];
            for (int k = posIdx[i]; k - best >= 0 && p[k - best] >= l;) best++, bestVal = comp[i];
        }
        return {vals[bestVal], best};
    }

    // O(1) -- a[i]
    T pointGet(int i) const { return arr[i]; }
};
