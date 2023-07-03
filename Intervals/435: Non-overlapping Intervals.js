// https://leetcode.com/problems/non-overlapping-intervals/description/
// Difficulty: Medium
// tags: intervals

// Solution
// O(nlogn) time and O(sort) space
/*
Sort by starting time.
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
