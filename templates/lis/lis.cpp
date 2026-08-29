// Given an array, returns a lis length + a lis in N log N time
// STRICTLY INCREASING LIS

#include <vector>
#include <algorithm>
using namespace std;

pair<int, vector<int>> strictlyIncreasingLisAndSequence(const vector<int>& nums) {
    int n = nums.size();
    if (n == 0) {
        return {0, {}};
    }

    vector<int> tails;
    vector<int> tailsIndex;
    vector<int> prevIndex(n, -1);

    for (int i = 0; i < n; i++) {
        int val = nums[i];
        int pos = lower_bound(tails.begin(), tails.end(), val) - tails.begin();
        if (pos == (int)tails.size()) {
            tails.push_back(val);
            tailsIndex.push_back(i);
        } else {
            tails[pos] = val;
            tailsIndex[pos] = i;
        }
        if (pos > 0) {
            prevIndex[i] = tailsIndex[pos - 1];
        }
    }

    int length = tails.size();
    vector<int> seq;
    int idx = tailsIndex.back();
    while (idx != -1) {
        seq.push_back(nums[idx]);
        idx = prevIndex[idx];
    }
    reverse(seq.begin(), seq.end());

    return {length, seq};
}


pair<int, vector<int>> monoIncreasingLisAndSequence(const vector<int>& nums) {
    int n = nums.size();
    if (n == 0) {
        return {0, {}};
    }

    vector<int> tails;
    vector<int> tailsIndex;
    vector<int> prevIndex(n, -1);

    for (int i = 0; i < n; i++) {
        int val = nums[i];
        int pos = upper_bound(tails.begin(), tails.end(), val) - tails.begin();  // allow equals to extend
        if (pos == (int)tails.size()) {
            tails.push_back(val);
            tailsIndex.push_back(i);
        } else {
            tails[pos] = val;
            tailsIndex[pos] = i;
        }
        if (pos > 0) {
            prevIndex[i] = tailsIndex[pos - 1];
        }
    }

    int length = tails.size();
    vector<int> seq;
    int idx = tailsIndex.back();
    while (idx != -1) {
        seq.push_back(nums[idx]);
        idx = prevIndex[idx];
    }
    reverse(seq.begin(), seq.end());

    return {length, seq};
}