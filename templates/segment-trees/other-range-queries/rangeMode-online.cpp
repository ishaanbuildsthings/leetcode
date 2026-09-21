// TEMPLATE BY https://github.com/agrawalishaan

// ========================
// COMPLEXITIES

// O(n root n) build time, O(n) memory

// O(rootN) query(l, r) -> {mode, frequency}

// ========================
/*
How do range mode work in rootN?

First, we split the array into rootN blocks. I want to be able to answer: "what is the mode from bl...br and how many time does it occur)
This is easy, from the starting point of each block sweep to the end of the array, every time we hit the end of the block we know the mode for bl...some other block and we store the answer. We do rootN sweeps each N time.

Now I claim in a rangeMode(l, r) query, the mode is one of:
-the mode JUST inside the full blocks portion
-any one of the partial values

It wouldn't be possible for a value to be the mode if it's not a partial and not the mode of the full region.

We can find the mode of just the inside full blocks portion since we precomputed it.

Now we want to know for each partial, how many times does it occur in the full region? We could do this with NrootN memory by, for each value, computing a prefix sum of size rootN, like for each block. But we can do N memory:

Map all values -> indices, and also an index to its position in that index bucket, so [5, 2, 5] has:

5 : [0, 2]
2 : [1]

But also 0->0, 1->1, 2->1 as the global index -> inside bucket index, mapping.

Now for any partial value we can find exactly where it occurs in its indices list in O(1). We then jump ahead by modeMiddleFrequency spots and check if the ending spot is <= qr or not.
*/

// ========================

#include <bits/stdc++.h>
using namespace std;

template <typename T>
struct RangeMode {
    int n, B, numBlocks;
    vector<T> vals;                 // compressed id -> original value
    vector<int> comp;               // comp[i] = compressed id of arr[i]
    vector<vector<int>> positions;  // positions[valId] = sorted indices holding valId
    vector<int> posIdx;             // posIdx[i] = where i sits inside positions[comp[i]]
    vector<int> blockMode;          // blockMode[startBlock * numBlocks + endBlock] = mode id
    vector<int> blockCnt;           // its frequency

    // O(n root n)
    RangeMode(const vector<T>& arr) {
        n = arr.size();
        B = max(1, (int)sqrt((double)n));
        numBlocks = (n + B - 1) / B;

        // coordinate compress so counting can use a flat array
        vals = arr;
        sort(vals.begin(), vals.end());
        vals.erase(unique(vals.begin(), vals.end()), vals.end());
        comp.resize(n);
        for (int i = 0; i < n; i++) {
            comp[i] = lower_bound(vals.begin(), vals.end(), arr[i]) - vals.begin();
        }

        positions.assign(vals.size(), {});
        posIdx.resize(n);
        for (int i = 0; i < n; i++) {
            posIdx[i] = positions[comp[i]].size();
            positions[comp[i]].push_back(i);
        }

        blockMode.assign((long long)numBlocks * numBlocks, 0);
        blockCnt.assign((long long)numBlocks * numBlocks, 0);
        vector<int> cnt(vals.size(), 0);
        for (int startBlock = 0; startBlock < numBlocks; startBlock++) {
            int best = 0;
            int bestVal = 0;
            int row = startBlock * numBlocks;
            for (int endBlock = startBlock; endBlock < numBlocks; endBlock++) {
                int stop = min(n, (endBlock + 1) * B);
                for (int i = endBlock * B; i < stop; i++) {
                    int valId = comp[i];
                    cnt[valId]++;
                    if (cnt[valId] > best) {
                        best = cnt[valId];
                        bestVal = valId;
                    }
                }
                blockMode[row + endBlock] = bestVal;
                blockCnt[row + endBlock] = best;
            }
            // reset only what we touched
            for (int i = startBlock * B; i < n; i++) {
                cnt[comp[i]] = 0;
            }
        }
    }

    //////////////////// PUBLIC METHODS START HERE ////////////////////

    // O(rootN) -- {mode, frequency} of arr[l...r] inclusive. requires 0 <= l <= r < n
    // ties: returns any one of the tied values
    pair<T, int> query(int l, int r) const {
        int leftBlock = l / B;
        int rightBlock = r / B;
        int best, bestVal, leftEdgeEnd, rightEdgeStart;

        if (rightBlock - leftBlock <= 1) {
            // no whole middle block, every element is a candidate
            best = 0;
            bestVal = comp[l];
            leftEdgeEnd = r;
            rightEdgeStart = r + 1;
        } else {
            int idx = (leftBlock + 1) * numBlocks + (rightBlock - 1);
            best = blockCnt[idx];
            bestVal = blockMode[idx];
            leftEdgeEnd = (leftBlock + 1) * B - 1;
            rightEdgeStart = rightBlock * B;
        }

        // left edge: is the (best + 1)-th copy counting forward from here still <= r?
        for (int i = l; i <= leftEdgeEnd; i++) {
            int valId = comp[i];
            const vector<int>& plist = positions[valId];
            int k = posIdx[i];
            while (k + best < (int)plist.size() && plist[k + best] <= r) {
                best++;
                bestVal = valId;
            }
        }

        // right edge: is the (best + 1)-th copy counting backward from here still >= l?
        for (int i = rightEdgeStart; i <= r; i++) {
            int valId = comp[i];
            const vector<int>& plist = positions[valId];
            int k = posIdx[i];
            while (k - best >= 0 && plist[k - best] >= l) {
                best++;
                bestVal = valId;
            }
        }

        return {vals[bestVal], best};
    }
};