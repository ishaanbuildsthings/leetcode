// // Try #1
// // dp(maskI, countPlaced, smallPrimeBitmask)
// Should be ~50 maskI buckets I'm guessing, up to 25 count placed, 2^15 small prime bitmasks
// This issue with this is when we try placing big primes in the outside for loop, before the dp is called
// We now allow countPlaced up to 25 (big primes and other numbers)
// FYI, the C++ bottom up version of this seems to have barely passed https://www.codechef.com/viewsolution/1222791207

// #include <bits/stdc++.h>
// using namespace std;

// using ll = long long;
// using ull = unsigned long long;

// const ll MOD = 1000000007LL;
// const int MAXN = 100000;

// struct custom_hash {
//     static ull splitmix64(ull x) {
//         x += 0x9e3779b97f4a7c15ULL;
//         x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9ULL;
//         x = (x ^ (x >> 27)) * 0x94d049bb133111ebULL;
//         return x ^ (x >> 31);
//     }
//     size_t operator()(ull x) const noexcept {
//         static const ull FIXED_RANDOM = chrono::steady_clock::now().time_since_epoch().count();
//         return (size_t)splitmix64(x + FIXED_RANDOM);
//     }
// };

// ll modPow(ll base, ll exponent) { // O(log exponent)
//     ll result = 1 % MOD;
//     base %= MOD;
//     while (exponent > 0) {
//         if (exponent & 1) result = (result * base) % MOD;
//         base = (base * base) % MOD;
//         exponent >>= 1;
//     }
//     return result;
// }

// vector<ll> fact;
// vector<ll> invFact;

// void initFacts(int maxN = MAXN) { // O(maxN)
//     fact.assign(maxN + 1, 1);
//     for (int i = 1; i <= maxN; i++) fact[i] = (fact[i - 1] * i) % MOD;

//     invFact.assign(maxN + 1, 1);
//     invFact[maxN] = modPow(fact[maxN], MOD - 2);
//     for (int i = maxN; i >= 1; i--) invFact[i - 1] = (invFact[i] * i) % MOD;
// }

// ll nCk(int n, int k) { // O(1)
//     if (k < 0 || k > n) return 0;
//     return fact[n] * invFact[k] % MOD * invFact[n - k] % MOD;
// }

// ll falling(int x, int y) { // O(1), returns x! / (x - y)!
//     if (y < 0 || y > x) return 0;
//     return fact[x] * invFact[x - y] % MOD;
// }

// vector<int> getPrimesUpTo(int limitVal) { // O(limitVal log log limitVal)
//     vector<char> sieve(limitVal + 1, true);
//     if (limitVal >= 0) sieve[0] = false;
//     if (limitVal >= 1) sieve[1] = false;

//     for (int p = 2; 1LL * p * p <= limitVal; p++) {
//         if (!sieve[p]) continue;
//         for (ll multiple = 1LL * p * p; multiple <= limitVal; multiple += p) {
//             sieve[(int)multiple] = false;
//         }
//     }

//     vector<int> primes;
//     for (int i = 2; i <= limitVal; i++) if (sieve[i]) primes.push_back(i);
//     return primes;
// }

// ull packKey(int bucketIndex, int placedCount, int usedSmallPrimesMask) { // O(1)
//     return (ull)usedSmallPrimesMask | ((ull)placedCount << 20) | ((ull)bucketIndex << 40);
// }

// int main() {
//     ios::sync_with_stdio(false);
//     cin.tie(nullptr);

//     initFacts(MAXN);

//     int T;
//     cin >> T;
//     while (T--) {
//         int n, m;
//         cin >> n >> m;

//         vector<int> primesUpToM = getPrimesUpTo(m);

//         int maxNonOnes = min(n, (int)primesUpToM.size());

//         vector<int> smallPrimes;
//         vector<int> bigPrimes;
//         for (int p : primesUpToM) {
//             if (2LL * p <= m) smallPrimes.push_back(p);
//             else bigPrimes.push_back(p);
//         }
//         int bigPrimeCount = (int)bigPrimes.size();

