// https://leetcode.com/problems/daily-temperatures/description/
// Difficulty: Medium
// tags: monotonic stack

// Problem
/*
Given an array of integers temperatures represents the daily temperatures, return an array answer such that answer[i] is the number of days you have to wait after the ith day to get a warmer temperature. If there is no future day for which this is possible, keep answer[i] == 0 instead.

Input: temperatures = [73,74,75,71,69,72,76,73]
Output: [1,1,4,2,1,1,0,0]
*/

// Solution

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
