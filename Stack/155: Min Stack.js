// https://leetcode.com/problems/min-stack/description/
// Difficulty: Medium
// tags: stack

// Problem
/*
Simplified: Design a stack that support push, pop, top (peek), and retrieve minimum in O(1) time.
*/

// Solution
// O(1) time for all operations, O(n) space
/*
Maintain a stack, and use normal push/pop/top functions. Also maintain a stack that tracks the minimums at a given time. Whenever we add a new minimum, it means only future elements are affected, so our min-stack simply needs to add that new minimum to it.
Stack: [3, 5, 2, 1, 4]
Minstack: [3, 3, 2, 1, 1]

Whenever we pop something, pop from the minstack. When we push something, check if it would make a new minimum, if it does, push that to the minstack. Otherwise push the previous minimum to the minstack. If we push an item for the first time, handle that edge case.
*/

var MinStack = function () {
  this.stack = [];
  this.mins = [];
  // [3, 5, 2, 1]
  // [3, 3, 2, 1]
};

/**
 * @param {number} val
 * @return {void}
 */
MinStack.prototype.push = function (val) {
  // edge case, if we are adding the first number, we have no prior minimum to compare to
  if (this.stack.length === 0) {
    this.stack.push(val);
    this.mins.push(val);
    return;
  }
  // if our new number is the smallest, add that smallest to our mins
  else if (val < this.mins[this.mins.length - 1]) {
    this.mins.push(val);
  }
  // if the new num is not the smallest, the smallest after we add the new num is what the previous smallest was
  else {
    this.mins.push(this.mins[this.mins.length - 1]);
  }

  this.stack.push(val);
};

/**
 * @return {void}
 */
MinStack.prototype.pop = function () {
  this.stack.pop();
  this.mins.pop();
};

/**
 * @return {number}
 */
MinStack.prototype.top = function () {
  return this.stack[this.stack.length - 1];
};

/**
 * @return {number}
 */
MinStack.prototype.getMin = function () {
  return this.mins[this.mins.length - 1];
};

/**
 * Your MinStack object will be instantiated and called as such:
 * var obj = new MinStack()
 * obj.push(val)
 * obj.pop()
 * var param_3 = obj.top()
 * var param_4 = obj.getMin()
 */
