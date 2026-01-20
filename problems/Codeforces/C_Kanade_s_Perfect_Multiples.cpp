#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int t; cin >> t;
    while (t--) {
        int n, k; cin >> n >> k;
        vector<int> A(n); for (int i = 0; i < n; i++) cin >> A[i];
        sort(A.begin(), A.end());
        vector<int> out;
        unordered_set<int> taken;
        unordered_set<int> aset;
        for (auto x : A) aset.insert(x);
        bool FAIL = false;

        for (auto num : A) {
            // If this number is covered no need to take it
            if (taken.find(num) != taken.end()) {
                continue;
            }
            taken.insert(num);
            out.push_back(num);
            int mult = num * 2;
            while (mult <= k) {
                taken.insert(mult);
                if (aset.find(mult) == aset.end()) {
                    // If the multiple of this number isn't in the array we could not take it and we fail
                    FAIL = true;
                    break;
                }
                mult += num;
            }
            if (FAIL) break;
        }
        if (FAIL) {
            cout << -1 << endl;
            continue;
        }
        cout << out.size() << endl;
        for (auto x : out) cout << x << " ";
        cout << endl;
    }
}