//         vector<char> isBigPrime(m + 1, false);
//         for (int p : bigPrimes) isBigPrime[p] = true;

//         unordered_map<int, int> smallPrimeToBitIndex;
//         smallPrimeToBitIndex.reserve(smallPrimes.size() * 2 + 1);
//         for (int i = 0; i < (int)smallPrimes.size(); i++) {
//             smallPrimeToBitIndex[smallPrimes[i]] = i;
//         }

//         unordered_map<int, int> numberToSmallMaskMemo;
//         numberToSmallMaskMemo.reserve((size_t)m * 2 + 10);

//         auto smallMaskOf = [&](int num) -> int {
//             auto it = numberToSmallMaskMemo.find(num);
//             if (it != numberToSmallMaskMemo.end()) return it->second;

//             int y = num;
//             int mask = 0;

//             for (int p : smallPrimes) {
//                 if (1LL * p * p > y) break;
//                 if (y % p == 0) {
//                     mask |= 1 << smallPrimeToBitIndex[p];
//                     while (y % p == 0) y /= p;
//                 }
//             }
//             if (y > 1 && 2LL * y <= m) mask |= 1 << smallPrimeToBitIndex[y];

//             numberToSmallMaskMemo[num] = mask;
//             return mask;
//         };

//         unordered_map<int, int> maskToBucketSize;
//         maskToBucketSize.reserve((size_t)m * 2 + 10);

//         for (int value = 2; value <= m; value++) {
//             if (isBigPrime[value]) continue;
//             int mask = smallMaskOf(value);
//             maskToBucketSize[mask] += 1;
//         }

//         vector<int> bucketMasks;
//         vector<int> bucketSizes;
//         bucketMasks.reserve(maskToBucketSize.size());
//         bucketSizes.reserve(maskToBucketSize.size());
//         for (auto &kv : maskToBucketSize) {
//             bucketMasks.push_back(kv.first);
//             bucketSizes.push_back(kv.second);
//         }

//         int bucketCount = (int)bucketMasks.size();

//         unordered_map<ull, ll, custom_hash> dpMemo;
//         dpMemo.reserve((size_t)bucketCount * 256 + 4096);

//         auto dp = [&](auto&& self, int bucketIndex, int placedCount, int usedSmallPrimesMask) -> ll {
//             if (placedCount == maxNonOnes) return 1;
//             if (bucketIndex == bucketCount) return 1;

//             ull key = packKey(bucketIndex, placedCount, usedSmallPrimesMask);
//             auto it = dpMemo.find(key);
//             if (it != dpMemo.end()) return it->second;

//             ll res = self(self, bucketIndex + 1, placedCount, usedSmallPrimesMask);

//             int bucketMask = bucketMasks[bucketIndex];
//             if ((usedSmallPrimesMask & bucketMask) == 0) {
//                 ll optionsFromBucket = bucketSizes[bucketIndex] % MOD;
//                 ll availableSlots = (n - placedCount) % MOD;
//                 ll waysPlaceThis = optionsFromBucket * availableSlots % MOD;
//                 ll sub = self(self, bucketIndex + 1, placedCount + 1, usedSmallPrimesMask | bucketMask);
//                 res = (res + waysPlaceThis * sub) % MOD;
//             }

//             dpMemo[key] = res;
//             return res;
//         };

//         ll answer = 0;
//         int maxBigToTake = min(bigPrimeCount, maxNonOnes);

//         for (int bigTaken = 0; bigTaken <= maxBigToTake; bigTaken++) {
//             ll waysChooseBig = nCk(bigPrimeCount, bigTaken);
//             ll waysPlaceBig = falling(n, bigTaken);
//             ll waysBig = waysChooseBig * waysPlaceBig % MOD;

//             ll waysSmall = dp(dp, 0, bigTaken, 0);
//             answer = (answer + waysBig * waysSmall) % MOD;
//         }

//         cout << answer << "\n";
//     }

//     return 0;
// }




