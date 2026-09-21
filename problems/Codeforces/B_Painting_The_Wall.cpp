#include <bits/stdc++.h>
using namespace std;

int n;
int numPainted;
const int MAXN = 2000;

double memo[MAXN+1][MAXN+1]; // memo[rowsPainted][colsPainted] tells us the expected # of moves

double dp(int rowsPainted, int colsPainted) {
    // cout << "dp called on " << rowsPainted << " " << colsPainted << "\n";
    if (rowsPainted == n && colsPainted == n) {
        return 0.0;
    }
    if (rowsPainted > n || colsPainted > n) {
        return 0.0;
    }
    if (memo[rowsPainted][colsPainted] != -1.0) {
        return memo[rowsPainted][colsPainted];
    }
    double n2 = 1.0 * n;
    double nsq = n2 * n2;

    int makeNone = rowsPainted * colsPainted; // double covered
    int makeCol = n * rowsPainted - makeNone;
    int makeRow = n * colsPainted - makeNone;
    int makeBoth = (n * n) - (makeNone + makeCol + makeRow);

    double pCol = makeCol / (nsq);
    double pRow = makeRow / (nsq);
    double pBoth = makeBoth / (nsq);
    double pNone = makeNone / (nsq);

    double res =(1
        + pCol * dp(rowsPainted, colsPainted + 1)
        + pRow * dp(rowsPainted + 1, colsPainted)
        + pBoth * dp(rowsPainted + 1, colsPainted + 1)
        ) / (1 - pNone);

    memo[rowsPainted][colsPainted] = res;
    return res;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    cin >> n >> numPainted;

    bool rowCovered[MAXN] = {false};
    bool colCovered[MAXN] = {false};
    int initialRows = 0, initialCols = 0;

    for (int i = 0; i < numPainted; i++) {
        int r, c;
        cin >> r >> c;
        r -= 1;
        c -= 1;
        if (!rowCovered[r]) {
            rowCovered[r] = true;
            initialRows++;
        }
        if (!colCovered[c]) {
            colCovered[c] = true;
            initialCols++;
        }
    }

    for (int i = 0; i < MAXN+1; i++) {
        for (int j = 0; j < MAXN+1; j++) {
            memo[i][j] = -1.0;
        }
    }

    double answer = dp(initialRows, initialCols);
    cout << answer;

    return 0;
}

// dp(rows covered, cols covered)
// we can compute how many squares that we pick wouldn't cover anything, its
// rows*cols
// we can compute how many cells we would pick would just cover a column, those
// are all cells covered by a row, minus those double covered
// same for would just cover a row
// remaining cells would cover both

// the steps we expect to take is the sum of steps we expect to take for each
// substep multipled by the probability to transition into that substep
// except for if we pick a cell that doesn't help us since we recurse forever,
// we can just compute with probability how many steps that would add
 