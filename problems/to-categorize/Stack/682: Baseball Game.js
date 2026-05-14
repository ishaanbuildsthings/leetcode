// https://leetcode.com/problems/baseball-game/description/
// Difficulty: Easy
// tags: stack

// Problem
/*
You are keeping the scores for a baseball game with strange rules. At the beginning of the game, you start with an empty record.

You are given a list of strings operations, where operations[i] is the ith operation you must apply to the record and is one of the following:

An integer x.
Record a new score of x.
'+'.
Record a new score that is the sum of the previous two scores.
'D'.
Record a new score that is the double of the previous score.
'C'.
Invalidate the previous score, removing it from the record.
Return the sum of all the scores on the record after applying all the operations.

The test cases are generated such that the answer and all intermediate calculations fit in a 32-bit integer and that all operations are valid.
*/

// Solution: O(n) time and space
/*
Maintain a stack, this is because we need to keep a history of all previous values. For instance if we add 10 scores then want to clear them all, we need that data saved (so O(1) space is not possible). A stack makes sense because the operations are being applied to the most recent numbers, not the first numbers.
*/

var calPoints = function (operations) {
  const stack = [];
  for (const operation of operations) {
    if (operation === "+") {
      const newNum = stack[stack.length - 1] + stack[stack.length - 2];
      stack.push(newNum);
    } else if (operation === "D") {
      const newNum = stack[stack.length - 1] * 2;
      stack.push(newNum);
    } else if (operation === "C") {
      stack.pop();
    } else {
      stack.push(Number(operation));
    }
  }
  return stack.reduce((acc, val) => acc + val, 0);
};
