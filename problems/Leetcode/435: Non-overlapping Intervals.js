// https://leetcode.com/problems/non-overlapping-intervals/description/
// Difficulty: Medium
// tags: intervals

// Problem: Given an array of intervals intervals where intervals[i] = [starti, endi], return the minimum number of intervals you need to remove to make the rest of the intervals non-overlapping.

// Solution
// O(nlogn) time and O(sort) space
/*
Sort by starting time. Iterate through the intervals. The first interval we see is the earliest (or tied for). Once we reach another interval that overlaps, clearly we should be greedy and remove the one that ends later, since it has more potential to overlap with other intervals.
*/

var eraseOverlapIntervals = function (intervals) {
  // sort intervals by starting time, then iterate from the left, greedily removing the one that ends last.
  const intervalsSorted = intervals.sort((a, b) => a[0] - b[0]);

  // iterate through intervals, if our intervals overlaps with the next interval, remove the one that ends later
  let result = 0;
  let prevEndingTime = -Infinity;
  for (let i = 0; i < intervalsSorted.length; i++) {
    const startTime = intervalsSorted[i][0];
    const endTime = intervalsSorted[i][1];
    if (startTime < prevEndingTime) {
      prevEndingTime = Math.min(prevEndingTime, endTime);
      result++;
    } else {
      prevEndingTime = endTime;
    }
  }

  return result;
  /*
    <------------------------>
      <-> <-> <-> <-> <->
    */
};
