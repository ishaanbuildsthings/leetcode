// https://leetcode.com/problems/minimum-speed-to-arrive-on-time/description/
// difficulty: Medium
// tags: binary search

// Problem
/*
You are given a floating-point number hour, representing the amount of time you have to reach the office. To commute to the office, you must take n trains in sequential order. You are also given an integer array dist of length n, where dist[i] describes the distance (in kilometers) of the ith train ride.

Each train can only depart at an integer hour, so you may need to wait in between each train ride.

For example, if the 1st train ride takes 1.5 hours, you must wait for an additional 0.5 hours before you can depart on the 2nd train ride at the 2 hour mark.
Return the minimum positive integer speed (in kilometers per hour) that all the trains must travel at for you to reach the office on time, or -1 if it is impossible to be on time.

Tests are generated such that the answer will not exceed 107 and hour will have at most two digits after the decimal point.
*/

// Solution, O(n log n) time, O(1) space
/*
Binary search- try a speed, and see if we can arrive on time. Note the last train doesn't round up to a ceiling hour, since we get to the office as soon as the train stops. We have to handle the edge case where even if we had infinite speed on the last train, we couldn't finish in time, due to the number of trains to take.
*/

var minSpeedOnTime = function (dist, hour) {
  if (dist.length - 1 >= hour) {
    return -1;
  }

  let l = 0;
  let r = 10 ** 7;

  while (l < r) {
    const m = Math.floor((r + l) / 2); // m is the number we try for speed
    let totalTime = 0;
    for (let i = 0; i < dist.length - 1; i++) {
      const timeForThis = Math.ceil(dist[i] / m);
      totalTime += timeForThis;
    }
    // with the last train, we don't wait an extra hour
    const timeForLastTrain = dist[dist.length - 1] / m;
    totalTime += timeForLastTrain;

    // if the total time was too long, we strictly need a faster speed
    if (totalTime > hour) {
      l = m + 1;
    } else {
      r = m;
    }
  }

  return r;
};
