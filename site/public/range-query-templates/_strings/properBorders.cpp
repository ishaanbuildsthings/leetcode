// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/strings/properBorders.cpp
#include <bits/stdc++.h>
using namespace std;

// properBorders[i] = length of the longest proper prefix of arrOrString[0..i] that is also a suffix of it (this is KMP)
// works on a string or vector of any element type that has == (char, int, long long, pair, ...)
// properBorders(string("aabaaab")) -> {0, 1, 0, 1, 2, 2, 3}
// properBorders(vector<int>{-1, 2, -1, 2, 5, -1}) -> {0, 0, 1, 2, 0, 1}
// O(n) time and space
template <class T>
vector<int> properBorders(const T& arrOrString) {
    int n = (int)arrOrString.size();
    vector<int> properBorders(n, 0);
    for (int i = 1; i < n; i++) {
        int k = properBorders[i - 1];
        while (k > 0 && arrOrString[i] != arrOrString[k]) k = properBorders[k - 1];
        if (arrOrString[i] == arrOrString[k]) k++;
        properBorders[i] = k;
    }
    return properBorders;
}
