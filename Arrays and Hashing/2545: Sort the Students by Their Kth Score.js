// https://leetcode.com/problems/sort-the-students-by-their-kth-score/description/
// difficulty: medium

// Problem
// There is a class with m students and n exams. You are given a 0-indexed m x n integer matrix score, where each row represents one student and score[i][j] denotes the score the ith student got in the jth exam. The matrix score contains distinct integers only.

// You are also given an integer k. Sort the students (i.e., the rows of the matrix) by their scores in the kth (0-indexed) exam from the highest to the lowest.

// Return the matrix after sorting it.

// Solution, O(rows * log(rows)) time and O(sort(rows)) space, just use the custom comparator. I did this in JS even after switching to python since I knew how to use the comparator!

/**
 * @param {number[][]} score
 * @param {number} k
 * @return {number[][]}
 */
var sortTheStudents = function (score, k) {
  score.sort((row1, row2) => {
    return row2[k] - row1[k];
  });
  return score;
};
