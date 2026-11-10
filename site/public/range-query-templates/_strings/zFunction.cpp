// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/strings/zFunction.cpp
#include <bits/stdc++.h>
using namespace std;

// z[i] = longest common prefix of the entire sequence against the suffix starting at i (z[0] = n)
// works on a string or vector of any element type that has == (char, int, long long, pair, ...)
// zFunction(string("aabxaab")) -> {7, 1, 0, 0, 3, 1, 0}
// zFunction(vector<int>{-1, 2, -1, 2, 5}) -> {5, 0, 2, 0, 0}
// O(n) time and space
template <class T>
vector<int> zFunction(const T& arrOrString) {
    int n = (int)arrOrString.size();
    vector<int> z(n, 0);
    if (n == 0) return z;
    z[0] = n;
    int l = 0, r = 0; // [l, r) = the match reaching furthest right so far
    for (int i = 1; i < n; i++) {
        int k = i < r ? min(r - i, z[i - l]) : 0;
        while (i + k < n && arrOrString[k] == arrOrString[i + k]) k++;
        z[i] = k;
        if (i + k > r) {
            l = i;
            r = i + k;
        }
    }
    return z;
}
