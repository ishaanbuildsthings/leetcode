import collections
n, reqSum = map(int, input().split())
arr = list(map(int, input().split()))

left = arr[:n//2]
right = arr[n//2:]

def getSumCounts(arr):
    sums = [0]
    for num in arr:
        sums += [x + num for x in sums]
    return collections.Counter(sums)

leftCounts = getSumCounts(left)
rightCounts = getSumCounts(right)

res = 0

for leftAmount in leftCounts:
    requiredRightAmount = reqSum - leftAmount
    res += leftCounts[leftAmount] * rightCounts[requiredRightAmount]

print(res)



# // C++ version, naive enumeration of masks to get sums, TLEs
# // O(n/2 * 2 ^ (n/2))
# // 2^(n/2) to generate all subsets in a half, extra n factor to sum up the size of that mask

# // #include <bits/stdc++.h>
# // using namespace std;

# // unordered_map<long long, long long> getSumCounts(const vector<long long>& a) {
# //     unordered_map<long long, long long> cnt;
# //     int m = (int)a.size();
# //     int fmask = (1 << m) - 1;

# //     for (int mask = 0; mask <= fmask; mask++) {
# //         long long tot = 0;
# //         for (int i = 0; i < m; i++) {
# //             if (mask & (1 << i)) tot += a[i];
# //         }
# //         cnt[tot]++;
# //     }
# //     return cnt;
# // }

# // int main() {
# //     ios::sync_with_stdio(false);
# //     cin.tie(nullptr);

# //     int n;
# //     long long reqSum;
# //     cin >> n >> reqSum;

# //     vector<long long> arr(n);
# //     for (int i = 0; i < n; i++) cin >> arr[i];

# //     vector<long long> left(arr.begin(), arr.begin() + n / 2);
# //     vector<long long> right(arr.begin() + n / 2, arr.end());

# //     auto leftCounts = getSumCounts(left);
# //     auto rightCounts = getSumCounts(right);

# //     long long res = 0;
# //     for (auto &p : leftCounts) {
# //         long long leftAmount = p.first;
# //         long long leftWays = p.second;
# //         long long need = reqSum - leftAmount;

# //         auto it = rightCounts.find(need);
# //         if (it != rightCounts.end()) res += leftWays * it->second;
# //     }

# //     cout << res << "\n";
# //     return 0;
# // }


# // Naive Python version O(n/2 * 2^(n/2)), naively enumerates on subsets to get sums

# // import collections
# // n, reqSum = map(int, input().split())
# // arr = list(map(int, input().split()))

# // left = arr[:n//2]
# // right = arr[n//2:]

# // def getSumCounts(arr):
# //     sumCounts = collections.Counter()
# //     fmask = (1 << len(arr)) - 1
# //     for mask in range(fmask + 1):
# //         tot = 0
# //         for i in range(len(arr)):
# //             if mask & (1 << i):
# //                 tot += arr[i]
# //         sumCounts[tot] += 1
# //     return sumCounts

# // leftCounts = getSumCounts(left)
# // rightCounts = getSumCounts(right)

# // res = 0

# // for leftAmount in leftCounts:
# //     requiredRightAmount = reqSum - leftAmount
# //     res += leftCounts[leftAmount] * rightCounts[requiredRightAmount]

# // print(res)
