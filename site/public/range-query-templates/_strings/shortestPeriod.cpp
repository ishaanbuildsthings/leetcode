// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/strings/shortestPeriod.cpp
#include <bits/stdc++.h>
using namespace std;

// length of the shortest prefix that repeats a whole number of times to form the sequence (n if none, 0 if empty)
// works on a string or vector of any element type that has == (char, int, long long, pair, ...)
// shortestPeriod(string("abcabcabc")) -> 3
// shortestPeriod(string("abcab")) -> 5
// shortestPeriod(vector<int>{5, -1, 5, -1}) -> 2
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
    int p = n - properBorders[n - 1];
    return n % p == 0 ? p : n;
}
