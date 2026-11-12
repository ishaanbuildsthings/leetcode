// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/bubble-sort/MinSwapsToTarget.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// Minimum adjacent swaps to turn sequence into target, or -1 if target isn't a rearrangement of sequence sequence,
// target: vectors or strings of values that compare with each other: int, long long, negatives, chars ok
template <typename Seq>
long long minAdjacentSwapsToTarget(const Seq& sequence, const Seq& target) {
    int n = sequence.size();
    if ((int)target.size() != n) return -1;

    vector<int> fromOrder(n), toOrder(n);
    iota(fromOrder.begin(), fromOrder.end(), 0);
    iota(toOrder.begin(), toOrder.end(), 0);
    stable_sort(fromOrder.begin(), fromOrder.end(), [&](int i, int j) { return sequence[i] < sequence[j]; });
    stable_sort(toOrder.begin(), toOrder.end(), [&](int i, int j) { return target[i] < target[j]; });
    vector<int> dest(n);
    for (int k = 0; k < n; k++) {
        int i = fromOrder[k], j = toOrder[k];
        if (sequence[i] < target[j] || target[j] < sequence[i]) return -1;
        dest[i] = j;
    }

    vector<int> tree(n + 1, 0);
    long long swaps = 0;
    for (int i = n - 1; i >= 0; i--) {
        for (int idx = dest[i]; idx > 0; idx -= idx & -idx) swaps += tree[idx];
        for (int idx = dest[i] + 1; idx <= n; idx += idx & -idx) tree[idx]++;
    }

    return swaps;
}
