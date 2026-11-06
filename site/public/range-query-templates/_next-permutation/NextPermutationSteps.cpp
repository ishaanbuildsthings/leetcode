// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/next-permutation/NextPermutationSteps.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// Can pass in a vector of any comparable values (ints, longs, negatives, chars) or a string, and a # of steps which can be very large
// Returns a new permutation in the same format, that many steps forward, with looping behavior around to the lexicographical smallest permutation if we step past the lexicographical max
template <typename Seq>
Seq nextPermutation(Seq arrOrString, long long steps) {
    using i128 = __int128;
    int n = arrOrString.size();
    if (steps == 0) return arrOrString;

    vector<int> order(n), rk(n);
    iota(order.begin(), order.end(), 0);
    stable_sort(order.begin(), order.end(), [&](int i, int j) { return arrOrString[i] < arrOrString[j]; });
    vector<typename Seq::value_type> vals;
    for (int k = 0; k < n; k++) {
        int i = order[k];
        if (vals.empty() || vals.back() < arrOrString[i]) vals.push_back(arrOrString[i]);
        rk[i] = vals.size() - 1;
    }
    int d = vals.size();

    i128 cap = ((i128)steps + 1) * (n + 1);
    vector<int> cnt(d, 0), fen(d + 1, 0);
    i128 arrangements = 1, after = 0, afterNext = 0;
    int s = n;
    while (after < steps) {
        if (s == 0) {  // fewer than steps arrangements come after arrOrString: loop around to the smallest and count on from there
            long long r = (long long)((steps - after - 1) % arrangements);  // arrangements: how many in all (or more than steps)
            sort(arrOrString.begin(), arrOrString.end());
            return nextPermutation(arrOrString, r);
        }
        s--;
        int v = rk[s], len = n - s;
        cnt[v]++;
        int atMost = 0;
        for (int i = v + 1; i <= d; i += i & -i) fen[i]++;
        for (int i = v + 1; i > 0; i -= i & -i) atMost += fen[i];
        arrangements = min(cap, arrangements * len / cnt[v]);
        afterNext = after;
        after = min(cap, after + arrangements * (len - atMost) / len);
    }

    int v = rk[s], len = n - s, w = v + 1;
    i128 r = steps - afterNext - 1;
    for (;; w++) {
        if (!cnt[w]) continue;
        i128 c = arrangements * cnt[w] / len;
        if (r < c) break;
        r -= c;
    }

    vector<int> rest(rk.begin() + s, rk.end());
    sort(rest.begin(), rest.end());
    rest.erase(find(rest.begin(), rest.end(), w));
    int m = rest.size(), t = m;
    vector<int> tc(d, 0);
    i128 tailCount = 1;
    while (tailCount <= r) {
        t--;
        tc[rest[t]]++;
        tailCount = tailCount * (m - t) / tc[rest[t]];
    }
    int lo = t < m ? rest[t] : 0;
    for (int pos = t; pos < m; pos++) {
        for (int x = lo;; x++) {
            if (!tc[x]) continue;
            i128 c = tailCount * tc[x] / (m - pos);
            if (r < c) {
                rest[pos] = x, tc[x]--, tailCount = c;
                break;
            }
            r -= c;
        }
    }

    arrOrString[s] = vals[w];
    for (int k = 0; k < m; k++) arrOrString[s + 1 + k] = vals[rest[k]];
    return arrOrString;
}
