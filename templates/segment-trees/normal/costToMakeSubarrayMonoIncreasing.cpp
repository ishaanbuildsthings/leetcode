#include <bits/stdc++.h>
using namespace std;
// Min increments to make a range non-decreasing (increments only). Static array, 0-indexed.
// Build: O(n log n) time/space.  query/argMax/rawSum: O(1).
// T = int or long long (deduced); all sums accumulate in long long.
template <class T>
struct MonoIncreaseCost {
    using S = long long;
    int n;
    std::vector<T> a;
    std::vector<S> pf, suff;          // suff[i] = sum of prefix maxes over [i, n)
    std::vector<std::vector<int>> sp; // sparse table of argmax (leftmost on ties)

    explicit MonoIncreaseCost(std::vector<T> arr) : n((int)arr.size()), a(std::move(arr)) {
        pf.assign(n + 1, 0);
        for (int i = 0; i < n; i++) pf[i + 1] = pf[i] + (S)a[i];

        suff.assign(n + 1, 0);
        std::vector<int> st;
        for (int i = n - 1; i >= 0; i--) {
            while (!st.empty() && a[st.back()] <= a[i]) st.pop_back();
            int nxt = st.empty() ? n : st.back();
            suff[i] = (S)a[i] * (nxt - i) + suff[nxt];
            st.push_back(i);
        }

        int LOG = 1;
        while ((1 << LOG) <= n) LOG++;
        sp.assign(LOG, {});
        sp[0].resize(n);
        std::iota(sp[0].begin(), sp[0].end(), 0);
        for (int j = 1; j < LOG; j++) {
            int len = n - (1 << j) + 1, half = 1 << (j - 1);
            sp[j].resize(len);
            for (int i = 0; i < len; i++) {
                int x = sp[j - 1][i], y = sp[j - 1][i + half];
                sp[j][i] = a[x] >= a[y] ? x : y;
            }
        }
    }

    // Sum of a[l..r] inclusive; 0 if l > r.  O(1).
    S rawSum(int l, int r) const { return r >= l ? pf[r + 1] - pf[l] : 0; }

    // Index of the maximum in a[l..r] inclusive, leftmost on ties.  O(1).
    int argMax(int l, int r) const {
        int j = std::__lg(r - l + 1);
        int x = sp[j][l], y = sp[j][r - (1 << j) + 1];
        return a[x] >= a[y] ? x : y;
    }

    // Min total increments to make a[l..r] inclusive non-decreasing.  O(1).
    S query(int l, int r) const {
        int m = argMax(l, r);
        S endsAt = (suff[l] - suff[m]) + (S)a[m] * (r - m + 1);
        return endsAt - rawSum(l, r);
    }
};