// Try 2
// Now we don't loop on taking the big primes outside the DP, instead when we have maskI == len(masks) base case
// We can loop over the amount of big primes we want to take and handle that in our base case
// We can cache this loop too so the dp recurrence stays O(1)
// This makes the states dp(maskI, numPlaced, smallPrimeMask) closer to ~50 * 15 * 2^15
https://www.codechef.com/viewsolution/1222791562
// Also if we don't cache the for loop in the base case, it still runs fast (even faster?) https://www.codechef.com/viewsolution/1222791836
// I don't fully get how that works out, we do more work in the dp function now but only on base cases, also not sure how it became faster

// #include <bits/stdc++.h>
// using namespace std;

// using ll = long long;
// using ull = unsigned long long;

// const ll MOD = 1000000007LL;
// const int MAXN = 100000;

// struct custom_hash {
//     static ull splitmix64(ull x) {
//         x += 0x9e3779b97f4a7c15ULL;
//         x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9ULL;
//         x = (x ^ (x >> 27)) * 0x94d049bb133111ebULL;
//         return x ^ (x >> 31);
//     }
//     size_t operator()(ull x) const noexcept {
//         static const ull FIXED_RANDOM = chrono::steady_clock::now().time_since_epoch().count();
//         return (size_t)splitmix64(x + FIXED_RANDOM);
//     }
// };

// ll modPow(ll base, ll exponent) {
//     ll result = 1 % MOD;
//     base %= MOD;
//     while (exponent > 0) {
//         if (exponent & 1) result = (result * base) % MOD;
//         base = (base * base) % MOD;
//         exponent >>= 1;
//     }
//     return result;
// }

// vector<ll> fact;
// vector<ll> invFact;

// void initFacts(int maxN = MAXN) {
//     fact.assign(maxN + 1, 1);
//     for (int i = 1; i <= maxN; i++) fact[i] = (fact[i - 1] * i) % MOD;

//     invFact.assign(maxN + 1, 1);
//     invFact[maxN] = modPow(fact[maxN], MOD - 2);
//     for (int i = maxN; i >= 1; i--) invFact[i - 1] = (invFact[i] * i) % MOD;
// }

// ll nCk(int n, int k) {
//     if (k < 0 || k > n) return 0;
//     return fact[n] * invFact[k] % MOD * invFact[n - k] % MOD;
// }

// ll falling(int x, int y) {
//     if (y < 0 || y > x) return 0;
//     return fact[x] * invFact[x - y] % MOD;
// }

// vector<int> getPrimesUpTo(int limitVal) {
//     vector<char> sieve(limitVal + 1, true);
//     if (limitVal >= 0) sieve[0] = false;
//     if (limitVal >= 1) sieve[1] = false;

//     for (int p = 2; 1LL * p * p <= limitVal; p++) {
//         if (!sieve[p]) continue;
//         for (ll multiple = 1LL * p * p; multiple <= limitVal; multiple += p) {
//             sieve[(int)multiple] = false;
//         }
//     }

//     vector<int> primes;
//     for (int i = 2; i <= limitVal; i++) if (sieve[i]) primes.push_back(i);
//     return primes;
// }

// ull packKey(int bucketIndex, int placedCount, int usedSmallPrimesMask) {
//     return (ull)usedSmallPrimesMask | ((ull)placedCount << 20) | ((ull)bucketIndex << 40);
// }

// int main() {
//     ios::sync_with_stdio(false);
//     cin.tie(nullptr);

//     initFacts(MAXN);

//     int T;
//     cin >> T;
//     while (T--) {
//         int n, m;
//         cin >> n >> m;

//         vector<int> primesUpToM = getPrimesUpTo(m);
//         int maxNonOnes = min(n, (int)primesUpToM.size());

//         vector<int> smallPrimes;
//         vector<int> bigPrimes;
//         for (int p : primesUpToM) {
//             if (2LL * p <= m) smallPrimes.push_back(p);
//             else bigPrimes.push_back(p);
//         }
//         int bigPrimeCount = (int)bigPrimes.size();

//         vector<char> isBigPrime(m + 1, false);
//         for (int p : bigPrimes) isBigPrime[p] = true;

