// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/countOccurrences-leftmostIndexOf-leftmostIndexOfInRange-pointGet-rightmostIndexOf-rightmostIndexOfInRange/template.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: countOccurrences leftmostIndexOf leftmostIndexOfInRange pointGet rightmostIndexOf rightmostIndexOfInRange
// @data-structure-type: positions
// @letters: same
// @complexities:
//   countOccurrences: log(N)
//   leftmostIndexOf: log(N)
//   leftmostIndexOfInRange: log(N)
//   pointGet: 1
//   rightmostIndexOf: log(N)
//   rightmostIndexOfInRange: log(N)
//   build: N*log(N)
// @memory:
//   layout: none
//   node: pos[1*N]
//   tags: none
//   other: arr[1*N]
//   note: pos maps each value to the sorted list of indices holding it; the build sorts the (value, index) pairs, O(N log N)

// Static "how many times does x appear in a[l..r]?". All indices 0-based, ranges inclusive. T: any type with <.
// All (value, index) pairs sorted once; x's occurrences in [l, r] are one contiguous run, found by two binary searches.
template <typename T>
struct OccurrenceLists {
    vector<T> arr;
    vector<pair<T, int>> pos;  // (value, index), sorted

    // O(N log N)
    explicit OccurrenceLists(const vector<T>& a) : arr(a), pos(a.size()) {
        for (int i = 0; i < (int)a.size(); i++) pos[i] = {a[i], i};
        sort(pos.begin(), pos.end());
    }

    // O(logN) -- # of i in [l, r] with a[i] == x; needs 0 <= l <= r < size(), else throws out_of_range
    int countOccurrences(int l, int r, const T& x) const {
        if (l < 0 || l > r || r >= size()) throw out_of_range("countOccurrences: needs 0 <= l <= r < size()");
        if (l > r) return 0;
        return int(lower_bound(pos.begin(), pos.end(), pair<T, int>{x, r + 1}) - lower_bound(pos.begin(), pos.end(), pair<T, int>{x, l}));
    }

    // O(logN) -- the smallest i with a[i] == x, or -1 if x isn't in the array
    int leftmostIndexOf(const T& x) const { return leftmostIndexOfInRange(0, (int)arr.size() - 1, x); }

    // O(logN) -- the largest i with a[i] == x, or -1 if x isn't in the array
    int rightmostIndexOf(const T& x) const { return rightmostIndexOfInRange(0, (int)arr.size() - 1, x); }

    // O(logN) -- the smallest i in [l, r] with a[i] == x, or -1 if there is none; needs 0 <= l <= r < size(), else
    // throws out_of_range
    int leftmostIndexOfInRange(int l, int r, const T& x) const {
        if (l < 0 || l > r || r >= size()) throw out_of_range("leftmostIndexOfInRange: needs 0 <= l <= r < size()");
        auto it = lower_bound(pos.begin(), pos.end(), pair<T, int>{x, l});
        return it != pos.end() && it->first == x && it->second <= r ? it->second : -1;
    }

    // O(logN) -- the largest i in [l, r] with a[i] == x, or -1 if there is none; needs 0 <= l <= r < size(), else
    // throws out_of_range
    int rightmostIndexOfInRange(int l, int r, const T& x) const {
        if (l < 0 || l > r || r >= size()) throw out_of_range("rightmostIndexOfInRange: needs 0 <= l <= r < size()");
        auto it = lower_bound(pos.begin(), pos.end(), pair<T, int>{x, r + 1});
        if (it == pos.begin()) return -1;
        --it;
        return it->first == x && it->second >= l ? it->second : -1;
    }

    // O(1) -- the length of the array
    int size() const { return (int)arr.size(); }

    // O(1) -- a[i]; needs 0 <= i < size(), else throws out_of_range
    T pointGet(int i) const {
        if (i < 0 || i >= size()) throw out_of_range("pointGet: needs 0 <= i < size()");
        return arr[i];
    }
};
