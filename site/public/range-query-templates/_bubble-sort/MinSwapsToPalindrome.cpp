// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/bubble-sort/MinSwapsToPalindrome.cpp
#include <bits/stdc++.h>
using namespace std;

// Minimum adjacent swaps to turn s into a palindrome, or -1 if no rearrangement of s is one (more than one value with
// an odd count)
// Greedy: the leftmost unplaced element pairs with the last unplaced copy of its value, taking the outermost free pair
// of slots; the lone copy of the odd-count value (if any) goes to the middle. Every element then has a destination, and
// the answer is the number of inversions of the destinations
// Seq: string, vector<int>, vector<long long>, ... (any comparable values); answer can reach ~n^2/2, so long long
// Time: O(n log n), Space: O(n)
template <typename Seq>
long long minAdjacentSwapsToPalindrome(const Seq& s) {
    int n = s.size();

    // indices grouped by value (sorted by (value, index)); grp[i]: where i's value's run starts in order, back[g]: the
    // last unplaced index of the run starting at g
    vector<int> order(n), grp(n), back(n);
    iota(order.begin(), order.end(), 0);
    stable_sort(order.begin(), order.end(), [&](int i, int j) { return s[i] < s[j]; });
    int odd = 0;
    for (int a = 0, b; a < n; a = b) {
        for (b = a; b < n && !(s[order[a]] < s[order[b]]); b++) grp[order[b]] = a;
        odd += (b - a) & 1;
        back[a] = b - 1;
    }
    if (odd > 1) return -1;

    vector<int> dest(n, -1);  // dest[i]: the index s[i] has to end up at
    int left = 0, right = n - 1;
    for (int i = 0; i < n; i++) {
        if (dest[i] != -1) continue;
        int j = order[back[grp[i]]--];  // the last unplaced copy of s[i]
        if (j == i) {  // the lone copy of the odd-count value
            dest[i] = n / 2;
            continue;
        }
        dest[i] = left++, dest[j] = right--;
    }

    // inversions of dest (pairs i < j with dest[i] > dest[j]), with a Fenwick tree over destinations
    vector<int> tree(n + 1, 0);
    long long swaps = 0;
    for (int i = n - 1; i >= 0; i--) {  // right to left: destinations already seen that are smaller than this one
        for (int idx = dest[i]; idx > 0; idx -= idx & -idx) swaps += tree[idx];
        for (int idx = dest[i] + 1; idx <= n; idx += idx & -idx) tree[idx]++;
    }

    return swaps;
}
