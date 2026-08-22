#include <bits/stdc++.h>
using namespace std;
#pragma GCC target("popcnt")

int main() {
    int n, k; cin >> n >> k;
    vector<long long> nums;
    for (int i = 0; i < n; i++) {
        string s; cin >> s;
        long long v = stoll(s, nullptr, 2);    
        nums.push_back(v);
    }
    long long res = 1000000000000000;
    for (int i = 0; i < n; i++) {
        for (int j = i + 1; j < n; j++) {
            res = min(res, (long long)__builtin_popcount((nums[i] ^ nums[j])));
        }
    }
    cout << res;
}