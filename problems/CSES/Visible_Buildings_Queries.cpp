#include <bits/stdc++.h>
using namespace std;

int MAX_HEIGHT = 1000000000;

int main() {
    cin.tie(nullptr);
    ios::sync_with_stdio(false);
    int n, q; cin >> n >> q;
    vector<int> A(n);
    for (int i = 0; i < n; i++) cin >> A[i];
    A.push_back(MAX_HEIGHT + 1); // we are going to find the next greater element for every element, or N if there is none
    vector<int> stack; // holds indices, mono-decreasing
    vector<int> nextGreater(n);
    for (int i = 0; i < A.size(); i++) {
        while (stack.size() && A[i] > A[stack.back()]) {
            int popped = stack.back(); stack.pop_back();
            nextGreater[popped] = i;
        }
        stack.push_back(i);
    }
    
    // lift[power][index] is going to point to the first index on the right greater than, or if it is lift[power][sentinel] it will point to itself, to make jump queries easy
    int BITS = 32;
    vector<vector<int>> jump(BITS, vector<int>(n + 1));
    for (int i = 0; i < n; i++) {
        jump[0][i] = nextGreater[i];
    }
    jump[0][n] = n;

    for (int power = 1; power < BITS; power++) {
        for (int i = 0; i < A.size(); i++) {
            int mid = jump[power - 1][i];
            int second = jump[power - 1][mid];
            jump[power][i] = second;
        }
    }

    for (int i = 0; i < q; i++) {
        int a, b; cin >> a >> b;
        a--; b--;
        int jumpsMade = 0;
        int curr = a;
        for (int power = BITS - 1; power >= 0; power--) {
            int thatFar = jump[power][curr];
            if (thatFar <= b) {
                jumpsMade += pow(2, power);
                curr = thatFar;
            }
        }
        cout << jumpsMade + 1 << endl;
    }
}
