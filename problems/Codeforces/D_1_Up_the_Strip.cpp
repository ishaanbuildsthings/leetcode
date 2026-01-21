#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m; cin >> n >> m;
    vector<int>dp(n + 1, 0);
    dp[1] = 1;
    int pf = 1;

    for (int x = 2; x <= n; x++) {
        // cout << "sovling for x= " << x << endl;
        long long newWays = pf; // we can definitely add the entire previous set of moves via subtraction
        int divStart = 2;
        // cout << "pf ways was: " << pf << endl;
        while (divStart <= x) {
            // x/currDiv = some number
            // we want to find the largest currDiv such that x/that still = some number
            // like 100/15 = 6
            // but 100/16 also equals 6, so 6 is the largest
            // to find the largest we literally just do 100/6 of course
            // so 15...16 is a block and that block all adds dp[6]
            int nextCell = x / divStart;
            int divEnd = x / nextCell; // TODO: is this safe?
            long long width = divEnd - divStart + 1;
            newWays += (width * dp[nextCell]) % m;
            newWays %= m;
            divStart = divEnd + 1;
            // cout << "for divisor: " << divStart << " we had a width: " << width << endl;
            // cout << "next cell was: " << nextCell << endl;
        }
        pf += newWays;
        pf %= m;
        dp[x] = newWays;
    }
    cout << dp[n] << endl;
}