// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/strings/prefixFunction.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// pi[i] = length of the longest proper prefix that is also a suffix of arrOrString[0..i]
// prefixFunction(string("aabaaab")) -> {0, 1, 0, 1, 2, 2, 3}
// prefixFunction(vector<int>{1, 2, 1, 2}) -> {0, 0, 1, 2}
// O(n) time and space
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
