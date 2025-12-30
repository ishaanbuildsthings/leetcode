#include <bits/stdc++.h>
using namespace std;

long long cycle(const vector<int>& one, const vector<int>& two, int type) {
    int n = (int)one.size();
    long long score = 0;

    for (int s = 0; s < n; s++) {
        bool ok = true;
        for (int i = 0; i < n; i++) {
            int idx = i - s;
            if (idx < 0) idx += n;
            if (two[i] <= one[idx]) {
                ok = false;
                break;
            }
        }
        if (ok) score++;
    }

    if (type == 0) return score * n;
    return score;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int T;
    cin >> T;
    while (T--) {
        int n;
        cin >> n;

        vector<int> A(n), B(n), C(n);
        for (int i = 0; i < n; i++) cin >> A[i];
        for (int i = 0; i < n; i++) cin >> B[i];
        for (int i = 0; i < n; i++) cin >> C[i];

        long long top = cycle(A, B, 0);
        long long bot = cycle(B, C, 1);
        cout << top * bot << "\n";
    }
    return 0;
}


// from collections import deque
// T = int(input())
// for _ in range(T):
//     n = int(input())
//     A = list(map(int, input().split()))
//     B = list(map(int, input().split()))
//     C = list(map(int, input().split()))

//     def cycle(one, two, type):
//         # print(f'cycle called')
//         d1 = deque(one)
//         d2 = deque(two)
//         # print(f'{d1=} {d2=}')
//         score = 0
//         # try all starts for A
//         for _ in range(n):
//             if all(d2[i] > d1[i] for i in range(n)):
//                 score += 1
//                 # print(f'all were bigger, adding score 1')
//             d1.appendleft(d1.pop())
//         if type == 0:
//             return score * n
//         if type == 1:
//             return score
            
//     top = cycle(A, B, 0)
//     bot = cycle(B, C, 1)
//     # print(f'{top=} {bot=}')
//     print(top * bot)
