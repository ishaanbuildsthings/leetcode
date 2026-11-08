#include <bits/stdc++.h>
using namespace std;

// TEMPLATE BY github.com/ishaanbuildsthings PLEASE DO NOT USE

// Prefix function (pi, KMP): pi[i] = length of the longest proper prefix that is also a suffix ending at i
// works on any comparable container (string, vector<int>, vector<long long>)


// prefixFunction(string("aabaaab")) -> {0, 1, 0, 1, 2, 2, 3}
// prefixFunction(vector<int>{1, 2, 1, 2}) -> {0, 0, 1, 2}
// O(n) time, O(n) space
template <class T>
vector<int> prefixFunction(const T& arrOrString) {
    int n = (int)arrOrString.size();
    vector<int> pi(n, 0);
    for (int i = 1; i < n; i++) {
        int k = pi[i - 1];
        while (k > 0 && arrOrString[i] != arrOrString[k]) k = pi[k - 1];
        if (arrOrString[i] == arrOrString[k]) k++;
        pi[i] = k;
    }
    return pi;
}

// Every start index in text where pattern occurs (overlaps included), ascending. KMP, no concatenation.
// findMatchesKmp(string("ababa"), string("aba")) -> {0, 2}
// findMatchesKmp(vector<int>{1, 2, 1, 2}, vector<int>{1, 2}) -> {0, 2}
// O(n + m) time, O(m) space
template <class T>
vector<int> findMatchesKmp(const T& text, const T& pattern) {
    int m = (int)pattern.size();
    vector<int> res;
    if (m == 0) {
        for (int i = 0; i <= (int)text.size(); i++) res.push_back(i);
        return res;
    }
    vector<int> pi = prefixFunction(pattern);
    int k = 0;
    for (int i = 0; i < (int)text.size(); i++) {
        while (k > 0 && text[i] != pattern[k]) k = pi[k - 1];
        if (text[i] == pattern[k]) k++;
        if (k == m) {
            res.push_back(i - m + 1);
            k = pi[k - 1];
        }
    }
    return res;
}

// Length of the shortest p such that the sequence is a repeat of its first p items (n if it isn't a repeat).
// shortestPeriod(string("abcabcabc")) -> 3
// shortestPeriod(string("abcab")) -> 5
// O(n) time
template <class T>
int shortestPeriod(const T& arrOrString) {
    int n = (int)arrOrString.size();
    if (n == 0) return 0;
    int p = n - prefixFunction(arrOrString).back();
    return n % p == 0 ? p : n;
}
