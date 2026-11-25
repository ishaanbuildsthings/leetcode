// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/lis/lis.cpp
#include <bits/stdc++.h>
using namespace std;

// Longest increasing / decreasing subsequence, O(n log n). Each function returns {length, one longest subsequence}:
//   vector<int> nums = {3, 1, 2, 2, 5, 4};
//   strictlyIncreasingLis(nums)  -> {3, {1, 2, 4}}       each value > the one before
//   monoIncreasingLis(nums)      -> {4, {1, 2, 2, 4}}    each value >= the one before
//   strictlyDecreasingLis(nums)  -> {2, {5, 4}}          each value < the one before
//   monoDecreasingLis(nums)      -> {3, {3, 2, 2}}       each value <= the one before
//   auto [len, seq] = strictlyIncreasingLis(nums);
// Empty nums gives {0, {}}. Works for any T with < (int, long long, double, ...).

template <typename T, typename Cmp>
pair<int, vector<T>> lisWith(const vector<T>& nums, Cmp cmp, bool allowEqual) {
    // tails[k] = the best last value (by cmp) of a subsequence of length k + 1 seen so far
    vector<T> tails;
    vector<int> tailsIndex, prevIndex(nums.size(), -1);
    for (int i = 0; i < (int)nums.size(); i++) {
        auto it = allowEqual ? upper_bound(tails.begin(), tails.end(), nums[i], cmp)
                             : lower_bound(tails.begin(), tails.end(), nums[i], cmp);
        int pos = it - tails.begin();
        if (pos == (int)tails.size()) tails.push_back(nums[i]), tailsIndex.push_back(i);
        else tails[pos] = nums[i], tailsIndex[pos] = i;
        if (pos > 0) prevIndex[i] = tailsIndex[pos - 1];
    }
    vector<T> seq;
    for (int idx = tailsIndex.empty() ? -1 : tailsIndex.back(); idx != -1; idx = prevIndex[idx]) seq.push_back(nums[idx]);
    reverse(seq.begin(), seq.end());
    return {(int)seq.size(), seq};
}

// O(n log n) -- {length, subsequence} where each value is > the one before
template <typename T>
pair<int, vector<T>> strictlyIncreasingLis(const vector<T>& nums) { return lisWith(nums, less<T>(), false); }

// O(n log n) -- {length, subsequence} where each value is >= the one before
template <typename T>
pair<int, vector<T>> monoIncreasingLis(const vector<T>& nums) { return lisWith(nums, less<T>(), true); }

// O(n log n) -- {length, subsequence} where each value is < the one before
template <typename T>
pair<int, vector<T>> strictlyDecreasingLis(const vector<T>& nums) { return lisWith(nums, greater<T>(), false); }

// O(n log n) -- {length, subsequence} where each value is <= the one before
template <typename T>
pair<int, vector<T>> monoDecreasingLis(const vector<T>& nums) { return lisWith(nums, greater<T>(), true); }
