// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/bubble-sort/MinSwapsToTarget.cpp
#include <bits/stdc++.h>
using namespace std;

// Minimum adjacent swaps to turn arr into target, or -1 if target isn't a rearrangement of arr
// The k-th copy of a value in arr always goes to the k-th copy of it in target (crossing two equal values never helps),
// so the answer is the number of inversions of where each element has to go
// Seq: string, vector<int>, vector<long long>, ... (any comparable values); answer can reach ~n^2/2, so long long
// Time: O(n log n), Space: O(n)
template <typename Seq>
long long minAdjacentSwapsToTarget(const Seq& arr, const Seq& target) {
    int n = arr.size();
    if ((int)target.size() != n) return -1;

    // pair the k-th copy of each value in arr with its k-th copy in target: both sorted by (value, position)
    vector<int> fromOrder(n), toOrder(n);
    iota(fromOrder.begin(), fromOrder.end(), 0);
    iota(toOrder.begin(), toOrder.end(), 0);
    stable_sort(fromOrder.begin(), fromOrder.end(), [&](int i, int j) { return arr[i] < arr[j]; });
    stable_sort(toOrder.begin(), toOrder.end(), [&](int i, int j) { return target[i] < target[j]; });
    vector<int> dest(n);  // dest[i]: the index arr[i] has to end up at
    for (int k = 0; k < n; k++) {
        int i = fromOrder[k], j = toOrder[k];
        if (arr[i] < target[j] || target[j] < arr[i]) return -1;
        dest[i] = j;
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
