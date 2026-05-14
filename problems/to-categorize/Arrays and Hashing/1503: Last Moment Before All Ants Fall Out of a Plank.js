//https://leetcode.com/problems/last-moment-before-all-ants-fall-out-of-a-plank/description/
// Difficulty: Medium

// Problem
/*
We have a wooden plank of the length n units. Some ants are walking on the plank, each ant moves with a speed of 1 unit per second. Some of the ants move to the left, the other move to the right.

When two ants moving in two different directions meet at some point, they change their directions and continue moving again. Assume changing directions does not take any additional time.

When an ant reaches one end of the plank at a time t, it falls out of the plank immediately.

Given an integer n and two integer arrays left and right, the positions of the ants moving to the left and the right, return the moment when the last ant(s) fall out of the plank.
*/

// Solution, O(n) time and O(1) space
// Standard ants on a log problem. We can treat the ants as walking through each other insteaad of colliding, to simplify the calculations.

var getLastMoment = function (n, left, right) {
  let maxDistance = 0;
  for (const leftPos of left) {
    if (leftPos > maxDistance) {
      maxDistance = leftPos;
    }
  }
  for (const rightPos of right) {
    if (n - rightPos > maxDistance) {
      maxDistance = n - rightPos;
    }
  }

  return maxDistance;
};
