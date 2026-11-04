// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/bubble-sort/MinSwapsToSort.cpp
#include <bits/stdc++.h>
using namespace std;

// Minimum adjacent swaps to sort arr into non-decreasing order (= bubble sort swap count)
// Equal values are never swapped past each other, so ties cost nothing
// Works for any comparable T (int, long long, etc.); answer can reach ~n^2/2, so returns long long
// Time: O(n log n), Space: O(n)
template <typename T>
long long minAdjacentSwapsToSort(const vector<T>& arr) {
    int n = arr.size();

    // original indices in the order their values get placed (smallest first, ties by position)
    vector<int> placeOrder(n);
    iota(placeOrder.begin(), placeOrder.end(), 0);
    stable_sort(placeOrder.begin(), placeOrder.end(), [&](int idx1, int idx2) {
        return arr[idx1] < arr[idx2];
    });

    // Fenwick tree over original indices, 1-based internally
    // every index starts as 1 (unplaced); built in O(n)
    vector<int> tree(n + 1, 0);
    for (int i = 1; i <= n; i++) {
        tree[i] += 1;
        int parent = i + (i & -i);
        if (parent <= n) {
            tree[parent] += tree[i];
        }
    }

    // number of unplaced indices among original indices [0, idx)
    auto countBefore = [&](int idx) {
        int total = 0;
        while (idx > 0) {
            total += tree[idx];
            idx -= idx & -idx;
        }
        return total;
    };

    // adds delta to original index idx (delta = -1 marks it placed)
    auto add = [&](int idx, int delta) {
        idx += 1;
        while (idx <= n) {
            tree[idx] += delta;
            idx += idx & -idx;
        }
    };

    long long swaps = 0;
    for (int idx : placeOrder) {
        swaps += countBefore(idx);  // unplaced values still in front of this one
        add(idx, -1);
    }

    return swaps;
}