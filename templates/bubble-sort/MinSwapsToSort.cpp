// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/bubble-sort/MinSwapsToSort.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// sequence: a vector or a string of values that compare with each other: int, long long, negatives, chars ok
template <typename Seq>
long long minAdjacentSwapsToSort(const Seq& sequence) {
    int n = sequence.size();

    vector<int> placeOrder(n);
    iota(placeOrder.begin(), placeOrder.end(), 0);
    stable_sort(placeOrder.begin(), placeOrder.end(), [&](int idx1, int idx2) {
        return sequence[idx1] < sequence[idx2];
    });

    vector<int> tree(n + 1, 0);
    for (int i = 1; i <= n; i++) {
        tree[i] += 1;
        int parent = i + (i & -i);
        if (parent <= n) {
            tree[parent] += tree[i];
        }
    }

    auto countBefore = [&](int idx) {
        int total = 0;
        while (idx > 0) {
            total += tree[idx];
            idx -= idx & -idx;
        }
        return total;
    };

    auto add = [&](int idx, int delta) {
        idx += 1;
        while (idx <= n) {
            tree[idx] += delta;
            idx += idx & -idx;
        }
    };

    long long swaps = 0;
    for (int idx : placeOrder) {
        swaps += countBefore(idx);
        add(idx, -1);
    }

    return swaps;
}