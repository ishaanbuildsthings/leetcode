// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/strings/minRotationIndices.cpp
#include <bits/stdc++.h>
using namespace std;

// Every start index whose rotation is the lexicographically smallest one (ascending)
// more than one only when the sequence repeats: those rotations are all equal
// minRotationIndices(string("bcabca")) -> {2, 5}
// minRotationIndices(vector<int>{2, 1, 2, 1}) -> {1, 3}
// O(n) time, O(1) extra space besides the result
template <class T>
vector<int> minRotationIndices(const T& arrOrString) {
    int n = (int)arrOrString.size();
    if (n == 0) return {};
    // Duval: walk the sequence twice around in Lyndon-word blocks; best = start of the smallest rotation found so far
    int i = 0, best = 0, period = n;
    while (i < n) {
        best = i;
        int j = i + 1, k = i;
        while (j < 2 * n) {
            const auto& a = arrOrString[k >= n ? k - n : k];
            const auto& b = arrOrString[j >= n ? j - n : j];
            if (b < a) break;
            k = (a < b) ? i : k + 1;
            j++;
        }
        period = j - k;
        while (i <= k) i += j - k;
    }
    vector<int> res;
    res.reserve(n / period);
    for (int x = best % period; x < n; x += period) res.push_back(x);
    return res;
}
