// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/strings/longestPrefixMatches.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// list of size text.size(): arr[i] = length of match between pattern and text[i...]
// text and pattern can be different containers (e.g. string and vector<char>) of any element type that has ==
// longestPrefixMatches(string("xaabaa"), string("aab")) -> {0, 3, 1, 0, 2, 1}
// longestPrefixMatches(vector<int>{-1, 2, -1, 5}, vector<int>{-1, 2}) -> {2, 0, 1, 0}
// O(n + m) time, O(m) extra space besides the result (n = text size, m = pattern size)
template <class T1, class T2>
vector<int> longestPrefixMatches(const T1& text, const T2& pattern) {
    int n = (int)text.size(), m = (int)pattern.size();
    if (m == 0) return vector<int>(n, 0);
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
    vector<int> arr(n, 0);
    l = 0;
    r = 0;
    for (int i = 0; i < n; i++) {
        int k = i < r ? min(r - i, z[i - l]) : 0;
        while (k < m && i + k < n && pattern[k] == text[i + k]) k++;
        arr[i] = k;
        if (i + k > r) {
            l = i;
            r = i + k;
        }
    }
    return arr;
}
