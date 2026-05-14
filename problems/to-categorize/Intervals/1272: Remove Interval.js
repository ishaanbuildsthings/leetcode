// https://leetcode.com/problems/remove-interval/description/
// difficulty: Medium
// tags: intervals

// Problem
/*
A set of real numbers can be represented as the union of several disjoint intervals, where each interval is in the form [a, b). A real number x is in the set if one of its intervals [a, b) contains x (i.e. a <= x < b).

You are given a sorted list of disjoint intervals intervals representing a set of real numbers as described above, where intervals[i] = [ai, bi] represents the interval [ai, bi). You are also given another interval toBeRemoved.

Return the set of real numbers with the interval toBeRemoved removed from intervals. In other words, return the set of real numbers such that every x in the set is in intervals but not in toBeRemoved. Your answer should be a sorted list of disjoint intervals as described above.
*/

// Solution, O(n) time, O(1) space
/*
The [a, b) thing and the definition of numbers honestly just makes the problem harder to conceptualize. Just look at the image and think about all cases of interval : toBeRmoeved interactions. We are either fully contained, fully contain, fully left, fully right, partially left, or partially right.
*/

var removeInterval = function (intervals, toBeRemoved) {
  const result = [];

  for (const interval of intervals) {
    const [left, right] = interval;

    // if we are fully outside the to be removed
    if (
      (left < toBeRemoved[0] && right <= toBeRemoved[0]) ||
      (left > toBeRemoved[1] && right > toBeRemoved[1])
    ) {
      result.push(interval);
    }

    // if we are fully inside the interval, skip it, in this case the right being equal to the right border is considered inside since we wouldn't add [x, x], honestly the easiest way is to ignore the [a, b) form and just use the image
    else if (left >= toBeRemoved[0] && right <= toBeRemoved[1]) {
      continue;
    }

    // if the left is outside, and the right is inside, truncate
    else if (
      left < toBeRemoved[0] &&
      right > toBeRemoved[0] &&
      right <= toBeRemoved[1]
    ) {
      result.push([left, toBeRemoved[0]]);
    }

    // if the left is inside, and the right is outside, truncate
    else if (
      left >= toBeRemoved[0] &&
      left <= toBeRemoved[1] &&
      right >= toBeRemoved[1]
    ) {
      result.push([toBeRemoved[1], right]);
    }

    // if the left is on the left of to be removed, and the right is on the right of to be removed, add both left and right portions
    else if (left < toBeRemoved[0] && right >= toBeRemoved[1]) {
      result.push([left, toBeRemoved[0]]);
      result.push([toBeRemoved[1], right]);
    }
  }

  return result;
};
