#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n; cin >> n;
    vector<int> A(n);
    for (int i = 0; i < n; i++) {
        A[i] = i;
    }

    vector<bool> removed(n + 1, false);
    int i = 0;
    int removedCount = 0;
    int validSeen = 0;

    while (removedCount < n) {
            if (removed[i]) {
                i++;
                if (i == n) {
                    i = 0;
                }
                continue;
            };
            if (validSeen == 0) {
                validSeen = 1;
                i++;
                if (i == n) {
                    i = 0;
                }
                continue;
            }
            validSeen = 0;
            cout << i + 1 << " ";
            removed[i] = true;
            removedCount++;
            i++;
            if (i == n) {
                i = 0;
            }
    }
}

// 1 2 3 4 5 6 7
//   ^