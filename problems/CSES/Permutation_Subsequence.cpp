#include <bits/stdc++.h>
using namespace std;
using ll = long long;


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

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m; cin >> n >> m;
    vector<int> A(n); for (int i = 0; i < n; i++) cin >> A[i];
    vector<int> B(m); for (int i = 0; i < m; i++) cin >> B[i];
    // labels[num] -> new value
    vector<int> labels(n + 1);
    for (int i = 0; i < n; i++) {
        labels[A[i]] = i + 1;
    }
    vector<int> newB;
    for (int i = 0; i < m; i++) {
        int v = B[i];
        if (v <= n) {
            newB.push_back(labels[v]);
        }
    }

    auto [lis, seq] = monoIncreasingLisAndSequence(newB);
    cout << lis << '\n';
    for (auto x : seq) {
        cout << A[x - 1] << ' ';
    }
}