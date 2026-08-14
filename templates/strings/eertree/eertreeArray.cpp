#include <bits/stdc++.h>
using namespace std;

// Palindromic tree (eertree) over an array a of any comparable type T
// (int, long long, negatives, double, string, pair -- values are compared only
// for equality, never used as indices, so anything with operator< works).
// Internally each distinct palindromic subarray of a is one node, but no method
// below exposes nodes -- everything is stated in terms of indices into a.
// An array of length n has at most n distinct palindromic subarrays, so every
// vector returned below has size <= n.
// numUniqueValsInArray below = how many DISTINCT values actually appear in a
// (derived from a): 2 for a binary array, 4 for DNA, up to n in general.

template <class T>
struct Eertree {
    int n, numUniqueValsInArray;
    vector<T> a;
    vector<int> code;
    vector<int> palLen, palLink, depth, firstEnd, diff, sLink, sufNode, newAt;
    vector<int> occCache, prefCache, revLenCache;

    // O(n log numUniqueValsInArray) time, O(n) memory
    // (the transition table is dense when small enough to afford, else hashed,
    // and is discarded when the build ends -- it is not kept on the object)
    Eertree(const vector<T> &arr) {
        a = arr;
        n = (int)a.size();
        vector<T> vals = a;
        sort(vals.begin(), vals.end());
        vals.erase(unique(vals.begin(), vals.end()), vals.end());
        int k = numUniqueValsInArray = max<int>(1, (int)vals.size());
        code.resize(n);
        for (int i = 0; i < n; i++)
            code[i] = (int)(lower_bound(vals.begin(), vals.end(), a[i]) - vals.begin());

        palLen = {-1, 0};
        palLink = {0, 0};
        depth = {0, 0};
        firstEnd = {-1, -1};
        diff = {0, 0};
        sLink = {0, 0};
        sufNode.assign(n, 0);
        newAt.assign(n, 0);

        bool dense = (long long)(n + 2) * k <= 8000000LL;
        vector<int> tableDense;
        unordered_map<long long, int> tableSparse;
        if (dense) tableDense.assign((size_t)(n + 2) * k, 0);
        else tableSparse.reserve(2 * n + 4);

        auto getT = [&](int v, int c) -> int {
            long long idx = (long long)v * k + c;
            if (dense) return tableDense[idx];
            auto it = tableSparse.find(idx);
            return it == tableSparse.end() ? 0 : it->second;
        };
        auto setT = [&](int v, int c, int u) {
            long long idx = (long long)v * k + c;
            if (dense) tableDense[idx] = u;
            else tableSparse[idx] = u;
        };

        int last = 1;
        for (int i = 0; i < n; i++) {
            int c = code[i];
            int cur = last;
            while (true) {
                int j = i - palLen[cur] - 1;
                if (j >= 0 && code[j] == c) break;
                cur = palLink[cur];
            }
            int ex = getT(cur, c);
            if (ex) { last = ex; sufNode[i] = last; continue; }
            int v = (int)palLen.size();
            palLen.push_back(palLen[cur] + 2);
            firstEnd.push_back(i);
            int link;
            if (palLen[v] == 1) link = 1;
            else {
                int t = palLink[cur];
                while (true) {
                    int j = i - palLen[t] - 1;
                    if (j >= 0 && code[j] == c) break;
                    t = palLink[t];
                }
                link = getT(t, c);
            }
            palLink.push_back(link);
            depth.push_back(depth[link] + 1);
            int d = palLen[v] - palLen[link];
            diff.push_back(d);
            sLink.push_back(d != diff[link] ? link : sLink[link]);
            setT(cur, c, v);
            newAt[i] = 1;
            last = v;
            sufNode[i] = last;
        }
    }

    // O(1) -- the smallest l such that a[l..r] is a palindrome
    int leftmostLForPalEndingAt(int r) {
        return r - palLen[sufNode[r]] + 1;
    }

    // O(n) -- vector of size n, res[r] = leftmostLForPalEndingAt(r)
    vector<int> leftmostLForPalEndingAtEach() {
        vector<int> res(n);
        for (int r = 0; r < n; r++) res[r] = leftmostLForPalEndingAt(r);
        return res;
    }

