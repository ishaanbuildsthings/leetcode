#include <bits/stdc++.h>
using namespace std;

int main() {
    long long n; cin >> n;
    long long tot = n * (n + 1) / 2;
    if (tot % 2) {
        cout << "NO";
        return 0;
    }
    cout << "YES" << endl;
    long long half = tot / 2;
    // Keep taking from the left until we overflow, then subtract
    // We are guaranteed to be able to make all sums of 1 using just 1
    // So when we add a 2, we can make 2, and all previous sums added (up to 3)
    // Now when we add 3, we can add it to all previous ranges, so up to 6, and so on
    // Eventually we will overflow the target by some amount < the number we just added at the end, so we can remove that single number
    
    long long curr = 0;
    int brokeBarrier = -1;
    for (int number = 1; number <= n; number++) {
        curr += number;
        if (curr >= half) {
            brokeBarrier = number;
            break;
        }
    }
    // we use all numbers from 1 to brokeBarrier if curr is exactly half
    if (curr == half) {
        cout << brokeBarrier << endl;
        for (int x = 1; x <= brokeBarrier; x++) {
            cout << x << " ";
        }
        cout << endl;
        cout << n - brokeBarrier << endl;
        for (int x = brokeBarrier + 1; x <= n; x++) {
            cout << x << " ";
        }
        return 0;
    }

    // if we overshot, we use 1...brokBarrier, but not the skipped
    int skipped = curr - half;
    cout << brokeBarrier - 1 << endl;
    for (int x = 1; x <= brokeBarrier; x++) {
        if (x == skipped) continue;
        cout << x << " ";
    }
    cout << endl;

    int lastWidth = n - (brokeBarrier - 1);
    cout << lastWidth << endl;
    cout << skipped << " ";
    for (int x = brokeBarrier + 1; x <= n; x++) {
        cout << x << " ";
    }
}