#include <bits/stdc++.h>
using namespace std;

int basePower, numAvengers;
long long emptyCost, occupiedMultiplier;
vector<int> avengerPositions;

int findHowManyAvengersAreInRange(int l, int r) {
    auto leftIdx = lower_bound(avengerPositions.begin(), avengerPositions.end(), l) - avengerPositions.begin();
    auto rightIdx = upper_bound(avengerPositions.begin(), avengerPositions.end(), r) - avengerPositions.begin();
    return rightIdx - leftIdx;
}

long long subcost(int l, int r) {
    // print(f'{l=} {r=}')
    if (l > r) return 0;
    int numInRange = findHowManyAvengersAreInRange(l, r);
    long long costToTakeOutWhenOccupied = numInRange > 0
        ? (long long)numInRange * (r - l + 1) * occupiedMultiplier
        : LLONG_MAX;
    long long costToTakeOutWhenEmpty = numInRange == 0
        ? emptyCost
        : LLONG_MAX;
    if (numInRange == 0) return costToTakeOutWhenEmpty;
    if (l == r) return min(costToTakeOutWhenOccupied, costToTakeOutWhenEmpty);
    int halfWidth = (r - l + 1) / 2;
    int ll = l;
    int lr = ll + halfWidth - 1;
    int rl = lr + 1;
    int rr = r;
    // print(f'{ll=} {lr=} {rl=} {rr=}')
    long long minLeftCost  = subcost(ll, lr);
    long long minRightCost = subcost(rl, rr);
    return min({
        minLeftCost + minRightCost,
        costToTakeOutWhenOccupied,
        costToTakeOutWhenEmpty
    });
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    cin >> basePower >> numAvengers >> emptyCost >> occupiedMultiplier;
    avengerPositions.resize(numAvengers);
    for (int i = 0; i < numAvengers; ++i) {
        cin >> avengerPositions[i];
    }
    sort(avengerPositions.begin(), avengerPositions.end());
    int baseLength = 1 << basePower;
    long long result = subcost(1, baseLength);
    cout << result << "\n";
    return 0;
}