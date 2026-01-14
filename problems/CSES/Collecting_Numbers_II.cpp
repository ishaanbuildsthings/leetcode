#include <bits/stdc++.h>
using namespace std;

int main() {
    cin.tie(nullptr);
    ios::sync_with_stdio(false);
    int n, m; cin >> n >> m;
    vector<int> A(n); for (int i = 0; i < n; i++) cin >> A[i];

    vector<bool> isAfterNext(n + 1, true);
    unordered_map<int,int> numToPos;
    for (int i = 0; i < n; i++) {
        numToPos[A[i]] = i;
    }
    int inversions = 0;
    for (int number = 1; number < n; number++) {
        int nextPos = numToPos[number + 1];
        int currPos = numToPos[number];
        if (currPos > nextPos) {
            isAfterNext[number] = false;
            inversions++;
        }
    }
    for (int i = 0; i < m; i++) {
        int a, b; cin >> a >> b; a--; b--;
        if (a > b) {
            swap(a, b);
        }
        int num1 = A[a];
        int num2 = A[b];
        
        // if num1 was not after its next, but now is, we gain an inversion
        if (num1 < n && numToPos[num1 + 1] > a && numToPos[num1 + 1] < b) {
            inversions++;
        }
        // If num2 was after its next, but now is not, we lose an inversion
        if (num2 < n && numToPos[num2 + 1] < b && numToPos[num2 + 1] > a) {
            inversions--;
        }
        // If num1-1 was after num1, but now is not, we lose an inversion
        if (num1 > 1 && numToPos[num1-1] > a && numToPos[num1-1] < b) {
            inversions--;
        }
        // If num2-1 was before num2, but now is after, we gain an inversion
        if (num2 > 1 && numToPos[num2-1] < b && numToPos[num2-1] > a) {
            inversions++;
        }
        // Handle edge case separate
        if (num2 == num1 + 1) {
            inversions++;
        }
        if (num1 == num2 + 1) {
            inversions--;
        }
        A[a] = num2;
        A[b] = num1;
        numToPos[num1] = b;
        numToPos[num2] = a;
        cout << inversions + 1 << endl;
    }
}