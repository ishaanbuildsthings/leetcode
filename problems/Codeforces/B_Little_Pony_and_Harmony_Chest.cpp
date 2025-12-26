// Bottom up C++
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    cin >> n;
    vector<int> A(n);
    for (int i = 0; i < n; i++) cin >> A[i];

    auto uniquePrimeFactorsUpTo60 = [&]() {
        vector<vector<int>> res;
        for (int x = 2; x <= 60; x++) {
            int n = x;
            vector<int> factors;
            int p = 2;
            while (p * p <= n) {
                if (n % p == 0) {
                    factors.push_back(p);
                    while (n % p == 0) {
                        n /= p;
                    }
                }
                p += 1;
            }
            if (n > 1) {
                factors.push_back(n);
            }
            res.push_back(factors);
        }
        return res;
    };

    vector<vector<int>> pf;
    pf.push_back({});
    pf.push_back({});
    {
        auto tmp = uniquePrimeFactorsUpTo60();
        for (auto &v : tmp) pf.push_back(v);
    }

    vector<int> allPrimesUnder60 = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59};
    unordered_map<int, int> primeToIdx;
    primeToIdx.reserve(allPrimesUnder60.size() * 2);
    for (int i = 0; i < (int)allPrimesUnder60.size(); i++) {
        primeToIdx[allPrimesUnder60[i]] = i;
    }

    int fmask = (1 << (int)allPrimesUnder60.size()) - 1;

    vector<int> numberToPrimeMask(61, 0);
    for (int number = 0; number <= 60; number++) {
        auto &uniquePf = pf[number];
        int mask = 0;
        for (int item : uniquePf) {
            int idx = primeToIdx[item];
            mask += 1 << idx;
        }
        numberToPrimeMask[number] = mask;
    }

    const int INF = 1000000000;
    vector<int> dp(fmask + 1, INF);
    dp[0] = 0;

    vector<vector<int>> prevMask(n, vector<int>(fmask + 1, -1));
    vector<vector<int>> prevChoice(n, vector<int>(fmask + 1, -1));

    for (int i = 0; i < n; i++) {
        int num = A[i];
        vector<int> ndp(fmask + 1, INF);

        int distFromOne = num - 1;
        int maxTakeable = num + distFromOne; // no point taking a bigger number, we can just take 1 and not use extra prime factors

        for (int alreadyTakenPrimes = 0; alreadyTakenPrimes <= fmask; alreadyTakenPrimes++) {
            for (int newNum = 1; newNum <= maxTakeable; newNum++) {
                int newPrimeMask = numberToPrimeMask[newNum];
                if (newPrimeMask & alreadyTakenPrimes) {
                    continue;
                }
                int newMask = alreadyTakenPrimes | newPrimeMask;
                int proposedVal = dp[alreadyTakenPrimes] + abs(num - newNum);
                if (dp[alreadyTakenPrimes] + abs(num - newNum) < ndp[newMask]) {
                    ndp[newMask] = dp[alreadyTakenPrimes] + abs(num - newNum);
                    prevMask[i][newMask] = alreadyTakenPrimes;
                    prevChoice[i][newMask] = newNum;
                }
            }
        }
        dp = std::move(ndp);
    }

    vector<int> resArr(n, -1);
    int bestEndingMask = (int)(min_element(dp.begin(), dp.end()) - dp.begin());
    int currMask = bestEndingMask;

    for (int i = n - 1; i >= 0; i--) {
        resArr[i] = prevChoice[i][currMask];
        currMask = prevMask[i][currMask];
    }

    for (int i = 0; i < n; i++) {
        if (i) cout << ' ';
        cout << resArr[i];
    }
    cout << "\n";
    return 0;
}








// Bottom up Python TLE
// import functools
// n = int(input())
// A = list(map(int, input().split()))

