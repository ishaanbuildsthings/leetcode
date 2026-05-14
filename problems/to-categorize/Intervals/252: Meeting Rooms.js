// https://leetcode.com/problems/meeting-rooms/
// Difficulty: Easy
// tags: intervals

// Solution
// * Solution 2, same thing but with better coding practice, redid it once I was better
// O(nlogn) time and O(1) space. Sort the intervals by start time and check if any end time is greater than the next start time.

const canAttendMeetings = function (intervals) {
  intervals.sort((a, b) => a[0] - b[0]);
  for (let i = 0; i < intervals.length - 1; i++) {
    const currentInterval = intervals[i];
    const nextInterval = intervals[i + 1];
    if (currentInterval[1] > nextInterval[0]) {
      return false;
    }
  }
  return true;
};

// Solution 2, same thing but better practice, not mutating input and better naming
var canAttendMeetings2 = function (intervals) {
  const intervalsSortedByStartTime = intervals.sort((a, b) => a[0] - b[0]);
  // iterate over the first n-1 intervals, checking if the next interval starts before the current one ends
  for (let i = 0; i < intervalsSortedByStartTime.length - 1; i++) {
    if (
      intervalsSortedByStartTime[i + 1][0] < intervalsSortedByStartTime[i][1]
    ) {
      return false;
    }
  }
  return true;
};
