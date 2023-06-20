// https://leetcode.com/problems/find-the-highest-altitude/description/
// Difficulty: Easy

// Problem
/*
Simplified:
Input: gain = [-5,1,5,0,-7]
Output: 1
Explanation: The altitudes are [0,-5,-4,1,1,-6]. The highest is 1.

Detailed:
There is a biker going on a road trip. The road trip consists of n + 1 points at different altitudes. The biker starts his trip on point 0 with altitude equal 0.

You are given an integer array gain of length n where gain[i] is the net gain in altitude between points i​​​​​​ and i + 1 for all (0 <= i < n). Return the highest altitude of a point.
*/

// Solution, O(n) time and O(1) space. Iterate through gains and track the highest altitude.

var largestAltitude = function (gain) {
  let currentElevation = 0;
  let result = 0;
  for (const diff of gain) {
    currentElevation += diff;
    result = Math.max(result, currentElevation);
  }
  return result;
};