//         unordered_map<int, int> smallPrimeToBitIndex;
//         smallPrimeToBitIndex.reserve(smallPrimes.size() * 2 + 1);
//         for (int i = 0; i < (int)smallPrimes.size(); i++) {
//             smallPrimeToBitIndex[smallPrimes[i]] = i;
//         }

//         unordered_map<int, int> numberToSmallMaskMemo;
//         numberToSmallMaskMemo.reserve((size_t)m * 2 + 10);

//         auto smallMaskOf = [&](int num) -> int {
//             auto it = numberToSmallMaskMemo.find(num);
//             if (it != numberToSmallMaskMemo.end()) return it->second;

//             int remaining = num;
//             int mask = 0;

//             for (int p : smallPrimes) {
//                 if (1LL * p * p > remaining) break;
//                 if (remaining % p == 0) {
//                     mask |= 1 << smallPrimeToBitIndex[p];
//                     while (remaining % p == 0) remaining /= p;
//                 }
//             }
//             if (remaining > 1 && 2LL * remaining <= m) {
//                 mask |= 1 << smallPrimeToBitIndex[remaining];
//             }

//             numberToSmallMaskMemo[num] = mask;
//             return mask;
//         };

//         unordered_map<int, int> maskToBucketSize;
//         maskToBucketSize.reserve((size_t)m * 2 + 10);

//         for (int value = 2; value <= m; value++) {
//             if (isBigPrime[value]) continue;
//             int mask = smallMaskOf(value);
//             maskToBucketSize[mask] += 1;
//         }

//         vector<int> bucketMasks;
//         vector<int> bucketSizes;
//         bucketMasks.reserve(maskToBucketSize.size());
//         bucketSizes.reserve(maskToBucketSize.size());
//         for (auto &kv : maskToBucketSize) {
//             bucketMasks.push_back(kv.first);
//             bucketSizes.push_back(kv.second);
//         }
//         int bucketCount = (int)bucketMasks.size();

//         unordered_map<ull, ll, custom_hash> dpMemo;
//         dpMemo.reserve((size_t)bucketCount * 256 + 4096);

//         auto dp = [&](auto&& self, int bucketIndex, int placedCount, int usedSmallPrimesMask) -> ll {
//             if (placedCount >= maxNonOnes) return 1;

//             if (bucketIndex == bucketCount) {
//                 int remainingSlots = n - placedCount;
//                 int maxExtraBig = min({bigPrimeCount, maxNonOnes - placedCount, remainingSlots});
//                 ll sumWays = 0;
//                 for (int takeBig = 0; takeBig <= maxExtraBig; takeBig++) {
//                     ll waysChooseBig = nCk(bigPrimeCount, takeBig);
//                     ll waysPlaceBig = falling(remainingSlots, takeBig);
//                     sumWays = (sumWays + waysChooseBig * waysPlaceBig) % MOD;
//                 }
//                 return sumWays;
//             }

//             ull key = packKey(bucketIndex, placedCount, usedSmallPrimesMask);
//             auto it = dpMemo.find(key);
//             if (it != dpMemo.end()) return it->second;

//             ll res = self(self, bucketIndex + 1, placedCount, usedSmallPrimesMask);

//             int bucketMask = bucketMasks[bucketIndex];
//             if ((usedSmallPrimesMask & bucketMask) == 0) {
//                 ll optionsFromBucket = bucketSizes[bucketIndex] % MOD;
//                 ll availableSlots = (n - placedCount) % MOD;
//                 ll waysPlaceThis = optionsFromBucket * availableSlots % MOD;
//                 ll sub = self(self, bucketIndex + 1, placedCount + 1, usedSmallPrimesMask | bucketMask);
//                 res = (res + waysPlaceThis * sub) % MOD;
//             }

//             dpMemo[key] = res;
//             return res;
//         };

//         ll answer = dp(dp, 0, 0, 0);
//         cout << answer << "\n";
//     }

//     return 0;
// }


// Try 3, speeding up from 3s to 0.03s using mask cleansing
// Say we just considered a mask using 13 and 5 as the primes, and we took something with a 13
// And we know all future maskI buckets won't have a 13 prime-bit set
// We could just remove this from oru mask to collide DP states
// We can take a suffix of all future mask buckets ORd together, and AND that with our current mask, to cleanse it
// https://www.codechef.com/viewsolution/1222792505
// #include <bits/stdc++.h>
// using namespace std;

