// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/strings/maxRotation.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// The lexicographically largest rotation, same type as the input (string, vector<int>, vector<long long>, ...)
// works on a string or vector of any element type that has < (char, int, long long, pair, ...)
// maxRotation(string("bcabca")) -> "cabcab"
// maxRotation(vector<int>{3, -1, 2}) -> {3, -1, 2}
// pass a container, not a string literal: maxRotation(string("abc")), not maxRotation("abc")
// O(n) time, O(n) space for the result
template <class T>
T maxRotation(const T& arrOrString) {
    int n = (int)arrOrString.size();
    if (n == 0) return {};
    // Duval: walk the sequence twice around in Lyndon-word blocks; best = start of the largest rotation found so far
    int i = 0, best = 0, period = n;
    while (i < n) {
        best = i;
        int j = i + 1, k = i;
        while (j < 2 * n) {
            const auto& a = arrOrString[k >= n ? k - n : k];
            const auto& b = arrOrString[j >= n ? j - n : j];
            if (a < b) break;
            k = (b < a) ? i : k + 1;
            j++;
        }
        period = j - k;
        while (i <= k) i += j - k;
    }
    int start = best % period;
    T res(arrOrString.begin() + start, arrOrString.end());
    res.insert(res.end(), arrOrString.begin(), arrOrString.begin() + start);
    return res;
}
