#include <bits/stdc++.h>
using namespace std;

int n, k;
vector<pair<long long,long long>> es; // [l, r]

string strNum;
long long memoDigit[20][2][2][2];
char usedDigit[20][2][2][2];

long long dp(int i, int nStarted, int isTight, int didStartWith1) {
    // base case
    if (i == (int)strNum.size()) {
        return (nStarted && didStartWith1) ? 1 : 0;
    }

    // memo
    long long &resHere = memoDigit[i][nStarted][isTight][didStartWith1];
    if (usedDigit[i][nStarted][isTight][didStartWith1]) return resHere;
    usedDigit[i][nStarted][isTight][didStartWith1] = 1;

    resHere = 0;
    int upper = isTight ? (strNum[i] - '0') : 9;

    for (int nxt = 0; nxt <= upper; nxt++) {
        int nnStarted  = nStarted || nxt > 0;
        int newIsTight = isTight && nxt == upper;
        int newDidStart = didStartWith1 || (!nStarted && nxt == 1);
        resHere += dp(i + 1, nnStarted, newIsTight, newDidStart);
    }
    return resHere;
}

long long calcUpTo(long long x) {
    if (x <= 0) return 0;
    strNum = to_string(x);
    memset(usedDigit, 0, sizeof usedDigit);
    return dp(0, 0, 1, 0);
}

long long query(long long low, long long high) {
    return calcUpTo(high) - calcUpTo(low - 1);
}

vector<vector<double>> memo2;
vector<double> chancePick, chanceNotPick; // PRECOMPUTE to make dp2 not double up for a same step

double dp2(int step, int curr) {
    if (step > n) {
        double percentage = 100.0 * curr / n;
        return (percentage >= k) ? 1.0 : 0.0;
    }

    double &res = memo2[step][curr];
    if (res != -1.0) return res;

    double pPick = chancePick[step];
    double pNotPick  = chanceNotPick[step];

    res = pPick * dp2(step + 1, curr + 1) + pNotPick * dp2(step + 1, curr);
    return res;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    cin >> n;
    es.resize(n);
    for (int i = 0; i < n; i++) {
        long long l, r;
        cin >> l >> r;
        es[i] = {l, r};
    }
    cin >> k;

    chancePick.resize(n + 2);
    chanceNotPick.resize(n + 2);

    for (int i = 1; i <= n; i++) {
        long long l = es[i - 1].first, r = es[i - 1].second;

        long long ones = query(l, r);
        double width = (double)(r - l + 1);
        chancePick[i] = ones / width;
        chanceNotPick[i] = 1.0 - chancePick[i];
    }

    memo2.assign(n + 2, vector<double>(n + 2, -1.0));
    cout << fixed << setprecision(15) << dp2(1, 0);
    return 0;
}