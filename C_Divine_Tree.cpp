#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int t; cin >> t;
    while (t--) {
        long long n, totalDivine; cin >> n >> totalDivine;

        long long maxGain = n * (n + 1) / 2;
        if (totalDivine > maxGain) {
            cout << -1 << endl;
            continue;
        }
        if (totalDivine < n) {
            cout << -1 << endl;
            continue;
        }

        deque<int> q;
        for (int num = 1; num <= n; num++) {
            q.push_back(num);
        }

        long long remain = totalDivine - n;
        int movedtoBack = 0;

        for (int numberToMove = 1; numberToMove <= n; numberToMove++) {
            long long gainable = n - numberToMove;
            if (gainable >= remain) {
                int popped = q.front(); q.pop_front();
                q.insert(q.begin() + remain, popped);
                break;
            }

            remain -= gainable;
            movedtoBack = numberToMove;
            q.pop_front();
        }
        for (int number = movedtoBack; number > 0; number--) {
            q.push_back(number);
        }
        cout << q[0] << endl;
        for (int i = 0; i < q.size() - 1; i++) {
            cout << q[i] << " " << q[i + 1] << endl;
        }
    }
}