// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/next-permutation/PrevPermutation.cpp
#include <bits/stdc++.h>
using namespace std;

// The next smaller arrangement of sequence (a new vector, or a string for a string), or nullopt if it is the smallest
// sequence: a vector or a string of values that compare with each other: int, long long, negatives, chars ok
template <typename Seq>
optional<Seq> prevPermutation(Seq sequence) {
    int n = sequence.size();
    int i = n - 2;
    while (i >= 0 && !(sequence[i + 1] < sequence[i])) i--;
    if (i < 0) return nullopt;
    int j = n - 1;
    while (!(sequence[j] < sequence[i])) j--;
    swap(sequence[i], sequence[j]);
    reverse(sequence.begin() + i + 1, sequence.end());
    return sequence;
}