// using ll = long long;
// using ull = unsigned long long;

// const ll MOD = 1000000007LL;
// const int MAXN = 100000;

// struct custom_hash {
//     static ull splitmix64(ull x) {
//         x += 0x9e3779b97f4a7c15ULL;
//         x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9ULL;
//         x = (x ^ (x >> 27)) * 0x94d049bb133111ebULL;
//         return x ^ (x >> 31);
//     }
//     size_t operator()(ull x) const noexcept {
//         static const ull FIXED_RANDOM = chrono::steady_clock::now().time_since_epoch().count();
//         return (size_t)splitmix64(x + FIXED_RANDOM);
//     }
// };

// ll modPow(ll base, ll exponent) {
//     ll result = 1 % MOD;
//     base %= MOD;
//     while (exponent > 0) {
//         if (exponent & 1) result = (result * base) % MOD;
//         base = (base * base) % MOD;
//         exponent >>= 1;
//     }
//     return result;
// }

// vector<ll> fact;
// vector<ll> invFact;

// void initFacts(int maxN = MAXN) {
//     fact.assign(maxN + 1, 1);
//     for (int i = 1; i <= maxN; i++) fact[i] = (fact[i - 1] * i) % MOD;

//     invFact.assign(maxN + 1, 1);
//     invFact[maxN] = modPow(fact[maxN], MOD - 2);
//     for (int i = maxN; i >= 1; i--) invFact[i - 1] = (invFact[i] * i) % MOD;
// }

// ll nCk(int n, int k) {
//     if (k < 0 || k > n) return 0;
//     return fact[n] * invFact[k] % MOD * invFact[n - k] % MOD;
// }

// ll falling(int x, int y) {
//     if (y < 0 || y > x) return 0;
//     return fact[x] * invFact[x - y] % MOD;
// }

// vector<int> getPrimesUpTo(int limitVal) {
//     vector<char> sieve(limitVal + 1, true);
//     if (limitVal >= 0) sieve[0] = false;
//     if (limitVal >= 1) sieve[1] = false;

//     for (int p = 2; 1LL * p * p <= limitVal; p++) {
//         if (!sieve[p]) continue;
//         for (ll multiple = 1LL * p * p; multiple <= limitVal; multiple += p) {
//             sieve[(int)multiple] = false;
//         }
//     }

//     vector<int> primes;
//     for (int i = 2; i <= limitVal; i++) if (sieve[i]) primes.push_back(i);
//     return primes;
// }

// ull packKey(int bucketIndex, int placedCount, int usedSmallPrimesMask) {
//     return (ull)usedSmallPrimesMask | ((ull)placedCount << 20) | ((ull)bucketIndex << 40);
// }

// int main() {
//     ios::sync_with_stdio(false);
//     cin.tie(nullptr);

//     initFacts(MAXN);

//     int T;
//     cin >> T;
//     while (T--) {
//         int n, m;
//         cin >> n >> m;

//         vector<int> primesUpToM = getPrimesUpTo(m);
//         int maxNonOnes = min(n, (int)primesUpToM.size());

//         vector<int> smallPrimes;
//         vector<int> bigPrimes;
//         for (int p : primesUpToM) {
//             if (2LL * p <= m) smallPrimes.push_back(p);
//             else bigPrimes.push_back(p);
//         }
//         int bigPrimeCount = (int)bigPrimes.size();

//         vector<char> isBigPrime(m + 1, false);
//         for (int p : bigPrimes) isBigPrime[p] = true;

//         unordered_map<int, int> smallPrimeToBitIndex;
//         smallPrimeToBitIndex.reserve(smallPrimes.size() * 2 + 1);
//         for (int i = 0; i < (int)smallPrimes.size(); i++) {
//             smallPrimeToBitIndex[smallPrimes[i]] = i;
//         }

//         unordered_map<int, int> numberToSmallMaskMemo;
//         numberToSmallMaskMemo.reserve((size_t)m * 2 + 10);

