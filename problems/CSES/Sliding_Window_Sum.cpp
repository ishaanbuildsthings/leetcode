#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, k;
    cin >> n >> k;

    long long x, a, b, c;
    cin >> x >> a >> b >> c;

    queue<long long> q;
    long long windowSum = 0;
    long long res = 0;

    for (int i = 1; i <= n; i++) {
        if (i > 1) x = (a * x + b) % c;

        q.push(x);
        windowSum += x;

        if ((int)q.size() > k) {
            windowSum -= q.front();
            q.pop();
        }

        if ((int)q.size() == k) {
            res ^= windowSum;
        }
    }

    cout << res << "\n";
    return 0;
}
