// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/strings/shortestPeriod.overflow.cpp
#include <bits/stdc++.h>
using namespace std;

// length of the shortest prefix that repeats to form the sequence, where the last copy may be cut off (n if none, 0 if
// empty) i.e. the smallest p with arrOrString[i] == arrOrString[i + p] for every i; p doesn't have to divide n works on
// a string or vector of any element type that has == (char, int, long long, pair, ...)
// shortestPeriod(string("abcabcabc")) -> 3
// shortestPeriod(string("abcab")) -> 3   // "abc" + "ab"
// shortestPeriod(string("abcd")) -> 4
// shortestPeriod(vector<int>{5, -1, 5}) -> 2
// O(n) time and space
template <class T>
int shortestPeriod(const T& arrOrString) {
    int n = (int)arrOrString.size();
    if (n == 0) return 0;
    vector<int> properBorders(n, 0);
    for (int i = 1; i < n; i++) {
        int k = properBorders[i - 1];
        while (k > 0 && arrOrString[i] != arrOrString[k]) k = properBorders[k - 1];
        if (arrOrString[i] == arrOrString[k]) k++;
        properBorders[i] = k;
    }
    return n - properBorders[n - 1];
}