//         auto smallMaskOf = [&](int num) -> int {
//             auto it = numberToSmallMaskMemo.find(num);
//             if (it != numberToSmallMaskMemo.end()) return it->second;

//             int remaining = num;
//             int mask = 0;

//             for (int p : smallPrimes) {
//                 if (1LL * p * p > remaining) break;
//                 if (remaining % p == 0) {
//                     mask |= 1 << smallPrimeToBitIndex[p];
//                     while (remaining % p == 0) remaining /= p;
//                 }
//             }
//             if (remaining > 1 && 2LL * remaining <= m) {
//                 mask |= 1 << smallPrimeToBitIndex[remaining];
//             }

//             numberToSmallMaskMemo[num] = mask;
//             return mask;
//         };

//         unordered_map<int, int> maskToBucketSize;
//         maskToBucketSize.reserve((size_t)m * 2 + 10);

//         for (int value = 2; value <= m; value++) {
//             if (isBigPrime[value]) continue;
//             int mask = smallMaskOf(value);
//             maskToBucketSize[mask] += 1;
//         }

//         vector<int> bucketMasks;
//         vector<int> bucketSizes;
//         bucketMasks.reserve(maskToBucketSize.size());
//         bucketSizes.reserve(maskToBucketSize.size());
//         for (auto &kv : maskToBucketSize) {
//             bucketMasks.push_back(kv.first);
//             bucketSizes.push_back(kv.second);
//         }
//         int bucketCount = (int)bucketMasks.size();

//         vector<int> suffixOr(bucketCount + 1, 0);
//         for (int i = bucketCount - 1; i >= 0; i--) {
//             suffixOr[i] = suffixOr[i + 1] | bucketMasks[i];
//         }

//         vector<ll> baseWhenBucketsDone(maxNonOnes + 1, 0);
//         for (int placedCount = 0; placedCount <= maxNonOnes; placedCount++) {
//             int remainingSlots = n - placedCount;
//             int maxExtraBig = min({bigPrimeCount, maxNonOnes - placedCount, remainingSlots});
//             ll sumWays = 0;
//             for (int takeBig = 0; takeBig <= maxExtraBig; takeBig++) {
//                 ll waysChooseBig = nCk(bigPrimeCount, takeBig);
//                 ll waysPlaceBig = falling(remainingSlots, takeBig);
//                 sumWays = (sumWays + waysChooseBig * waysPlaceBig) % MOD;
//             }
//             baseWhenBucketsDone[placedCount] = sumWays;
//         }

//         unordered_map<ull, ll, custom_hash> dpMemo;
//         dpMemo.reserve((size_t)bucketCount * 256 + 4096);

//         auto dp = [&](auto&& self, int bucketIndex, int placedCount, int usedSmallPrimesMask) -> ll {
//             if (placedCount >= maxNonOnes) return 1;

//             usedSmallPrimesMask &= suffixOr[bucketIndex];

//             if (bucketIndex == bucketCount) return baseWhenBucketsDone[placedCount];

//             ull key = packKey(bucketIndex, placedCount, usedSmallPrimesMask);
//             auto it = dpMemo.find(key);
//             if (it != dpMemo.end()) return it->second;

//             ll res = self(self, bucketIndex + 1, placedCount, usedSmallPrimesMask);

//             int bucketMask = bucketMasks[bucketIndex];
//             if ((usedSmallPrimesMask & bucketMask) == 0) {
//                 ll optionsFromBucket = bucketSizes[bucketIndex] % MOD;
//                 ll availableSlots = (n - placedCount) % MOD;
//                 ll waysPlaceThis = optionsFromBucket * availableSlots % MOD;
//                 ll sub = self(self, bucketIndex + 1, placedCount + 1, usedSmallPrimesMask | bucketMask);
//                 res = (res + waysPlaceThis * sub) % MOD;
//             }

//             dpMemo[key] = res;
//             return res;
//         };

//         ll answer = dp(dp, 0, 0, 0);
//         cout << answer << "\n";
//     }

//     return 0;
// }
