// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/next-permutation/NextPermutation.inplace.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// Moves arr in place to be the next permutation, if it was already the lexicographical largest it loops around.
// Works with a vector of any comparable item (int, long, negatives, char, etc)
template <typename T>
bool nextPermutation(vector<T>& arr) {
    int n = arr.size();
    if (n == 0) return false;
    int i = n - 2;
    while (i >= 0 && !(arr[i] < arr[i + 1])) i--;
    if (i >= 0) {  // i < 0: it was the largest, so reversing all of it loops around
        int j = n - 1;
        while (!(arr[i] < arr[j])) j--;
        swap(arr[i], arr[j]);
    }
    reverse(arr.begin() + i + 1, arr.end());
    return i >= 0;  // false when it looped around
}
