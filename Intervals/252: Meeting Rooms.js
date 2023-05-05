// https://leetcode.com/problems/meeting-rooms/
// Difficulty: Easy
// tags: intervals

// Solution
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
