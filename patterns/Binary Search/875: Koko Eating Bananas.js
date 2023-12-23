// https://leetcode.com/problems/koko-eating-bananas/description/
// Difficulty: Medium
// tags: binary search

// Problem
/*
Simplfied: Koko has an array of piles of bananas. She can eat a certain number of bananas per hour. She wants to eat all the bananas before the guards come back in h hours. Return the minimum number of bananas she can eat per hour to finish all the bananas in time. Once she finishes a pile she stops for that hour

Detailed:
Koko loves to eat bananas. There are n piles of bananas, the ith pile has piles[i] bananas. The guards have gone and will come back in h hours.

Koko can decide her bananas-per-hour eating speed of k. Each hour, she chooses some pile of bananas and eats k bananas from that pile. If the pile has less than k bananas, she eats all of them instead and will not eat any more bananas during this hour.

Koko likes to eat slowly but still wants to finish eating all the bananas before the guards return.

Return the minimum integer k such that she can eat all the bananas within h hours.
*/

// Solution
/* O(n * log k) time, where n is the number of piles, and k is the maximum sized pile, O(1) space. We can establish an upper bound to be the maximum pile size, since in the worst case koko will need to eat that many bananas per hour (piles is always <= h). The lower bound could be 0 or the minimum number of time needed to finish all the bananas ignoring the piles. We test the middle eating speed, which is an n operation, and adjust our new test eating speed until we find the smallest one. */

var minEatingSpeed = function (piles, h) {
  const totalBananas = piles.reduce((acc, val) => acc + val);

  let upperBound = Math.max(...piles);
  let lowerBound = Math.ceil(totalBananas / h); // if koko doesn't eat this many bananas per hour, the bananas wouldn't even finish, regardless of the arrangement

  // we are trying to figure out the minimum eating speed koko can use
  let currentEatingSpeed = Math.floor((lowerBound + upperBound) / 2);
  while (lowerBound < upperBound) {
    currentEatingSpeed = Math.floor((lowerBound + upperBound) / 2); // we have some eating speed to test

    // figure out how long koko takes to eat the bananas
    let totalHours = 0;
    for (let pile of piles) {
      totalHours += Math.ceil(pile / currentEatingSpeed);
    }
    // if koko took too long to eat the bananas, we must try a strictly faster eating speed
    if (totalHours > h) {
      lowerBound = currentEatingSpeed + 1;
    }
    // if koko finished the bananas, we can try a faster speed
    else if (totalHours <= h) {
      upperBound = currentEatingSpeed;
    }
  }
  return lowerBound;
};
