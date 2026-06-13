#include <bits/stdc++.h>
using namespace std;

long long solve(vector<int>& arr, int k) {
    int n = arr.size();
    vector<vector<long long>> cache(n, vector<long long>(k + 1, -1));

    function<long long(int, int)> dp = [&](int i, int currUsed) -> long long {
        if (i == n) return 0;
        long long& res = cache[i][currUsed];
        if (res != -1) return res;

        long long ifSkip = dp(i + 1, currUsed) + arr[i];
        long long b = ifSkip;
        int smallest = arr[i];

        for (int j = i + 1; j <= i + k && j < n; ++j) {
            int morphs = j - i;
            int width = morphs + 1;
            if (morphs + currUsed > k) break;
            smallest = std::min(smallest, arr[j]);
            long long sumHere = 1LL * smallest * width + dp(j + 1, currUsed + morphs);
            b = std::min(b, sumHere);
        }
        return res = b;
    };

    return dp(0, 0);
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int t;
    cin >> t;
    while (t--) {
        int n, k;
        cin >> n >> k;
        vector<int> arr(n);
        for (int i = 0; i < n; ++i) cin >> arr[i];
        cout << solve(arr, k) << '\n';
    }
    return 0;
}