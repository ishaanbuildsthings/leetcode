// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/next-permutation/NextPermutation.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// Returns a new vector / string with the next larger permutation, or loops around to the minimum if it was already the largest
// works with a vector of comparable values (ints, longs, negatives, chars) or a string of chars
template <typename Seq>
Seq nextPermutation(Seq arr) {
    int n = arr.size();
    if (n == 0) return arr;
    int i = n - 2;
    while (i >= 0 && !(arr[i] < arr[i + 1])) i--;
    if (i >= 0) {  // i < 0: it was the largest, so reversing all of it loops around to the minimum
        int j = n - 1;
        while (!(arr[i] < arr[j])) j--;
        swap(arr[i], arr[j]);
    }
    reverse(arr.begin() + i + 1, arr.end());
    return arr;
}
