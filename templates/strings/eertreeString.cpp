#include <bits/stdc++.h>
using namespace std;

// Palindromic tree (eertree) over s. Constructor takes only s.
// Internally each distinct palindromic substring of s is one node, but no method
// below exposes nodes -- everything is stated in terms of indices into s.
// A string of length n has at most n distinct palindromic substrings, so every
// vector returned below has size <= n.
// numUniqueLettersInString below = how many DISTINCT characters actually appear
// in s (derived from s, never assumed to be 26): 2 for a binary string, 4 for DNA.

struct Eertree {
    int n, numUniqueLettersInString;
    string s;
    vector<int> code;
    vector<int> palLen, palLink, depth, firstEnd, diff, sLink, nxt, sufNode, newAt;
    vector<int> occCache, prefCache, revLenCache;

    // O(n * numUniqueLettersInString) time, O(n * numUniqueLettersInString) memory
    Eertree(const string &str) {
        s = str;
        n = (int)s.size();
        vector<int> lookup(256, 0);
        vector<int> seen(256, 0);
        for (char ch : s) seen[(unsigned char)ch] = 1;
        int k = 0;
        for (int ch = 0; ch < 256; ch++)
            if (seen[ch]) lookup[ch] = k++;
        k = numUniqueLettersInString = max(1, k);
        code.resize(n);
        for (int i = 0; i < n; i++) code[i] = lookup[(unsigned char)s[i]];

        palLen = {-1, 0};
        palLink = {0, 0};
        depth = {0, 0};
        firstEnd = {-1, -1};
        diff = {0, 0};
        sLink = {0, 0};
        nxt.assign((size_t)(n + 2) * k, 0);
        sufNode.assign(n, 0);
        newAt.assign(n, 0);

        int last = 1;
        for (int i = 0; i < n; i++) {
            int c = code[i];
            int cur = last;
            while (true) {
                int j = i - palLen[cur] - 1;
                if (j >= 0 && code[j] == c) break;
                cur = palLink[cur];
            }
            if (nxt[(size_t)cur * k + c]) {
                last = nxt[(size_t)cur * k + c];
                sufNode[i] = last;
                continue;
            }
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
                link = nxt[(size_t)t * k + c];
            }
            palLink.push_back(link);
            depth.push_back(depth[link] + 1);
            int d = palLen[v] - palLen[link];
            diff.push_back(d);
            sLink.push_back(d != diff[link] ? link : sLink[link]);
            nxt[(size_t)cur * k + c] = v;
            newAt[i] = 1;
            last = v;
            sufNode[i] = last;
        }
    }

    // O(1) -- the smallest l such that s[l..r] is a palindrome
    int leftmostLForPalEndingAt(int r) {
        return r - palLen[sufNode[r]] + 1;
    }

    // O(n) -- vector of size n, res[r] = leftmostLForPalEndingAt(r)
    vector<int> leftmostLForPalEndingAtEach() {
        vector<int> res(n);
        for (int r = 0; r < n; r++) res[r] = leftmostLForPalEndingAt(r);
        return res;
    }

    // O(n * numUniqueLettersInString) on first call (builds the eertree of
    // reversed s), O(1) after -- the largest r such that s[l..r] is a palindrome
    int rightmostRForPalStartingAt(int l) {
        if (revLenCache.empty()) {
            string rev(s.rbegin(), s.rend());
            Eertree t(rev);
            revLenCache.resize(n);
            for (int i = 0; i < n; i++) revLenCache[i] = t.palLen[t.sufNode[i]];
        }
        return l + revLenCache[n - 1 - l] - 1;
    }

    // O(n * numUniqueLettersInString) on first call, O(n) after
    // vector of size n, res[l] = rightmostRForPalStartingAt(l)
    vector<int> rightmostRForPalStartingAtEach() {
        vector<int> res(n);
        for (int l = 0; l < n; l++) res[l] = rightmostRForPalStartingAt(l);
        return res;
    }

    // O(1) -- how many distinct palindromic substrings s[0..r] has
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

    // O(1) -- how many distinct palindromic substrings s has, at most n
    int numDistinctPals() {
        return (int)palLen.size() - 2;
    }

    // O(1) -- how many palindromic substrings end exactly at r, counting every
    // distinct palindrome that ends there (they are all suffixes of s[0..r])
    int numPalsEndingAt(int r) {
        return depth[sufNode[r]];
    }

    // O(n) -- vector of size n, res[r] = numPalsEndingAt(r)
    vector<int> numPalsEndingAtEach() {
        vector<int> res(n);
        for (int r = 0; r < n; r++) res[r] = depth[sufNode[r]];
        return res;
    }

    // O(n) -- total number of palindromic substrings of s with multiplicity
    // (so "aa" counts 3: two single a's and one "aa"), up to n * (n + 1) / 2
    long long numPalsTotal() {
        occCounts();
        long long tot = 0;
        for (int v = 2; v < (int)occCache.size(); v++) tot += occCache[v];
        return tot;
    }

    // O(n) -- vector of (l, r, count), one entry per DISTINCT palindromic
    // substring of s, so at most n entries. s[l..r] is that palindrome (using its
    // first occurrence) and count is how many times it occurs in s.
    vector<array<int, 3>> distinctPalsWithCounts() {
        occCounts();
        vector<array<int, 3>> res;
        for (int v = 2; v < (int)palLen.size(); v++) {
            int e = firstEnd[v];
            res.push_back({e - palLen[v] + 1, e, occCache[v]});
        }
        return res;
    }

    // O(n log n) -- fewest palindromes s can be cut into
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