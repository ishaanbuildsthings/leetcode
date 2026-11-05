// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/next-permutation/PrevPermutation.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// Returns a new vector / string with the next smaller permutation, or loops around to the maximum if it was already the smallest
// works with a vector of comparable values (ints, longs, negatives, chars) or a string of chars
template <typename Seq>
Seq prevPermutation(Seq arr) {
    int n = arr.size();
    if (n == 0) return arr;
    int i = n - 2;
    while (i >= 0 && !(arr[i + 1] < arr[i])) i--;
    if (i >= 0) {  // i < 0: it was the smallest, so reversing all of it loops around to the maximum
        int j = n - 1;
        while (!(arr[j] < arr[i])) j--;
        swap(arr[i], arr[j]);
    }
    reverse(arr.begin() + i + 1, arr.end());
    return arr;
}
