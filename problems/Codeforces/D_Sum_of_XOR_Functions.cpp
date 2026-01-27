// Solution 1, solve bit by bit and use a 4N dp that calculates the sum of lengths of all subarrays with an odd amount of bits, barely ACs in time

// #include <bits/stdc++.h>
// using namespace std;

// struct Key {
//     int i;
//     int parity;
//     int open;
// };

// struct KeyHash {
//     size_t operator()(Key const& k) const noexcept {
//         unsigned long long x = (unsigned long long)(unsigned int)k.i;
//         x = (x << 1) | (unsigned long long)(k.parity & 1);
//         x = (x << 1) | (unsigned long long)(k.open & 1);
//         return std::hash<unsigned long long>{}(x);
//     }
// };

// struct KeyEq {
//     bool operator()(Key const& a, Key const& b) const noexcept {
//         return a.i == b.i && a.parity == b.parity && a.open == b.open;
//     }
// };

// const int MAXN = 300000;

// static pair<long long, long long> memo[MAXN + 1][2][2];

// int main() {
//     ios::sync_with_stdio(false);
//     cin.tie(nullptr);

//     int n; cin >> n; vector<int> A(n); for (int i = 0; i < n; i++) cin >> A[i];
//     long long res = 0;
//     int BITS = 31;
//     long long MOD = 998244353;

//     for (int bit = 0; bit < BITS; bit++) {
//         vector<int> B;
//         B.reserve(n);
//         for (int v : A) {
//             if (v & (1 << bit)) {
//                 B.push_back(1);
//             } else {
//                 B.push_back(0);
//             }
//         }

//     // reset the memo
//     for (int i = 0; i <= n; i++) {
//         memo[i][0][0] = {-1LL, -1LL};
//         memo[i][0][1] = {-1LL, -1LL};
//         memo[i][1][0] = {-1LL, -1LL};
//         memo[i][1][1] = {-1LL, -1LL};
//     }
//     // we need the sum of lengths of all subarrays with an odd amount of 1s
//     // returns sum of lengths for odd amount 1s, # of sequences with odd 1s

//     auto dp = [&](auto&& self, int i, int parity, int open) -> pair<long long, long long> {
//         if (i == n) {
//             return {0LL, 0LL};
//         }
//         auto &cell = memo[i][parity][open];
//         if (cell.first != -1) return cell;

//         long long resSum = 0;
//         long long resNumSequences = 0;

//         // if not open
//         if (!open) {
//             auto [dontOpenSum, dontOpenSequences] = self(self, i + 1, parity, 0);
//             auto [openNowSum, openNowSequences] = self(self, i + 1, B[i], 1);
//             long long openAndCloseSum = B[i];
//             long long openAndCloseSequences = B[i];
//             resSum = (dontOpenSum + openNowSum + openAndCloseSum) % MOD;
//             resSum += openNowSequences;
//             resSum %= MOD;
//             long long resSequences = (dontOpenSequences + openNowSequences + openAndCloseSequences) % MOD;
//             cell = {resSum, resSequences};
//             return cell;
//         }

//         int ifCloseHereNewParity = parity ^ B[i];
//         long long ifCloseHereSum = ifCloseHereNewParity ? 1LL : 0LL;
//         long long ifCloseHereNumSequences = ifCloseHereNewParity ? 1LL : 0LL;
//         auto [ifKeepGoingSum, ifKeepGoingSequences] = self(self, i + 1, parity ^ B[i], 1);
//         resSum = ifCloseHereSum + ifKeepGoingSum;
//         resSum += ifKeepGoingSequences;
//         resSum %= MOD;
//         long long resSeq = (ifCloseHereNumSequences + ifKeepGoingSequences) % MOD;
//         cell = {resSum, resSeq};
//         return cell;
//     };

//         auto [allLengthsSum, numSequences] = dp(dp, 0, 0, 0);

//         res += (((1LL << bit) % MOD) * (allLengthsSum % MOD)) % MOD;
//         res %= MOD;
//     }

//     cout << (res % MOD) << "\n";
//     return 0;
// }


// Solution 2, solve bit by bit using lop off method to calculate sum of lengths of all subarrays with an odd amount of elements
#include <bits/stdc++.h>
using namespace std;
const int MOD = 998244353;
const int LOG = 32;
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n; cin >> n;
    vector<int> A(n); for (int i = 0; i < n; i++) cin >> A[i];
    long long out = 0;
    for (int bit = 0; bit < LOG; bit++) {
        vector<int> B;
        long long sumOfLengthsOddBits = 0;
        for (auto num : A) {
            if (num & (1 << bit)) {
                B.push_back(1);
            } else {
                B.push_back(0);
            }
        }

        int sumEven = 0; // sum of lengths of all subarrays ending at r, when the # of bits is even
        int sumOdd = 0;
        int countEven = 0; // number of subarrays with even amount of bits, ending at r
        int countOdd = 0;
        for (int r = 0; r < n; r++) {
            int number = B[r];

            int nSumEven, nSumOdd, nCountEven, nCountOdd;

            // if we gain a 1, the sum of lengths for all even subarrays ending here is the sum of previous odds + # of previous odds
            if (number == 1) {
                nSumEven = (sumOdd + countOdd) % MOD;
                nSumOdd = (sumEven + countEven + 1) % MOD;
                nCountEven = countOdd;
                nCountOdd = countEven + 1;
            } else {
                nSumEven = (sumEven + countEven + 1) % MOD;
                nSumOdd = (sumOdd + countOdd) % MOD;
                nCountEven = countEven + 1;
                nCountOdd = countOdd;
            }

            sumEven = nSumEven;
            sumOdd = nSumOdd;
            countEven = nCountEven;
            countOdd = nCountOdd;

            sumOfLengthsOddBits += sumOdd;
            sumOfLengthsOddBits %= MOD;
        }
        out += ((1 << bit) * sumOfLengthsOddBits) % MOD;
        out %= MOD;
    }
    cout << out << '\n';
}