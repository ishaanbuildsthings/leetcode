// https://leetcode.com/problems/minimum-number-of-taps-to-open-to-water-a-garden/
// Difficulty: Hard
// tags: intervals

// Problem
/*
There is a one-dimensional garden on the x-axis. The garden starts at the point 0 and ends at the point n. (i.e The length of the garden is n).

There are n + 1 taps located at points [0, 1, ..., n] in the garden.

Given an integer n and an integer array ranges of length n + 1 where ranges[i] (0-indexed) means the i-th tap can water the area [i - ranges[i], i + ranges[i]] if it was open.

Return the minimum number of taps that should be open to water the whole garden, If the garden cannot be watered return -1.
*/

// Solution, O(taps * max tap range) time, O(1) space
/*
Some DP solutions that initally come to mind don't work. Instead, we can think of this as an interval question. Clearly, we need to turn on a tap that covers the ground on the right of index 0. There's multiple taps, we should choose the one that extends the furthest. Then, when we go to the new unwatered index, we need to consider all taps that conver this ground, and choose the one that extends the furthest. Since a taps range is only 100, we only need to consider 201 taps that can cover this ground!
*/

/**
 * @param {number} n
 * @param {number[]} ranges
 * @return {number}
 */
var minTaps = function (n, ranges) {
  /*
    for each index, we need to know the range that goes the furthest right, then we can just greedily select and repeat

    essentially for a given index, we need water to be covered in that region. we can search the prior 100 taps, the current tap, and the future 100 taps, which are the only taps that could cover this region. we check ones that cover the index, and choose to turn on the tap that extends furthest to the right, then jump to the next position, if no taps cover the region we return -1
    */

  let result = 0;
  let pointer = 0; // where we are

  while (pointer < ranges.length - 1) {
    let furthestRight = -Infinity;

    // check prior 100 taps
    for (
      let priorTap = pointer - 1;
      priorTap >= Math.max(0, pointer - 100);
      priorTap--
    ) {
      const range = ranges[priorTap];
      const rightmost = priorTap + range;
      // don't consider previous taps that cannot reach our index
      if (rightmost < pointer) {
        continue;
      }
      furthestRight = Math.max(furthestRight, rightmost);
    }

    // check current tap
    // as per the problem, 0 range taps don't water any ground and are useless
    if (ranges[pointer] !== 0) {
      furthestRight = Math.max(furthestRight, pointer + ranges[pointer]);
    }

    // check the future 100 taps
    for (
      let futureTap = pointer + 1;
      futureTap <= Math.min(ranges.length - 1, pointer + 100);
      futureTap++
    ) {
      const range = ranges[futureTap];
      const leftmost = futureTap - range;
      // don't consider taps that cannot reach our index
      if (leftmost > pointer) {
        continue;
      }
      const rightmost = futureTap + range;
      furthestRight = Math.max(furthestRight, rightmost);
    }

    if (furthestRight <= pointer) {
      return -1;
    }

    result++;
    pointer = furthestRight;
  }

  return result;
};