    // O(n log numUniqueValsInArray) on first call (builds the eertree of reversed
    // a), O(1) after -- the largest r such that a[l..r] is a palindrome
    int rightmostRForPalStartingAt(int l) {
        if (revLenCache.empty()) {
            vector<T> rev(a.rbegin(), a.rend());
            Eertree<T> t(rev);
            revLenCache.resize(n);
            for (int i = 0; i < n; i++) revLenCache[i] = t.palLen[t.sufNode[i]];
        }
        return l + revLenCache[n - 1 - l] - 1;
    }

    // O(n log numUniqueValsInArray) on first call, O(n) after
    // vector of size n, res[l] = rightmostRForPalStartingAt(l)
    vector<int> rightmostRForPalStartingAtEach() {
        vector<int> res(n);
        for (int l = 0; l < n; l++) res[l] = rightmostRForPalStartingAt(l);
        return res;
    }

    // O(1) -- how many distinct palindromic subarrays a[0..r] has
    int numDistinctPalsInPrefix(int r) {
        if (prefCache.empty()) {
            prefCache.resize(n);
            int run = 0;
            for (int i = 0; i < n; i++) { run += newAt[i]; prefCache[i] = run; }
        }
        return prefCache[r];
    }

    // O(n) -- vector of size n, res[r] = numDistinctPalsInPrefix(r)
    vector<int> numDistinctPalsInPrefixEach() {
        numDistinctPalsInPrefix(0);
        return prefCache;
    }

    // O(1) -- how many distinct palindromic subarrays a has, at most n
    int numDistinctPals() {
        return (int)palLen.size() - 2;
    }

    // O(1) -- how many palindromic subarrays end exactly at r, counting every
    // distinct palindrome that ends there (they are all suffixes of a[0..r])
    int numPalsEndingAt(int r) {
        return depth[sufNode[r]];
    }

    // O(n) -- vector of size n, res[r] = numPalsEndingAt(r)
    vector<int> numPalsEndingAtEach() {
        vector<int> res(n);
        for (int r = 0; r < n; r++) res[r] = depth[sufNode[r]];
        return res;
    }

    // O(n) -- total number of palindromic subarrays of a with multiplicity
    // (so [5, 5] counts 3: two single 5's and one [5, 5]), up to n * (n + 1) / 2
    long long numPalsTotal() {
        occCounts();
        long long tot = 0;
        for (int v = 2; v < (int)occCache.size(); v++) tot += occCache[v];
        return tot;
    }

    // O(n) -- vector of (l, r, count), one entry per DISTINCT palindromic
    // subarray of a, so at most n entries. a[l..r] is that palindrome (using its
    // first occurrence) and count is how many times it occurs in a.
    vector<array<int, 3>> distinctPalsWithCounts() {
        occCounts();
        vector<array<int, 3>> res;
        for (int v = 2; v < (int)palLen.size(); v++) {
            int e = firstEnd[v];
            res.push_back({e - palLen[v] + 1, e, occCache[v]});
        }
        return res;
    }

    // O(n log n) -- fewest palindromes a can be cut into
    int minPalPartition() {
        const int INF = INT_MAX / 2;
        vector<int> dp(n + 1, INF), seriesAns(palLen.size(), 0);
        dp[0] = 0;
        for (int i = 1; i <= n; i++) {
            for (int v = sufNode[i - 1]; palLen[v] > 0; v = sLink[v]) {
                seriesAns[v] = dp[i - palLen[sLink[v]] - diff[v]];
                if (diff[v] == diff[palLink[v]])
                    seriesAns[v] = min(seriesAns[v], seriesAns[palLink[v]]);
                dp[i] = min(dp[i], seriesAns[v] + 1);
            }
        }
        return dp[n];
    }

    vector<int> &occCounts() {
        if (occCache.empty()) {
            occCache.assign(palLen.size(), 0);
            for (int v : sufNode) occCache[v]++;
            for (int v = (int)palLen.size() - 1; v >= 2; v--)
                occCache[palLink[v]] += occCache[v];
            occCache[0] = occCache[1] = 0;
        }
        return occCache;
    }
};