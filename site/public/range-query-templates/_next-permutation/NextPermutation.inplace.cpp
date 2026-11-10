// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/next-permutation/NextPermutation.inplace.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// Moves arr in place to be the next permutation, with looping behavior around to the lexicographical smallest
// permutation if we step past the lexicographical max
// Works with a vector of any comparable item (int, long, negatives, char, etc)
template <typename T>
void nextPermutation(vector<T>& arr) {
    int n = arr.size();
    if (n == 0) return;
    int i = n - 2;
    while (i >= 0 && !(arr[i] < arr[i + 1])) i--;
    if (i >= 0) {  // i < 0: it was the largest, so reversing all of it loops around
        int j = n - 1;
        while (!(arr[i] < arr[j])) j--;
        swap(arr[i], arr[j]);
    }
    reverse(arr.begin() + i + 1, arr.end());
}
