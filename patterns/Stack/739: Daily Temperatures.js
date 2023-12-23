// https://leetcode.com/problems/daily-temperatures/description/
// Difficulty: Medium
// tags: monotonic stack

// Problem
/*
Given an array of integers temperatures represents the daily temperatures, return an array answer such that answer[i] is the number of days you have to wait after the ith day to get a warmer temperature. If there is no future day for which this is possible, keep answer[i] == 0 instead.

Input: temperatures = [73,74,75,71,69,72,76,73]
Output: [1,1,4,2,1,1,0,0]
*/

// Solution 1: O(n) time and O(1) space
/*
Solution 1 is an extremely difficult to find solution. Consider: [60, 50, 30, 40, 70]
Initialize our output array: [0, 0, 0, 0, 0]
Start iterating backwards, if we see a new hottest temperature, record that and move on, if it is a new hottest temperature it means there are no temperatures on the right that are hotter, so we can leave the output at 0, for instance: 70 40 50 30, the 70, 50, and 30 all don't have future hotter days, so we would have 0 1 0 0.
If we see a temperature that isn't the hottest, we need to figure out how many days it has been since the hottest
60 50 30 40 70
0  0  0  0  0

we are at 40
first, check the temperature on the right, since it is possible that is hotter, 70 is indeed hotter, so we add a 1 and move on
0  0  0  1  0

we are at 30
again, the temperature on the right is hotter, add a 1 and move on
0  0  1  1  0

we are at 50, the temperature on the right, 30, is not hotter. However we know that 1 temperature to the right of 30, is hotter than 30, since the result for 30 was 1. It's possible that could be hotter than 50 as well, so we check that temperature, which is 40. It isn't hotter. Now we repeat the same process at 40, and we see it has a 1, so we check the next temperature, which is 70, that is hotter, so we add a 3.
0  3  1  1  0

we are at 60, which is not a new hottest. We repeat the process, check to the right, 50 is not hotter, but 50 lets us jump straight to the next temperature larger than 50, so we look at the end result 70, and get our final answer
4 3 1 1 0

It looks like the complexity is bad, but at most, cells will only be looked at once, since afterwards we will jump past them.
*/

// Solution 2: O(n) time and O(n) space
/*
Maintain a monotonic stack. As long as temperatures are decreasing, add a new temperature along with its index to the stack. When we find a higher temerpature, pop until the monotonic property is preserved. As we pop, compute the number of days by comparing the indices and fill out the result array. We also don't need to use tuples, we can just use the indices and look up the temperatures.
*/

var dailyTemperatures = function (temperatures) {
  const stack = [];
  const result = new Array(temperatures.length).fill(0);

  for (let i = 0; i < temperatures.length; i++) {
    const tuple = [temperatures[i], i];

    // if the new temperature is higher, keep popping
    while (stack.length > 0 && tuple[0] > stack[stack.length - 1][0]) {
      const temperatureTupleThatFoundHigher = stack.pop();
      const index = temperatureTupleThatFoundHigher[1];
      result[index] = tuple[1] - index;
    }

    stack.push(tuple);
  }
  return result;
};

// 77 76 73 72 80

// 70 60 50 65
// (70 0) (60 1) (50 2) (65 3)
