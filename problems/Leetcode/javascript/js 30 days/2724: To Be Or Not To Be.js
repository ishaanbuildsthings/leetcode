// https://leetcode.com/problems/to-be-or-not-to-be/description/
// Difficulty: Easy

// Problem
// Write a function expect that helps developers test their code. It should take in any value val and return an object with the following two functions.

// toBe(val) accepts another value and returns true if the two values === each other. If they are not equal, it should throw an error "Not Equal".
// notToBe(val) accepts another value and returns true if the two values !== each other. If they are equal, it should throw an error "Equal".

// Solution
// Make expect return an instance of a class with the appropriate methods.
class Test {
  constructor(init) {
    this.init = init;
  }
  toBe(val) {
    if (this.init === val) {
      return true;
    }
    throw new Error("Not Equal");
  }
  notToBe(val) {
    if (this.init !== val) {
      return true;
    }
    throw new Error("Equal");
  }
}

/**
 * @param {string} val
 * @return {Object}
 */
var expect = function (val) {
  return new Test(val);
};

/**
 * expect(5).toBe(5); // true
 * expect(5).notToBe(5); // throws "Equal"
 */
