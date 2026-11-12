// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/bubble-sort/MinSwapsToPalindrome.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// Minimum adjacent swaps to turn sequence into a palindrome, or -1 if no rearrangement of it is one (more than one
// value with an odd count) sequence: a vector or a string of values that compare with each other: int, long long,
// negatives, chars ok
template <typename Seq>
long long minAdjacentSwapsToPalindrome(const Seq& sequence) {
    int n = sequence.size();

    vector<int> order(n), grp(n), back(n);
    iota(order.begin(), order.end(), 0);
    stable_sort(order.begin(), order.end(), [&](int i, int j) { return sequence[i] < sequence[j]; });
    int odd = 0;
    for (int a = 0, b; a < n; a = b) {
        for (b = a; b < n && !(sequence[order[a]] < sequence[order[b]]); b++) grp[order[b]] = a;
        odd += (b - a) & 1;
        back[a] = b - 1;
    }
    if (odd > 1) return -1;

    vector<int> dest(n, -1);
    int left = 0, right = n - 1;
    for (int i = 0; i < n; i++) {
        if (dest[i] != -1) continue;
        int j = order[back[grp[i]]--];
        if (j == i) {
            dest[i] = n / 2;
            continue;
        }
        dest[i] = left++, dest[j] = right--;
    }

    vector<int> tree(n + 1, 0);
    long long swaps = 0;
    for (int i = n - 1; i >= 0; i--) {
        for (int idx = dest[i]; idx > 0; idx -= idx & -idx) swaps += tree[idx];
        for (int idx = dest[i] + 1; idx <= n; idx += idx & -idx) tree[idx]++;
    }

    return swaps;
}
