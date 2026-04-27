#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, x; cin >> n >> x;
    vector<int> A(n); for (int i = 0; i < n; i++) cin >> A[i];

    // ideas
    // what makes something a factor

    // if the minimum factorial is say 15
    // then the final sum is divisible by all of 1 to 14


    // binary search doesn't work e.g. 2 + 2 + 2 + 2 is divisible by 8 but not 5

    // prime decompose X?

    // get a map of counts of each factorial -> how many times it occurs

    vector<int> cnt(x + 1);
    for (auto v : A) cnt[v]++;
    sort(A.begin(), A.end());
    long long gainBefore = 0;

    // the smallest one bounds us, like if the smallest we are forced to take is 5!, we can form everything <= 5

    for (int num = 1; num <= x; num++) {
        int reqToPromote = num + 1; // if we are at 3!, we need to sum 4 copies to get 4!
        int totalAmount = cnt[num] + gainBefore;
        int newGain = totalAmount / reqToPromote;
        int leftover = totalAmount % reqToPromote;
        if (leftover) {
            int mxCanMake = num;
            cout << (mxCanMake >= x ? "Yes" : "No");
            return 0;
        }
        gainBefore = newGain;
    }
    cout << "Yes";

}