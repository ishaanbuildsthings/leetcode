// https://leetcode.com/problems/merge-intervals/description/
// Difficulty: Medium
// tags: intervals

// Problem
/*
Simplified:
Input: intervals = [[1,3],[2,6],[8,10],[15,18]]
Output: [[1,6],[8,10],[15,18]]
Explanation: Since intervals [1,3] and [2,6] overlap, merge them into [1,6].

Detailed:
Given an array of intervals where intervals[i] = [starti, endi], merge all overlapping intervals, and return an array of the non-overlapping intervals that cover all the intervals in the input.
*/

// Solution, O(n log n) time and O(sort) space.
/*
First, sort the given intervals by starting time. We need to start with the earliest interval, then if other intervals start before that interval ends, merge them.

Iterate through the intervals, if the new interval we see starts before our last interval ends, update our last interval ending time. For instance [1, 5] and we get [2, 6], we update to [1, 6]. Or [1, 5] and we get [2, 3], we still update to [1, 5]. If there is no intersection, we just add the new interval. We could copy the intervals too if needed.
*/

var merge = function (intervals) {
  intervals.sort((a, b) => a[0] - b[0]);
  const result = [intervals[0]]; // start with the first interval, unique array so we don't modify input data

  for (let i = 1; i < intervals.length; i++) {
    const currentEnding = result[result.length - 1][1];
    const newElementStart = intervals[i][0];
    if (newElementStart <= currentEnding) {
      result[result.length - 1][1] = Math.max(intervals[i][1], currentEnding);
    } else {
      result.push(intervals[i]);
    }
  }

  return result;
};
