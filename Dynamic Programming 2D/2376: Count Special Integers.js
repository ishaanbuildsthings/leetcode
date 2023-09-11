// https://leetcode.com/problems/count-special-integers/
// Difficulty: Hard
// Tags: dynamic programming 2d, digit dp

// Problem
// We call a positive integer special if all of its digits are distinct.

// Given a positive integer n, return the number of special integers that belong to the interval [1, n].

// Solution, complexities listed inside
// Say we have taken some numbers. For that state, we need to know which numbers we took, so we don't repeat numbers. We also need to know the current index we are inserting a number at. This kind of represents an offset. For instance if our number is at most 5 digits, 00_ _ _ is clearly different than 0 _ _ _ _, even if the digit we insert is the same. We also need to know if we are allowed to break the bounds of the ith digit, this is the tight variable. For instance if n=25, and we pick a 1 for the first digit, we have free choice for the next. If we pick a 2, we are still bounded. We also use the index to compute this.

// Establish a dp state of length(n) * 2 (if tight or not) * bitmask (which numbers we have taken). This is 20*1024. Each state considers up to 10 digits.

// For each state, we check which digits we can take. If we are still tight, we can only take up to the ith digit of the original number. We also cannot take duplicate numbers so we check our mask. We can always take a 0 if we are leading, but once we aren't leading anymore, we can only take a 0 once, and we start marking the mask.

/**
 * @param {number} n
 * @return {number}
 */
var countSpecialNumbers = function (n) {
  const strNum = String(n);
  // memo[index][digitsConsideredMask][tight]
  const memo = new Array(strNum.length)
    .fill()
    .map(() => new Array(1024).fill().map(() => new Array(2).fill(-1)));

  function dp(index, mask, tight) {
    // base case, we are at the end
    if (index === strNum.length) {
      // we don't gain a number if we only took 0s
      return mask === 0 ? 0 : 1;
    }

    if (memo[index][mask][tight] !== -1) {
      return memo[index][mask][tight];
    }

    // what we can go up to if we are tight
    const tightBound = Number(strNum[index]);
    const upperBound = tight ? tightBound : 9;

    let resForThis = 0;

    for (let digit = 0; digit <= upperBound; digit++) {
      // skip numbers we already took
      if ((mask >> digit) & 1) {
        continue;
      }
      // if we were tight, and we took the top digit, we are still tight. if we weren't tight, or we broke the tightness, we arent
      const newTight = tight && digit === Number(strNum[index]) ? 1 : 0;
      let newMask;
      // we can always take a 0 if we are still leading. once we stop leading (our mask is > 0), then we cannot take a 0 anymore
      if (digit === 0) {
        // if we have already taken a number, now we need to mark the 0 as taken, to prevent numbers like 100 from being counted as special
        if (mask > 0) {
          newMask = mask | 1;
        }
        // if we have never taken a number, we should freely be allowed to take 0s without it interfering with duplicate numbers
        else {
          newMask = mask;
        }
      } else {
        newMask = mask | (1 << digit);
      }
      resForThis += dp(index + 1, newMask, newTight);
    }

    memo[index][mask][tight] = resForThis;
    return resForThis;
  }

  return dp(0, 0, 1);
};
