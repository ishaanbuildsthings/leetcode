// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/strings/longestPalAroundEachCenter.cpp
#include <bits/stdc++.h>
using namespace std;

// two vectors of size n, from Manacher:
//   atI[i] = {l, r} of the longest palindrome centered on index i
//   atIPlusOne[i] = {l, r} of the longest palindrome centered between i and i+1, or {i+1, i} if there's none
// works on a string or vector of any element type that has == (char, int, long long, pair, ...)
// auto [atI, atIPlusOne] = longestPalAroundEachCenter(string("abaab"));
//   atI        -> {0, 0}, {0, 2}, {2, 2}, {3, 3}, {4, 4}
//   atIPlusOne -> {1, 0}, {2, 1}, {1, 4}, {4, 3}, {5, 4}
// auto [atI, atIPlusOne] = longestPalAroundEachCenter(vector<int>{-1, 2, -1});
//   atI        -> {0, 0}, {0, 2}, {2, 2}
//   atIPlusOne -> {1, 0}, {2, 1}, {3, 2}
// pass a container, not a string literal: longestPalAroundEachCenter(string("abc")), not
// longestPalAroundEachCenter("abc")
// O(n) time and space
template <class T>
pair<vector<pair<int, int>>, vector<pair<int, int>>> longestPalAroundEachCenter(const T& arrOrString) {
    int n = (int)arrOrString.size();
    // odd[i] = how far the palindrome centered on i reaches, counting i itself (so at least 1)
    vector<int> odd(n, 0);
    for (int i = 0, l = 0, r = -1; i < n; i++) {  // [l, r] = the palindrome reaching furthest right so far
        int k = i > r ? 1 : min(odd[l + r - i], r - i + 1);  // start from the mirrored center's answer
        while (i - k >= 0 && i + k < n && arrOrString[i - k] == arrOrString[i + k]) k++;
        odd[i] = k;
        if (i + k - 1 > r) {
            l = i - k + 1;
            r = i + k - 1;
        }
    }
    // even[i] = how many pairs the palindrome centered between i-1 and i has (0 if none)
    vector<int> even(n, 0);
    for (int i = 0, l = 0, r = -1; i < n; i++) {
        int k = i > r ? 0 : min(even[l + r - i + 1], r - i + 1);
        while (i - k - 1 >= 0 && i + k < n && arrOrString[i - k - 1] == arrOrString[i + k]) k++;
        even[i] = k;
        if (i + k - 1 > r) {
            l = i - k;
            r = i + k - 1;
        }
    }
    vector<pair<int, int>> atI(n), atIPlusOne(n);
    for (int i = 0; i < n; i++) {
        atI[i] = {i - odd[i] + 1, i + odd[i] - 1};
        atIPlusOne[i] = i + 1 < n ? make_pair(i + 1 - even[i + 1], i + even[i + 1]) : make_pair(i + 1, i);
    }
    return {atI, atIPlusOne};
}
