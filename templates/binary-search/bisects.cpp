#include<bits/stdc++.h>
using namespace std;

// Works for ints and floats. NaN is not supported.
// "first" functions return arr.size() if nothing qualifies.
// "last" functions return -1 if nothing qualifies.
// Each function is O(log n) or O(1).
// threshold can be a different type from the values (an int array with a long long or a double threshold is fine).


// FOR INCREASING ARRAYS

template<typename T, typename U>
int firstIndexLT(const vector<T>& arr, U threshold) {
    return !arr.empty() && arr[0] < threshold ? 0 : (int)arr.size();
}

template<typename T, typename U>
int lastIndexLT(const vector<T>& arr, U threshold) {
    int index = lower_bound(arr.begin(), arr.end(), threshold) - arr.begin();
    return index - 1;
}

template<typename T, typename U>
int firstIndexLTE(const vector<T>& arr, U threshold) {
    return !arr.empty() && arr[0] <= threshold ? 0 : (int)arr.size();
}

template<typename T, typename U>
int lastIndexLTE(const vector<T>& arr, U threshold) {
    int index = upper_bound(arr.begin(), arr.end(), threshold) - arr.begin();
    return index - 1;
}

template<typename T, typename U>
int firstIndexGT(const vector<T>& arr, U threshold) {
    return upper_bound(arr.begin(), arr.end(), threshold) - arr.begin();
}

template<typename T, typename U>
int lastIndexGT(const vector<T>& arr, U threshold) {
    return !arr.empty() && arr.back() > threshold ? (int)arr.size() - 1 : -1;
}

template<typename T, typename U>
int firstIndexGTE(const vector<T>& arr, U threshold) {
    return lower_bound(arr.begin(), arr.end(), threshold) - arr.begin();
}

template<typename T, typename U>
int lastIndexGTE(const vector<T>& arr, U threshold) {
    return !arr.empty() && arr.back() >= threshold ? (int)arr.size() - 1 : -1;
}


// FOR DECREASING ARRAYS
// Passing greater<>() tells lower_bound / upper_bound the array is sorted
// in decreasing order.

template<typename T, typename U>
int firstIndexLTDecreasing(const vector<T>& arr, U threshold) {
    return upper_bound(arr.begin(), arr.end(), threshold, greater<>()) - arr.begin();
}

template<typename T, typename U>
int lastIndexLTDecreasing(const vector<T>& arr, U threshold) {
    return !arr.empty() && arr.back() < threshold ? (int)arr.size() - 1 : -1;
}

template<typename T, typename U>
int firstIndexLTEDecreasing(const vector<T>& arr, U threshold) {
    return lower_bound(arr.begin(), arr.end(), threshold, greater<>()) - arr.begin();
}

template<typename T, typename U>
int lastIndexLTEDecreasing(const vector<T>& arr, U threshold) {
    return !arr.empty() && arr.back() <= threshold ? (int)arr.size() - 1 : -1;
}

template<typename T, typename U>
int firstIndexGTDecreasing(const vector<T>& arr, U threshold) {
    return !arr.empty() && arr[0] > threshold ? 0 : (int)arr.size();
}

template<typename T, typename U>
int lastIndexGTDecreasing(const vector<T>& arr, U threshold) {
    int index = lower_bound(arr.begin(), arr.end(), threshold, greater<>()) - arr.begin();
    return index - 1;
}

template<typename T, typename U>
int firstIndexGTEDecreasing(const vector<T>& arr, U threshold) {
    return !arr.empty() && arr[0] >= threshold ? 0 : (int)arr.size();
}

template<typename T, typename U>
int lastIndexGTEDecreasing(const vector<T>& arr, U threshold) {
    int index = upper_bound(arr.begin(), arr.end(), threshold, greater<>()) - arr.begin();
    return index - 1;
}
