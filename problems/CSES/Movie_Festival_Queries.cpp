// Python top down jump tables (TLE)
// import bisect
// from functools import lru_cache
// n, q = map(int, input().split())

// movies = []
// for _ in range(n):
//     a, b = map(int, input().split())
//     movies.append([a, b])
// movies.sort()

// queries = []
// for _ in range(q):
//     a, b = map(int, input().split())
//     queries.append([a, b])


// movieIndexSuffixEndingMinimum = [float('inf')] * n
// mn = float('inf')
// for i in range(len(movies) - 1, -1, -1):
//     mn = min(mn, movies[i][1])
//     movieIndexSuffixEndingMinimum[i] = mn
// # for a given arrival time in our query, we need to find the smallest movie ending time, where the start is >= our arrival
// # we can do this online by sorting the movies by start time, binary searching for the earliest movie with a start >= arrival, and taking suffix min

// # print(f'{movies=}')

// MAX_T = 10**6
// LOG = MAX_T.bit_length() + 1
// # nextTime[arriveTime] is the earliest movie end time, with a movie start >= arriveTime
// nextTime = [MAX_T + 1] * (MAX_T + 1)
// for t in range(MAX_T + 1):
//     leftmostMovieIndex = bisect.bisect_left(movies, [t, -1])
//     timeOnRight = movieIndexSuffixEndingMinimum[leftmostMovieIndex] if leftmostMovieIndex < len(movieIndexSuffixEndingMinimum) else MAX_T + 1
//     nextTime[t] = timeOnRight

// # print(f'{nextTime=}')

// @lru_cache(maxsize=None)
// def up(time, power):
//     if time == MAX_T + 1:
//         return MAX_T + 1
//     if power == 0:
//         return nextTime[time]
//     mid = up(time, power - 1)
//     final = up(mid, power - 1)
//     return final

// # 0 1 2 3 4 5 6 7 8 9 10
// #     -------
// #             ----------
// #         -------
// #                   ----
// pow2 = [1]
// for power in range(1, LOG + 1):
//     pow2.append(pow2[-1] * 2)
// # print('======= PROCESSING QUERIES ======')
// for l, r in queries:
//     # print(f'{l=} {r=}')
//     watched = 0
//     curr = l
//     for power in range(LOG, -1, -1):
//         # print(f'trying power={power}')
//         jump = up(curr, power)
//         # print(f'jump time is: {jump}')
//         if jump > r:
//             continue
//         else:
//             curr = jump
//             watched += pow2[power]
//     print(watched)


#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, q;
    cin >> n >> q;

    vector<pair<int,int>> movies;
    movies.reserve(n);
    for (int i = 0; i < n; i++) {
        int a, b;
        cin >> a >> b;
        movies.push_back({a, b});
    }
    sort(movies.begin(), movies.end());

    vector<pair<int,int>> queries;
    queries.reserve(q);
    for (int i = 0; i < q; i++) {
        int a, b;
        cin >> a >> b;
        queries.push_back({a, b});
    }

    vector<int> movieIndexSuffixEndingMinimum(n, INT_MAX);
    int mn = INT_MAX;
    for (int i = (int)movies.size() - 1; i >= 0; i--) {
        mn = min(mn, movies[i].second);
        movieIndexSuffixEndingMinimum[i] = mn;
    }
    // for a given arrival time in our query, we need to find the smallest movie ending time, where the start is >= our arrival
    // we can do this online by sorting the movies by start time, binary searching for the earliest movie with a start >= arrival, and taking suffix min

    const int MAX_T = 1000000;
    const int LOG = (int)bit_width((unsigned)MAX_T) + 1;

    // nextTime[arriveTime] is the earliest movie end time, with a movie start >= arriveTime
    vector<int> nextTime(MAX_T + 1, MAX_T + 1);
    for (int t = 0; t <= MAX_T; t++) {
        int leftmostMovieIndex = (int)(lower_bound(movies.begin(), movies.end(), make_pair(t, -1)) - movies.begin());
        int timeOnRight = (leftmostMovieIndex < (int)movieIndexSuffixEndingMinimum.size()) ? movieIndexSuffixEndingMinimum[leftmostMovieIndex] : (MAX_T + 1);
        nextTime[t] = timeOnRight;
    }

    vector<vector<int>> upCache(MAX_T + 2, vector<int>(LOG + 1, -1));

    function<int(int,int)> up = [&](int time, int power) -> int {
        if (time == MAX_T + 1) return MAX_T + 1;
        int &cached = upCache[time][power];
        if (cached != -1) return cached;
        if (power == 0) return cached = nextTime[time];
        int mid = up(time, power - 1);
        int final = up(mid, power - 1);
        return cached = final;
    };

    vector<long long> pow2;
    pow2.reserve(LOG + 2);
    pow2.push_back(1);
    for (int power = 1; power <= LOG + 1; power++) {
        pow2.push_back(pow2.back() * 2);
    }

    for (auto qr : queries) {
        int l = qr.first, r = qr.second;
        long long watched = 0;
        int curr = l;
        for (int power = LOG; power >= 0; power--) {
            int jump = up(curr, power);
            if (jump > r) {
                continue;
            } else {
                curr = jump;
                watched += pow2[power];
            }
        }
        cout << watched << "\n";
    }

    return 0;
}
