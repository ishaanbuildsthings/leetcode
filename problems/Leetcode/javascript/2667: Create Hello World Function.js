// https://leetcode.com/problems/create-hello-world-function/
// Difficulty: Easy

// Problem
/*
Write a function createHelloWorld. It should return a new function that always returns "Hello World".
*/

// Solution, O(1) time and space to create the function. One of the easiest questions on leetcode!

var createHelloWorld = function () {
  return function (...args) {
    return "Hello World";
  };
};
