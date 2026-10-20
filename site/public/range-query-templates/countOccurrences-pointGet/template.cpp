// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/countOccurrences-pointGet/template.cpp
// @operations: countOccurrences pointGet
// @data-structure-type: positions
// @complexities:
//   countOccurrences: log(N)
//   pointGet: 1
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

    // O(logN) -- # of i in [l, r] with a[i] == x
    int countOccurrences(int l, int r, const T& x) const {
        if (l > r) return 0;
        return int(lower_bound(pos.begin(), pos.end(), pair<T, int>{x, r + 1}) - lower_bound(pos.begin(), pos.end(), pair<T, int>{x, l}));
    }

    // O(1) -- a[i]
    T pointGet(int i) const { return arr[i]; }
};
