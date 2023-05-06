// https://leetcode.com/problems/trapping-rain-water/description/
// Difficulty: Hard
// tags: two pointers

// Solution O(n) time and O(1) space. Initialize two pointers on the left and right. We need to track the highest walls seen from the left and from the right. We can only trap rainwater if it's bounded from both ends, consider the elevation map: 1 0 0 0 0 with a pointer at index 1. We can't trap water there, even though it is bounded by the highestLeft wall, because it isn't bounded by the highestRight wall. As we iterate to a new pointer, we first check if we can trap new water. Otherwise, we update the max wall height. We always want to increment/decrement a pointer based on which wall is currently shorter, because that wall is constraining our problem.
/*
For instance consider:
V     V
4 9 0 6
If we decremented from the right, we could trap water at the 0, but how much? Only 4, because our constrained wall is a 4. We should increment the 4 until it is at least as high as the 6, so we can trap more water. We aren't worried about missing water on the way, because as we increment from the left, we will keep trapping water, and our constraint is the left wall.
*/

const trap = function (height) {
  let highestLeft = 0; // track the highest possible walls we have seen from the left side, to know if more inner cells can keep in raintwater from the outer wall
  let highestRight = 0;
  let l = 0;
  let r = height.length - 1;
  let totalWater = 0;
  while (l <= r) {
    const shortestHeight = Math.min(highestLeft, highestRight);

    // if we are bounded on both sides, we know we can trap rain water
    if (height[l] < shortestHeight) {
      totalWater += shortestHeight - height[l];
    }
    if (height[r] < shortestHeight) {
      totalWater += shortestHeight - height[r];
    }

    // update the new max heights
    highestLeft = Math.max(highestLeft, height[l]);
    highestRight = Math.max(highestRight, height[r]);

    if (height[l] <= height[r]) {
      l++;
    } else {
      r--;
    }
  }
  return totalWater;
};
