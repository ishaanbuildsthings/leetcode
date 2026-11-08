#include <bits/stdc++.h>
using namespace std;

// TEMPLATE BY github.com/ishaanbuildsthings PLEASE DO NOT USE

// Z-function: z[i] = length of the longest common prefix of the whole sequence and the suffix starting at i
// works on any comparable container (string, vector<int>, vector<long long>)


// zFunction(string("aabxaab")) -> {7, 1, 0, 0, 3, 1, 0}   // z[0] is the full length
// zFunction(vector<int>{1, 2, 1, 2}) -> {4, 0, 2, 0}
// O(n) time, O(n) space
template <class T>
vector<int> zFunction(const T& arrOrString) {
    int n = (int)arrOrString.size();
    vector<int> z(n, 0);
    if (n == 0) return z;
    z[0] = n;
    int l = 0, r = 0;
    for (int i = 1; i < n; i++) {
        if (i < r) z[i] = min(r - i, z[i - l]);
        while (i + z[i] < n && arrOrString[z[i]] == arrOrString[i + z[i]]) z[i]++;
        if (i + z[i] > r) {
            l = i;
            r = i + z[i];
        }
    }
    return z;
}

// For every index of text, the length of the longest prefix of pattern that starts there.
// longestPrefixMatches(string("xaabaa"), string("aab")) -> {0, 3, 1, 0, 2, 1}
// O(n + m) time
template <class T>
vector<int> longestPrefixMatches(const T& text, const T& pattern) {
    int m = (int)pattern.size();
    T joined = pattern;
    joined.insert(joined.end(), text.begin(), text.end());
    vector<int> z = zFunction(joined);
    vector<int> res(text.size());
    for (int i = 0; i < (int)text.size(); i++) res[i] = min(z[m + i], m);
    return res;
}

// Every start index in text where pattern occurs (overlaps included), ascending.
// findMatches(string("ababa"), string("aba")) -> {0, 2}
// findMatches(vector<int>{1, 2, 1, 2}, vector<int>{1, 2}) -> {0, 2}
// O(n + m) time
template <class T>
vector<int> findMatches(const T& text, const T& pattern) {
    int m = (int)pattern.size();
    vector<int> res;
    if (m == 0) {
        for (int i = 0; i <= (int)text.size(); i++) res.push_back(i);
        return res;
    }
    T joined = pattern;
    joined.insert(joined.end(), text.begin(), text.end());
    vector<int> z = zFunction(joined);
    for (int i = 0; i < (int)text.size(); i++) {
        if (z[m + i] >= m) res.push_back(i);
    }
    return res;
}
