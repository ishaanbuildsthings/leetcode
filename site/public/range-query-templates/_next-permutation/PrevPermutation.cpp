// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/next-permutation/PrevPermutation.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// Returns a new vector / string with the previous (next smaller) permutation, with looping behavior around to the
// lexicographical largest permutation if we step past the lexicographical min
// works with a vector of comparable values (ints, longs, negatives, chars) or a string of chars
template <typename Seq>
Seq prevPermutation(Seq arrOrString) {
    int n = arrOrString.size();
    if (n == 0) return arrOrString;
    int i = n - 2;
    while (i >= 0 && !(arrOrString[i + 1] < arrOrString[i])) i--;
    if (i >= 0) {  // i < 0: it was the smallest, so reversing all of it loops around to the maximum
        int j = n - 1;
        while (!(arrOrString[j] < arrOrString[i])) j--;
        swap(arrOrString[i], arrOrString[j]);
    }
    reverse(arrOrString.begin() + i + 1, arrOrString.end());
    return arrOrString;
}
