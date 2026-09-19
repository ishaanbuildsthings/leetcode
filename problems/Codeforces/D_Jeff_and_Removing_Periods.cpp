#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int m;
    cin >> m;
    vector<int> arr(m);
    for (int i = 0; i < m; ++i) {
        cin >> arr[i];
    }

    int q;
    cin >> q;
    vector<pair<int,int>> queries; // HOLDS 0-INDEX
    for (int i = 0; i < q; ++i) {
        int l, r;
        cin >> l >> r;
        queries.emplace_back(l - 1, r - 1);
    }
    vector<pair<int,int>> origQueries; // HOLDS 1-INDEX
    origQueries.reserve(q);
    for (auto &qr : queries) {
        origQueries.emplace_back(qr.first + 1, qr.second + 1);
    }

    double BLOCK = sqrt((double)queries.size());
    if (BLOCK < 1.0) BLOCK = 1.0;
    sort(queries.begin(), queries.end(), [&](const pair<int,int> &a, const pair<int,int> &b) {
        long long blockA = floor(a.first / BLOCK);
        long long blockB = floor(b.first / BLOCK);
        if (blockA != blockB) return blockA < blockB;
        return a.second < b.second;
    });
    // print(f'{queries=}')

    map<pair<int,int>, int> zeroIndexQueryAnswers; // maps (ql, qr) -> answer
    int l = 0;
    int r = -1;
    unordered_map<int, deque<int>> numTypeToDequeOfIndices;
    unordered_map<int, unordered_map<int,int>> numTypeToAdjDiffs; // num 5 can have a diff of 3 occuring twice, a diff of 4 occuring once
    int totalArithmetic = 0;
    // print(f'{arr=}')

    for (auto &qrPair : queries) {
        int ql = qrPair.first;
        int qr = qrPair.second;
        // print('--------------')
        // print(f'PROCESSING QUERY: {ql}:{qr}')
        while (r < qr) {
            r++;
            int num = arr[r];
            auto &dq = numTypeToDequeOfIndices[num];
            dq.push_back(r);
            if (dq.size() > 1) {
                int newDiff = dq.back() - dq[dq.size() - 2];
                auto &cntMap = numTypeToAdjDiffs[num];
                cntMap[newDiff]++;
                // if we just got a brand new diff and its our second diff type, we lost arithmetic
                if (cntMap.size() == 2 && cntMap[newDiff] == 1) {
                    totalArithmetic--;
                }
            }
            // if we just got our first ever index, we gain arithmetic
            if (dq.size() == 1) {
                totalArithmetic++;
            }
        }
        while (l > ql) {
            l--;
            int num = arr[l];
            auto &dq = numTypeToDequeOfIndices[num];
            dq.push_front(l);
            if (dq.size() > 1) {
                int newDiff = dq[1] - dq[0];
                auto &cntMap = numTypeToAdjDiffs[num];
                cntMap[newDiff]++;
                // if we just got a brand new diff and its our second diff type, we lost arithmetic
                if (cntMap.size() == 2 && cntMap[newDiff] == 1) {
                    totalArithmetic--;
                }
            }
            // if we just got our first ever index, we gain arithmetic
            if (dq.size() == 1) {
                totalArithmetic++;
            }
        }
        while (r > qr) {
            int num = arr[r];
            int lostDiff;
            auto &dq = numTypeToDequeOfIndices[num];
            if (dq.size() > 1) {
                lostDiff = dq.back() - dq[dq.size() - 2];
            } else {
                lostDiff = INT_MIN;
            }
            dq.pop_back();
            // if we just lost our final number, we lose an arithmetic
            if (dq.empty()) {
                totalArithmetic--;
                numTypeToDequeOfIndices.erase(num);
            }
            if (lostDiff != INT_MIN) {
                auto &cntMap = numTypeToAdjDiffs[num];
                cntMap[lostDiff]--;
                if (cntMap[lostDiff] == 0) {
                    cntMap.erase(lostDiff);
                    // if we lost a diff that made us only have one diff type, we gain an arithmetic
                    if (cntMap.size() == 1) {
                        totalArithmetic++;
                    }
                }
            }
            r--;
        }
        while (l < ql) {
            int num = arr[l];
            int lostDiff;
            auto &dq = numTypeToDequeOfIndices[num];
            if (dq.size() > 1) {
                lostDiff = dq[1] - dq[0];
            } else {
                lostDiff = INT_MIN;
            }
            dq.pop_front();
            // if we just lost our final number, we lose an arithemtic
            if (dq.empty()) {
                totalArithmetic--;
                numTypeToDequeOfIndices.erase(num);
            }
            if (lostDiff != INT_MIN) {
                auto &cntMap = numTypeToAdjDiffs[num];
                cntMap[lostDiff]--;
                if (cntMap[lostDiff] == 0) {
                    cntMap.erase(lostDiff);
                    // if we lost a diff that made us only have one diff type, we gain an arithmetic
                    if (cntMap.size() == 1) {
                        totalArithmetic++;
                    }
                }
            }
            l++;
        }

        // print(f'end of query, arr range is: {arr[ql:qr+1]}')
        // print(f'{totalArithmetic=}')
        // print(f'{numTypeToAdjDiffs=}')
        // print(f'{numTypeToDequeOfIndices=}')
        int uniqueInRange = numTypeToDequeOfIndices.size();
        // print(f'{uniqueInRange=}')
        int removalsNeeded = uniqueInRange + (totalArithmetic == 0 ? 1 : 0);
        // print(f'{removalsNeeded=}')
        zeroIndexQueryAnswers[{ql, qr}] = removalsNeeded;
    }

    for (auto &oqPair : origQueries) {
        int ql = oqPair.first - 1;
        int qr = oqPair.second - 1;
        // print(f'transformed: {ql}:{qr}')
        cout << zeroIndexQueryAnswers[{ql, qr}] << '\n';
    }

    return 0;
}