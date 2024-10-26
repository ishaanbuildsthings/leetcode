// https://leetcode.com/problems/root-equals-sum-of-children/description/
// Difficulty: Easy

// Problem
/*
You are given the root of a binary tree that consists of exactly 3 nodes: the root, its left child, and its right child.

Return true if the value of the root is equal to the sum of the values of its two children, or false otherwise.
*/

// Solution, O(1) time and space. Done on my quest to finish all of leetcode!

var checkTree = function (root) {
  return root.val === root.left.val + root.right.val;
};
