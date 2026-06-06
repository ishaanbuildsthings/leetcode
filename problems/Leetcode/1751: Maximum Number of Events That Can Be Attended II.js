// https://leetcode.com/problems/maximum-number-of-events-that-can-be-attended-ii/description/
// Difficulty: Hard
// Tags: dynamic programming 2d, binary search, intervals

// Problem
/*
You are given an array of events where events[i] = [startDayi, endDayi, valuei]. The ith event starts at startDayi and ends at endDayi, and if you attend this event, you will receive a value of valuei. You are also given an integer k which represents the maximum number of events you can attend.

You can only attend one event at a time. If you choose to attend an event, you must attend the entire event. Note that the end day is inclusive: that is, you cannot attend two events where one of them starts and the other ends on the same day.

Return the maximum sum of values that you can receive by attending events.
*/

// Solution, O(nk log n) time, O(nk) space
/*
We are given n events, first sort them by starting time.

Then, we have a dp function. If we take the ith event, we can take kRemaining fewer events, starting from a position where the new interval starts after the interval we took ends. We use binary search to find that. There are n*k states, and each state takes O(log n) time to compute, so O(nk log n) time overall. I think the binary search stuff could be preprocessed but didn't bother.
*/

var maxValue = function (events, k) {
  events.sort((a, b) => a[0] - b[0]);

  // find the first event that starts at at least the previous ending time + 1
  function findNextEventStartTime(prevEventEndTime) {
    let l = 0;
    let r = events.length - 1;
    while (l <= r) {
      // m is the index of the event we are looking at
      const m = Math.floor((r + l) / 2);
      const newStartTime = events[m][0];
      if (newStartTime <= prevEventEndTime) {
        l = m + 1;
      } else if (newStartTime > prevEventEndTime) {
        r = m - 1;
      }
    }
    // now l is the index of the first element with a start time bigger than the previous event end time
    return l;
  }

  /*
     memo[start time][k remaining] gives the answer to the subproblem of having events left only at that start time, with k events left to take
     */
  const memo = new Array(events.length)
    .fill()
    .map(() => new Array(k + 1).fill(-1));

  function dp(eventIndex, kRemaining) {
    // if we can't take any more events, we cannot get any more value
    if (kRemaining === 0) {
      return 0;
    }

    // if there are no more events left in the range, we cannot take any more
    if (eventIndex === events.length) {
      return 0;
    }

    if (memo[eventIndex][kRemaining] !== -1) {
      return memo[eventIndex][kRemaining];
    }

    // if we skip this event
    const ifSkip = dp(eventIndex + 1, kRemaining);

    // if we take this event
    const [_, endingTime, value] = events[eventIndex];
    const nextEventIndexIfWeTake = findNextEventStartTime(endingTime);
    const ifTake = value + dp(nextEventIndexIfWeTake, kRemaining - 1);

    const maxForThis = Math.max(ifSkip, ifTake);

    memo[eventIndex][kRemaining] = maxForThis;

    return maxForThis;
  }

  return dp(0, k);
};
