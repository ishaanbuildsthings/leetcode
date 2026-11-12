// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/strings/findMatches.cpp
#include <bits/stdc++.h>
using namespace std;

// list of indices i where text[i...] matches pattern (an empty pattern matches at every i in 0..text.size()) text and
// pattern can be different containers (e.g. string and vector<char>) of any element type that has ==
// findMatches(string("ababa"), string("aba")) -> {0, 2}
// findMatches(vector<int>{-1, 2, -1, 2, 5}, vector<int>{-1, 2}) -> {0, 2}
// O(n + m) time, O(m) extra space besides the result (n = text size, m = pattern size)
template <class T1, class T2>
vector<int> findMatches(const T1& text, const T2& pattern) {
    int n = (int)text.size(), m = (int)pattern.size();
    if (m == 0) {
        vector<int> all(n + 1);
        iota(all.begin(), all.end(), 0);
        return all;
    }
    // z-function of pattern: z[i] = longest common prefix of pattern against pattern[i...]
    vector<int> z(m, 0);
    z[0] = m;
    int l = 0, r = 0;
    for (int i = 1; i < m; i++) {
        int k = i < r ? min(r - i, z[i - l]) : 0;
        while (i + k < m && pattern[k] == pattern[i + k]) k++;
        z[i] = k;
        if (i + k > r) {
            l = i;
            r = i + k;
        }
    }
    // the same scan over text, compared against pattern: [l, r) = text window matching pattern's start
    vector<int> res;
    l = 0;
    r = 0;
    for (int i = 0; i < n; i++) {
        int k = i < r ? min(r - i, z[i - l]) : 0;
        while (k < m && i + k < n && pattern[k] == text[i + k]) k++;
        if (k == m) res.push_back(i);
        if (i + k > r) {
            l = i;
            r = i + k;
        }
    }
    return res;
}
