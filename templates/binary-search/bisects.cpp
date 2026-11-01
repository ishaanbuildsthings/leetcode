#include<bits/stdc++.h>
using namespace std;

// Works for ints and floats. NaN is not supported.
// "first" functions return arr.size() if nothing qualifies.
// "last" functions return -1 if nothing qualifies.
// Each function is O(log n) or O(1).


// FOR INCREASING ARRAYS

template<typename T>
int firstIndexLT(const vector<T>& arr, T threshold) {
    return !arr.empty() && arr[0] < threshold ? 0 : (int)arr.size();
}

template<typename T>
int lastIndexLT(const vector<T>& arr, T threshold) {
    int index = lower_bound(arr.begin(), arr.end(), threshold) - arr.begin();
    return index - 1;
}

template<typename T>
int firstIndexLTE(const vector<T>& arr, T threshold) {
    return !arr.empty() && arr[0] <= threshold ? 0 : (int)arr.size();
}

template<typename T>
int lastIndexLTE(const vector<T>& arr, T threshold) {
    int index = upper_bound(arr.begin(), arr.end(), threshold) - arr.begin();
    return index - 1;
}

template<typename T>
int firstIndexGT(const vector<T>& arr, T threshold) {
    return upper_bound(arr.begin(), arr.end(), threshold) - arr.begin();
}

template<typename T>
int lastIndexGT(const vector<T>& arr, T threshold) {
    return !arr.empty() && arr.back() > threshold ? (int)arr.size() - 1 : -1;
}

template<typename T>
int firstIndexGTE(const vector<T>& arr, T threshold) {
    return lower_bound(arr.begin(), arr.end(), threshold) - arr.begin();
}

template<typename T>
int lastIndexGTE(const vector<T>& arr, T threshold) {
    return !arr.empty() && arr.back() >= threshold ? (int)arr.size() - 1 : -1;
}


// FOR DECREASING ARRAYS
// Passing greater<T>() tells lower_bound / upper_bound the array is sorted
// in decreasing order.

template<typename T>
int firstIndexLTDecreasing(const vector<T>& arr, T threshold) {
    return upper_bound(arr.begin(), arr.end(), threshold, greater<T>()) - arr.begin();
}

template<typename T>
int lastIndexLTDecreasing(const vector<T>& arr, T threshold) {
    return !arr.empty() && arr.back() < threshold ? (int)arr.size() - 1 : -1;
}

template<typename T>
int firstIndexLTEDecreasing(const vector<T>& arr, T threshold) {
    return lower_bound(arr.begin(), arr.end(), threshold, greater<T>()) - arr.begin();
}

template<typename T>
int lastIndexLTEDecreasing(const vector<T>& arr, T threshold) {
    return !arr.empty() && arr.back() <= threshold ? (int)arr.size() - 1 : -1;
}

template<typename T>
int firstIndexGTDecreasing(const vector<T>& arr, T threshold) {
    return !arr.empty() && arr[0] > threshold ? 0 : (int)arr.size();
}

template<typename T>
int lastIndexGTDecreasing(const vector<T>& arr, T threshold) {
    int index = lower_bound(arr.begin(), arr.end(), threshold, greater<T>()) - arr.begin();
    return index - 1;
}

template<typename T>
int firstIndexGTEDecreasing(const vector<T>& arr, T threshold) {
    return !arr.empty() && arr[0] >= threshold ? 0 : (int)arr.size();
}

template<typename T>
int lastIndexGTEDecreasing(const vector<T>& arr, T threshold) {
    int index = upper_bound(arr.begin(), arr.end(), threshold, greater<T>()) - arr.begin();
    return index - 1;
}