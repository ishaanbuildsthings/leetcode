// https://leetcode.com/problems/evaluate-reverse-polish-notation/description/
// Difficulty: Medium
// tags: stack

// Problem
/*
Simplified:
You get: [4, 13, 5, /, +]
You output: [4 + (13 / 5)]

Detailed:
You are given an array of strings tokens that represents an arithmetic expression in a Reverse Polish Notation.

Evaluate the expression. Return an integer that represents the value of the expression.

Note that:

The valid operators are '+', '-', '*', and '/'.
Each operand may be an integer or another expression.
The division between two integers always truncates toward zero.
There will not be any division by zero.
The input represents a valid arithmetic expression in a reverse polish notation.
The answer and all the intermediate calculations can be represented in a 32-bit integer.
*/

// Solution: O(n) time and O(1) space
/*
Iterate through the tokens, whenever we get a number, push it to a stack. Whenever we get an operator, compute a result for the two most recent numbers, and edit the stack. Division should round towards 0, so -1/10 should use a ceiling, but 1/10 should use a floor.
*/

var evalRPN = function (tokens) {
  const stack = [];
  for (let token of tokens) {
    // faster than set
    if (token !== "+" && token !== "-" && token !== "*" && token !== "/") {
      stack.push(Number(token));
      continue;
    }
    // if we get an operation, the first operand should become the result of the operation, and we should remove the second, for instance: [4, 13, 5, /, +], our stack is [4, 13, 5] and we reach a /, new stack is [4, 2]
    let result;
    if (token === "+") {
      result = stack[stack.length - 2] + stack[stack.length - 1];
    } else if (token === "-") {
      result = stack[stack.length - 2] - stack[stack.length - 1];
    } else if (token === "/") {
      result = stack[stack.length - 2] / stack[stack.length - 1];
      if (result < 0) {
        result = Math.ceil(result);
      } else {
        result = Math.floor(result);
      }
    } else if (token === "*") {
      result = stack[stack.length - 2] * stack[stack.length - 1];
    }

    stack[stack.length - 2] = result;
    stack.pop();
  }
  return stack[0];
};
