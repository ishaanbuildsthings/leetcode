// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/next-permutation/PrevPermutation.inplace.cpp
#include <bits/stdc++.h>
using namespace std;

// Rearranges sequence (a vector or a string) into the next smaller arrangement in place and returns true, or returns
// false (sequence unchanged) if it is the smallest; consecutive calls cost O(1) amortized, unless almost every value is
// the same
// sequence: a vector or a string of values that compare with each other: int, long long, negatives, chars ok
template <typename Seq>
bool prevPermutation(Seq& sequence) {
    int n = sequence.size();
    int i = n - 2;
    while (i >= 0 && !(sequence[i + 1] < sequence[i])) i--;
    if (i < 0) return false;
    int j = n - 1;
    while (!(sequence[j] < sequence[i])) j--;
    swap(sequence[i], sequence[j]);
    reverse(sequence.begin() + i + 1, sequence.end());
    return true;
}
