#include <bits/stdc++.h>
using namespace std;

// returns the 1-indexed position of that person removed
int solve(int n, int k) {
    // base case, if there is 1 person to be removed they are the "second" person technically so we remove them
    if (n == 1) {
        return 1;
    }

    // base case, if the person is removed this round
    // 1 2 3 4 5 6 7, k=3
    // removed = 3
    // removed person is 6
    int removeable = n / 2;
    if (k <= removeable) {
        return 2 * k;
    }

    int newPeople = n - removeable;
    int newRemovalQuery = k - removeable;

    // if we have an even amount of people
    // 1 2 3 4 5 6 7 8
    // 1   3   5   7
    // ^
    // 1   2   3   4
    // Every new person * 2 - 1 equals our old label
    if (n % 2 == 0) {
        return solve(newPeople, newRemovalQuery) * 2 - 1;
    }

    // if we have an odd amount of people
    // 1 2 3 4 5 6 7, k=5, we remove 3, new k=2
    // 1   3   5   7
    //             ^ but now this is the start
    // 7   1   3   5

    auto oneIndexResult = solve(newPeople, newRemovalQuery);
    // get the normal 1 3 5 7 indexing
    oneIndexResult -= 1;
    if (oneIndexResult == 0) {
        oneIndexResult = newPeople;
    }

    // Now we have the index in the good sequence 1 3 5 7
    // The index in our initial sequence is therefore 2 * that - 1
    return 2 * oneIndexResult - 1;
};

int main() {
    cin.tie(nullptr);
    ios::sync_with_stdio(false);

    int q; cin >> q;

    for (int i = 0; i < q; i++) {
        int n, k;
        cin >> n >> k;
        cout << solve(n, k) << endl;
    }
}