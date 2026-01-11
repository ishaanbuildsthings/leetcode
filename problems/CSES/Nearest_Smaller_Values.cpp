#include <bits/stdc++.h>
using namespace std;

int main() {
    cin.tie(nullptr);
    ios::sync_with_stdio(false);
    int n; cin >> n;
    vector<int> A(n);
    for (int i = 0; i < n; i++) cin >> A[i];

    // scan right to left, maintain a mono-increasing stack
    vector<int> stack;
    vector<int> res(n, -1);
    for (int i = n - 1; i >= 0; i--) {
        int num = A[i];
        while (stack.size() && num < A[stack.back()]) {
            int poppedI = stack.back();
            stack.pop_back();
            res[poppedI] = i;
        }
        stack.push_back(i);
    }
    for (auto v : res) {
        int out = v == -1 ? 0 : v + 1;
        cout << out << " ";
    }
}