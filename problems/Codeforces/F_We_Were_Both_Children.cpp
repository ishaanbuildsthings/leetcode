#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int t; cin >> t;
    while (t--) {
        int n; cin >> n;
        unordered_map<int, int> frq; // maps number -> freq
        frq.reserve(n * 2);
        frq.max_load_factor(0.7f);
        vector<int> A(n);
        for (int i = 0; i < n; i++) {
            cin >> A[i];
            frq[A[i]]++;
        }
        vector<int> hops(n + 1); // hops[i] is how many frogs hop there
        for (const auto& [key, val] : frq) {
            int position = key;
            while (position <= n) {
                hops[position] += val;
                position += key;
            }
        }
        cout << *max_element(hops.begin(), hops.end()) << endl;
    }
}

