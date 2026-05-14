// https://leetcode.com/problems/meeting-rooms-ii/description/
// Difficulty: Medium
// tags: intervals, heap, two pointers

// Problem
/*
Given an array of meeting time intervals intervals where intervals[i] = [starti, endi], return the minimum number of conference rooms required.
*/

// Solution 1, O(n log n) time, O(n) space. Sort start and end times, maintain pointer.
// * Solution 2, we could use a minheap for the start times and end times, so we easily know when the next meeting that needs a room or frees a room occurs.
// * Solution 3, brute force, we iterate from time 0 to the max time, and check how many meetings are gained or lost at that time. We keep track of the max number of meetings happening at once.
/*
Imagine these are our meetings: [[0, 30],[5, 10],[15, 20]]

We can order start and end times:
start: [0, 5, 15]
end: [10, 20, 30]

We then increment from the first time something notable happens (either we need a room, or free a room), and track the current amount of rooms needed. We use two pointers to maintain where we are in the start and end times.
*/

var minMeetingRooms = function (intervals) {
  const startTimes = intervals
    .map((interval) => interval[0])
    .sort((a, b) => a - b);
  const endTimes = intervals
    .map((interval) => interval[1])
    .sort((a, b) => a - b);

  let startPointer = 0;
  let endPointer = 0;

  let minRooms = 0;
  let currentRooms = 0;

  while (startPointer < startTimes.length) {
    // if a new room is needed before one clears
    if (startTimes[startPointer] < endTimes[endPointer]) {
      currentRooms++;
      startPointer++;
    }

    // if a used room clears before a new one is needed
    else if (endTimes[endPointer] < startTimes[startPointer]) {
      endPointer++;
      currentRooms--;
    }

    // if two rooms open and close at the same time
    else if (startTimes[startPointer] === endTimes[endPointer]) {
      startPointer++;
      endPointer++;
    }

    minRooms = Math.max(minRooms, currentRooms);
  }

  return minRooms;
};
