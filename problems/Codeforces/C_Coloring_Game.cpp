#include <bits/stdc++.h>
using namespace std;

int countInRange(const vector<int>& arr, int l, int r) {
    if (l > r) return 0;
    auto left = lower_bound(arr.begin(), arr.end(), l);
    auto right = upper_bound(arr.begin(), arr.end(), r);
    return (int)(right - left);
}


int main() {
    cin.tie(nullptr);
    ios::sync_with_stdio(false);
    int t; cin >> t;
    while (t--) {
        int n; cin >> n;
        vector<int> A(n); for (int i = 0; i < n; i++) cin >> A[i];
        sort(A.begin(), A.end());
        unordered_map<int,int> c;
        for (auto x : A) c[x]++;
        long long res = 0;
        int mx = *max_element(A.begin(), A.end());
        for (int i = 0; i < A.size(); i++) {
            int a = A[i];
            for (int j = i + 1; j < A.size(); j++) {
                int b = A[j];
                int maxC = a + b - 1;
                int minC = mx - a - b + 1;
                minC = max(minC, b + 1);
                int cnt = countInRange(A, minC, maxC);
                res += cnt;
            }
        }
        // add triplets
        for (const auto& kv : c) {
            auto key = kv.first;
            if (c[key] >= 3) {
                if (key * 3 > mx) {
                    long long ways = 1LL * c[key] * (c[key] - 1) * (c[key] - 2) / 6;
                    res += ways;
                }
            }
        }

        // add pairs
        vector<long long> keys;
        keys.reserve(c.size());
        for (auto &kv : c) keys.push_back(kv.first);
        sort(keys.begin(), keys.end());
    
        for (int i = 0; i < (int)keys.size(); i++) {
            long long low = keys[i];
            for (int j = i + 1; j < (int)keys.size(); j++) {
                long long high = keys[j];
                if (c[high] >= 2 && high + high + low > mx) {
                    res += c[low] * c[high] * (c[high] - 1) / 2;
                }
            }
        }

        cout << res << endl;
    }
}