// def uniquePrimeFactorsUpTo60():
//     res = []
//     for x in range(2, 61):
//         n = x
//         factors = []
//         p = 2
//         while p * p <= n:
//             if n % p == 0:
//                 factors.append(p)
//                 while n % p == 0:
//                     n //= p
//             p += 1
//         if n > 1:
//             factors.append(n)
//         res.append(factors)
//     return res
// pf = [[], []] + uniquePrimeFactorsUpTo60()
// allPrimesUnder60 = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59]
// primeToIdx = {prime : i for i, prime in enumerate(allPrimesUnder60)}
// fmask = (1 << len(allPrimesUnder60)) - 1

// numberToPrimeMask = [None] * 61
// for number in range(61):
//     uniquePf = pf[number]
//     mask = 0
//     for item in uniquePf:
//         idx = primeToIdx[item]
//         mask += 1 << idx
//     numberToPrimeMask[number] = mask

// INF = 10**9
// dp = [INF] * (fmask + 1) # dp[mask] tells us the minimum score we can get having taken those prime factors in odd remainders, after processing `i` elements as we scan 
// dp[0] = 0
// prevMask = [[-1] * (fmask + 1) for _ in range(n)]
// prevChoice = [[-1] * (fmask + 1) for _ in range(n)]

// for i, num in enumerate(A):
//     ndp = [INF] * (fmask + 1)
//     distFromOne = num - 1
//     maxTakeable = num + distFromOne # no point taking a bigger number, we can just take 1 and not use extra prime factors
//     for alreadyTakenPrimes in range(fmask + 1):
//         for newNum in range(1, maxTakeable + 1):
//             newPrimeMask = numberToPrimeMask[newNum]
//             if newPrimeMask & alreadyTakenPrimes:
//                 continue
//             newMask = alreadyTakenPrimes | newPrimeMask
//             proposedVal = dp[alreadyTakenPrimes] + abs(num - newNum)
//             if dp[alreadyTakenPrimes] + abs(num - newNum) < ndp[newMask]:
//                 ndp[newMask] = dp[alreadyTakenPrimes] + abs(num - newNum)
//                 prevMask[i][newMask] = alreadyTakenPrimes
//                 prevChoice[i][newMask] = newNum
//     dp = ndp

// resArr = [None] * n
// bestEndingMask = dp.index(min(dp))
// currMask = bestEndingMask
// for i in range(n - 1, -1, -1):
//     resArr[i] = prevChoice[i][currMask]
//     currMask = prevMask[i][currMask]
// print(*resArr)






// Top down Python TLE
// # choice = {} # maps (i, primeMask) -> the number we chose
// # @functools.lru_cache(maxsize=None)
// # def dp(i, primeMask):
// #     if i == n:
// #         return 0
// #     diff = A[i] - 1
// #     maxTakeable = A[i] + diff # We would never use a number over this because we can just use 1 which has smaller distance and does not affect the prime mask
// #     resHere = dp(i + 1, primeMask) + (abs(A[i] - 1)) # we can always take a 1
// #     choice[(i, primeMask)] = 1
// #     for taken in range(2, maxTakeable + 1):
// #         primeFactors = pf[taken]
// #         mustSkip = False
// #         newMask = primeMask
// #         for fac in primeFactors:
// #             idx = primeToIdx[fac]
// #             if primeMask & (1 << idx):
// #                 mustSkip = True
// #                 break
// #             newMask |= (1 << idx)
// #         if mustSkip:
// #             continue
// #         ifTakeThisNumber = dp(i + 1, newMask) + abs(A[i] - taken)
// #         if ifTakeThisNumber < resHere:
// #             resHere = ifTakeThisNumber
// #             choice[(i, primeMask)] = taken
// #     return resHere

// # dp(0, 0)
// # resArr = []
// # currI = 0
// # currMask = 0
// # while currI < n:
// #     pickedNumber = choice[(currI, currMask)]
// #     resArr.append(pickedNumber)
// #     currI += 1
// #     facs = pf[pickedNumber]
// #     for fac in facs:
// #         idx = primeToIdx[fac]
// #         currMask |= (1 << idx)
// # print(*resArr)
        




