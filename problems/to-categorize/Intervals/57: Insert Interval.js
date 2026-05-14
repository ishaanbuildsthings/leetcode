// https://leetcode.com/problems/insert-interval/description/
// Difficulty: Medium
// tags: intervals, binary search

// Problem
/*
You are given an array of non-overlapping intervals intervals where intervals[i] = [starti, endi] represent the start and the end of the ith interval and intervals is sorted in ascending order by starti. You are also given an interval newInterval = [start, end] that represents the start and end of another interval.

Insert newInterval into intervals such that intervals is still sorted in ascending order by starti and intervals still does not have any overlapping intervals (merge overlapping intervals if necessary).

Return intervals after the insertion.
*/

// Solution, O(n) time and O(n) space
/*
The input given to us is sorted and non-overlapping, which means start times are sorted. We can therefore insert the new interval into where it belongs, as per the start time, then merge things as needed. Consider the intervals: [1, 5], [10, 20], [21, 22], [23, 24], and we need to insert [15, 25]. This has the potential to overlap with every element to its right, as well as the direct left element of it.

The simplest way in terms of code is to locate the insertion point (I used binary search even though overall time is still O(n) ), insert it, then just merge from the beginning. Merging from right before the insertion point might save a little time but introduces more potential errors. To see how merging works, see problem 56, merge interval.
*/

var insert = function (intervals, newInterval) {
  // find the last index where the start time is smaller than our start time, insert the interval, then merge starting from that index

  const [start, end] = newInterval;
  let l = 0;
  let r = intervals.length - 1;
  while (l <= r) {
    // m is the index of the tuple we are checking
    const m = Math.floor((r + l) / 2);
    const [startM, endM] = intervals[m];
    if (startM < start) {
      l = m + 1;
    } else if (startM >= start) {
      r = m - 1;
    }
  }
  /* here, r is the index of the first element that ends before our current interval starts */
  // insert our interval on the right of
  intervals.splice(r + 1, 0, newInterval);

  const result = [intervals[0]]; // seed the first interval

  for (let i = 1; i < intervals.length; i++) {
    // if our previous interval ending overlaps with the new interval start, greedily select the largest ending
    if (result[result.length - 1][1] >= intervals[i][0]) {
      result[result.length - 1][1] = Math.max(
        result[result.length - 1][1],
        intervals[i][1]
      );
    } else {
      result.push(intervals[i]);
    }
  }

  return result;

  // const result = [];
  // let prefix = Number.NEGATIVE_INFINITY;
  // let intervalMerged = false;

  // for (let i = 0; i < intervals.length; i++) {

  //     if (!intervalMerged) {
  //         // maybe merge the interval
  //         if (prefix >= newInterval[0]) {
  //             const start = Math.min(
  //                 newInterval[0],
  //                 result[result.length - 1][0]
  //             );
  //             const end = Math.max(
  //                 newInterval[1],
  //                 result[result.length - 1][1]
  //             );
  //             result[result.length - 1] = [start, end];
  //             prefix = end;
  //             intervalMerged = true;
  //         }
  //         // not time to merge the new interval
  //         else {
  //             result.push(intervals[i]);
  //             prefix = intervals[i][1];
  //         }
  //     } else if (intervalMerged) {
  //         if (prefix >= intervals[i]) {
  //             const start = Math.min(
  //                 intervals[i][0],
  //                 result[result.length - 1][0]
  //             );
  //             const end = Math.max(
  //                 intervals[i][1],
  //                 result[result.length - 1][1]
  //             );
  //             result[result.length - 1] = [start, end];
  //             prefix = end;
  //         }
  //         // not time to merge the new interval
  //         else {
  //             result.push(intervals[i]);
  //             prefix = intervals[i][1];
  //         }
  //     }
  // }
  // return result;
};
