// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/next-permutation/PrevPermutation.inplace.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// Moves arr in place to be the previous permutation, with looping behavior around to the lexicographical largest permutation if we step past the lexicographical min
// Works with a vector of any comparable item (int, long, negatives, char, etc)
template <typename T>
bool prevPermutation(vector<T>& arr) {
    int n = arr.size();
    if (n == 0) return false;
    int i = n - 2;
    while (i >= 0 && !(arr[i + 1] < arr[i])) i--;
    if (i >= 0) {  // i < 0: it was the smallest, so reversing all of it loops around
        int j = n - 1;
        while (!(arr[j] < arr[i])) j--;
        swap(arr[i], arr[j]);
    }
    reverse(arr.begin() + i + 1, arr.end());
    return i >= 0;  // false when it looped around
}
