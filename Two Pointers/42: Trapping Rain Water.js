// https://leetcode.com/problems/trapping-rain-water/description/
// Difficulty: Hard
// tags: two pointers

// Solution O(n) time and O(1) space. Initialize two pointers on the left and right. We need to track the highest walls seen from the left and from the right. We can only trap rainwater if it's bounded from both ends, consider the elevation map: 1 0 0 0 0 with a pointer at index 1. We can't trap water there, even though it is bounded by the highestLeft wall, because it isn't bounded by the highestRight wall. As we iterate to a new pointer, we first check if we can trap new water. Otherwise, we update the max wall height. We always want to increment/decrement a pointer based on which wall is currently shorter, because that wall is constraining our problem.
/*
For instance consider:
V     V
4 9 0 6
If we decremented from the right, we could trap water at the 0, but how much? Only 4, because our constrained wall is a 4. We should increment the 4 until it is at least as high as the 6, so we can trap more water. We aren't worried about missing water on the way, because as we increment from the left, we will keep trapping water, and our constraint is the left wall.

v     v
1 3 _ 6

If we were pointing at _, and our highest walls were the 1 and 6, we would think we could only trap 1 block of water, but we can trap 3! The problem with this situation is it implies we knew of a wall of 1 and 6, but incremented the 6 wall first, we should increment the constraining factor first to possibly increase the amount of water we can trap.
*/

var trap = function (height) {
  let highestLeft = 0; // track the highest possible walls we have seen from the left side, to know if more inner cells can keep in raintwater from the outer wall
  let highestRight = 0;
  let l = 0;
  let r = height.length - 1;
  let totalWater = 0;
  while (l <= r) {
    // if we know some information, which is the shorter height, based on the shorter height, we can calculate water for a specific cell
    if (highestLeft <= highestRight) {
      if (height[l] < highestLeft) {
        totalWater += highestLeft - height[l];
      }
      highestLeft = Math.max(highestLeft, height[l]);
      l++;
    } else if (highestLeft > highestRight) {
      if (height[r] < highestRight) {
        totalWater += highestRight - height[r];
      }
      highestRight = Math.max(highestRight, height[r]);
      r--;
    }
  }
  return totalWater;
};
