// https://leetcode.com/problems/maximize-win-from-two-segments/description/
// Difficulty: Medium
// Tags: Sliding Window Variable, dynamic programming 1d

// Problem
/*
There are some prizes on the X-axis. You are given an integer array prizePositions that is sorted in non-decreasing order, where prizePositions[i] is the position of the ith prize. There could be different prizes at the same position on the line. You are also given an integer k.

You are allowed to select two segments with integer endpoints. The length of each segment must be k. You will collect all prizes whose position falls within at least one of the two selected segments (including the endpoints of the segments). The two selected segments may intersect.

For example if k = 2, you can choose segments [1, 3] and [2, 4], and you will win any prize i that satisfies 1 <= prizePositions[i] <= 3 or 2 <= prizePositions[i] <= 4.
Return the maximum number of prizes you can win if you choose the two segments optimally.
*/

// Solution, O(n) time and O(n) space
/*
We could use a sliding window, and the most prizes we can win is the amount in the current window, plus the amount from the remaining right portion. We precompute answers for the remaining right portion with a 1d dp.
*/

var maximizeWin = function (prizePositions, k) {
  /*
    memoRight[i] stores the answer to the most prizes we can win, with one segment, in [i:], though not necessarily starting at i
    */
  const memoRight = new Array(prizePositions.length);
  memoRight[prizePositions.length] = 0;

  let l = prizePositions.length - 1;
  let r = prizePositions.length - 1;
  while (l >= 0) {
    while (prizePositions[r] - prizePositions[l] > k) {
      r--;
    }

    const numPrizes = r - l + 1;
    memoRight[l] = Math.max(memoRight[l + 1], numPrizes);

    l--;
  }

  let result = 0;

  let l2 = 0;
  let r2 = 0;
  while (r2 < prizePositions.length) {
    while (prizePositions[r2] - prizePositions[l2] > k) {
      l2++;
    }

    const numPrizes = r2 - l2 + 1;
    const prizesInRightSegment = memoRight[r2 + 1];
    const totalPrizes = numPrizes + prizesInRightSegment;
    result = Math.max(result, totalPrizes);

    r2++;
  }

  return result;
};
