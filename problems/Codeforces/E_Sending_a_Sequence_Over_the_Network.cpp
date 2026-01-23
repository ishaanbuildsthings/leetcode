#include <bits/stdc++.h>
using namespace std;
int main() {
    cin.tie(nullptr);
    ios::sync_with_stdio(false);
    int t; cin >> t;
    while (t--) {
        int n; cin >> n;
        vector<int> A(n); for (int i = 0; i < n; i++) cin >> A[i];
        set<int> doable; // i... is doable
        doable.insert(n);
        for (int i = n - 1; i >= 0; i--) {
            int v = A[i];
            int right = v + i + 1; // 1 2 3 4 5 5 we are at the 3 which is index 2, 6 is doable (the end of the sequence)
            if (doable.find(right) != doable.end()) {
                doable.insert(i);
            }
            if (doable.find(i + 1) != doable.end()) {
                doable.insert(i - v);
            }
        }
        cout << (doable.find(0) != doable.end() ? "YES" : "NO") << endl;
    }
}