// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/strings/findMatchesKmp.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// list of indices i where text[i...] matches pattern (an empty pattern matches at every i in 0..text.size())
// findMatchesKmp(string("ababa"), string("aba")) -> {0, 2}
// findMatchesKmp(vector<int>{1, 2, 1, 2}, vector<int>{1, 2}) -> {0, 2}
// O(n + m) time, O(m) extra space besides the result (n = text size, m = pattern size)
template <class T1, class T2>
vector<int> findMatchesKmp(const T1& text, const T2& pattern) {
    int n = (int)text.size(), m = (int)pattern.size();
    if (m == 0) {
        vector<int> all(n + 1);
        iota(all.begin(), all.end(), 0);
        return all;
    }
    vector<int> pi(m, 0);
    for (int i = 1; i < m; i++) {
        int k = pi[i - 1];
        while (k > 0 && pattern[i] != pattern[k]) k = pi[k - 1];
        if (pattern[i] == pattern[k]) k++;
        pi[i] = k;
    }
    vector<int> res;
    int k = 0; // how much of pattern matches the text ending here
    for (int i = 0; i < n; i++) {
        while (k > 0 && text[i] != pattern[k]) k = pi[k - 1];
        if (text[i] == pattern[k]) k++;
        if (k == m) {
            res.push_back(i - m + 1);
            k = pi[k - 1];
        }
    }
    return res;
}
