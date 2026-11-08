#include <bits/stdc++.h>
using namespace std;

// TEMPLATE BY github.com/ishaanbuildsthings PLEASE DO NOT USE

// gives the least/greatest lexicographical rotation of any comparable container (string, vector<int>, vector<ll>) in O(n) time


// Returns every start index whose rotation equals the lexicographically smallest one, ascending.
// minRotationIndices("bcabca") -> {2, 5} // starting indices that have the min rotation (if multiple, those are equal rotations)
// minRotationIndices({2, 1, 2, 1}) -> {1, 3}
// O(n) time, O(1) extra space for the scan
template <class T>
vector<int> minRotationIndices(const T& stringOrArray) {
    int n = (int)stringOrArray.size();
    if (n == 0) return {};
    int i = 0, ans = 0, period = n;
    while (i < n) {
        ans = i;
        int j = i + 1, k = i;
        while (j < 2 * n) {
            const auto& a = stringOrArray[k >= n ? k - n : k];
            const auto& b = stringOrArray[j >= n ? j - n : j];
            if (b < a) break;
            k = (a < b) ? i : k + 1;
            j++;
        }
        period = j - k;
        while (i <= k) i += j - k;
    }
    if (period <= 0 || n % period) period = n; // guard, unreachable on a completed scan
    vector<int> res;
    res.reserve(n / period);
    for (int x = ans % period; x < n; x += period) res.push_back(x);
    return res;
}

// Returns every start index whose rotation equals the lexicographically largest one, ascending.
// maxRotationIndices("bcabca") -> {1, 4} // starting indices that have the max rotation (if multiple, those are equal rotations)
// maxRotationIndices({2, 1, 2, 1}) -> {0, 2}
// O(n) time, O(1) extra space for the scan
template <class T>
vector<int> maxRotationIndices(const T& stringOrArray) {
    int n = (int)stringOrArray.size();
    if (n == 0) return {};
    int i = 0, ans = 0, period = n;
    while (i < n) {
        ans = i;
        int j = i + 1, k = i;
        while (j < 2 * n) {
            const auto& a = stringOrArray[k >= n ? k - n : k];
            const auto& b = stringOrArray[j >= n ? j - n : j];
            if (b > a) break;
            k = (a > b) ? i : k + 1;
            j++;
        }
        period = j - k;
        while (i <= k) i += j - k;
    }
    if (period <= 0 || n % period) period = n; // guard, unreachable on a completed scan
    vector<int> res;
    res.reserve(n / period);
    for (int x = ans % period; x < n; x += period) res.push_back(x);
    return res;
}

// Returns the lexicographically smallest rotation.
// minRotation("bcabca") -> "abcabc" // the rotation itself, use minRotationIndices for where it starts
// minRotation({2, 1, 2, 1}) -> {1, 2, 1, 2}
// O(n) time
template <class T>
T minRotation(const T& stringOrArray) {
    vector<int> idx = minRotationIndices(stringOrArray);
    if (idx.empty()) return stringOrArray;
    int i = idx[0];
    T res(stringOrArray.begin() + i, stringOrArray.end());
    res.insert(res.end(), stringOrArray.begin(), stringOrArray.begin() + i);
    return res;
}

// Returns the lexicographically largest rotation.
// maxRotation("bcabca") -> "cabcab" // the rotation itself, use maxRotationIndices for where it starts
// maxRotation({2, 1, 2, 1}) -> {2, 1, 2, 1}
// O(n) time
template <class T>
T maxRotation(const T& stringOrArray) {
    vector<int> idx = maxRotationIndices(stringOrArray);
    if (idx.empty()) return stringOrArray;
    int i = idx[0];
    T res(stringOrArray.begin() + i, stringOrArray.end());
    res.insert(res.end(), stringOrArray.begin(), stringOrArray.begin() + i);
    return res;
}