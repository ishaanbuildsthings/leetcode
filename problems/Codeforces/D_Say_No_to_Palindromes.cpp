#include <bits/stdc++.h>
using namespace std;

string s;
int n;
vector<array<int, 3>> c1, c2;

int suff(int i, int req) {
    if (i == n) return 0;
    int &memo = c1[i][req];
    if (memo != -1) return memo;
    bool doesMatch = (s[i] - 'a') == req;
    memo = (doesMatch ? 1 : 0) + suff(i + 1, (req + 1) % 3);
    return memo;
}

int suffD(int i, int req) {
    if (i == n) return 0;
    int &memo = c2[i][req];
    if (memo != -1) return memo;
    bool doesMatch = (s[i] - 'a') == req;
    memo = (doesMatch ? 1 : 0) + suffD(i + 1, (req + 2) % 3); // (req-1)%3
    return memo;
}

int solveQ(int l, int r) {
    int ans = 0;
    int width = r - l + 1;
    for (int start = 0; start < 3; ++start) {
        int suffUp = suff(l, start);
        int endLetterUp = (width + start) % 3;
        int resUp = suffUp - suff(r + 1, endLetterUp);

        int suffDown = suffD(l, start);
        int shift = width % 3;
        int endLetterDown = (start - shift + 3) % 3;
        int resDown = suffDown - suffD(r + 1, endLetterDown);

        ans = max(ans, max(resUp, resDown));
    }
    return width - ans;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int q;
    cin >> n >> q;
    cin >> s;

    c1.assign(n, { -1, -1, -1 });
    c2.assign(n, { -1, -1, -1 });

    while (q--) {
        int l, r;
        cin >> l >> r;
        --l; --r;
        cout << solveQ(l, r) << '\n';
    }
    return 0;
}