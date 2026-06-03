#include <bits/stdc++.h>
using namespace std;
using ll = long long;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n; cin >> n;
    vector<int> A(n); for (int i = 0; i < n; i++) cin >> A[i];
    ll res = 0;

    vector<int> smallRight(n, n);
    vector<int> stack;
    for (int i = 0; i < n; i++) {
        while (stack.size() && A[i] < A[stack.back()]) {
            int poppedI = stack.back(); stack.pop_back();
            smallRight[poppedI] = i;
        }
        stack.push_back(i);
    }

    vector<int> smallLeft(n, -1);
    stack.clear();
    for (int i = n - 1; i >= 0; i--) {
        while (stack.size() && A[i] < A[stack.back()]) {
            int poppedI = stack.back(); stack.pop_back();
            smallLeft[poppedI] = i;
        }
        stack.push_back(i);
    }

    for (int i = 0; i < n; i++) {
        int width = (smallRight[i] - 1) - (smallLeft[i] + 1) + 1;
        int height = A[i];
        res = max(res, 1LL * width * height);
    }
    cout << res;
}