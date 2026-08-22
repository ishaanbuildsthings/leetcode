// https://leetcode.com/problems/maximum-fruits-harvested-after-at-most-k-steps/description/
// Difficulty: Hard
// Tags: prefix

// Problem
/*

Fruits are available at some positions on an infinite x-axis. You are given a 2D integer array fruits where fruits[i] = [positioni, amounti] depicts amounti fruits at the position positioni. fruits is already sorted by positioni in ascending order, and each positioni is unique.

You are also given an integer startPos and an integer k. Initially, you are at the position startPos. From any position, you can either walk to the left or right. It takes one step to move one unit on the x-axis, and you can walk at most k steps in total. For every position you reach, you harvest all the fruits at that position, and the fruits will disappear from that position.

Return the maximum total number of fruits you can harvest.
*/

// Solution, O(n + k) time, O(k) space
/*
We can just preprocess the amounts of fruits we get from walking up to k steps left, and up to k steps right. Then try all combinations of first walking some steps, then going right, and vice versa. Don't forget to add strawberries if they are on the cell we start at.
*/

var maxTotalFruits = function (fruits, startPos, k) {
  const fruitsDict = {}; // makes it easier to see if there are fruits at a step, maps a position to how many fruits are there
  for (const fruitTuple of fruits) {
    fruitsDict[fruitTuple[0]] = fruitTuple[1];
  }

  const leftCounts = []; // leftCounts[steps] tells us the amount of fruit we get just by walking left that many steps, but cuts off after the leftmost fruit
  // walk all the way left and see how many fruits we get
  let totalFruits = 0;
  for (let pos = startPos - 1; pos >= fruits[0][0]; pos--) {
    const stepsTaken = startPos - pos;
    if (stepsTaken > k) {
      break;
    }
    if (fruitsDict[pos] !== undefined) {
      totalFruits += fruitsDict[pos];
    }
    leftCounts[stepsTaken] = totalFruits;
  }

  const rightCounts = [];
  totalFruits = 0;
  for (let pos = startPos + 1; pos <= fruits[fruits.length - 1][0]; pos++) {
    const stepsTaken = pos - startPos;
    if (stepsTaken > k) {
      break;
    }
    if (fruitsDict[pos] !== undefined) {
      totalFruits += fruitsDict[pos];
    }
    rightCounts[stepsTaken] = totalFruits;
  }

  let result = 0;

  // simulate going `stepsLeft` left first, then the remaining steps right
  for (let stepsLeft = 1; stepsLeft <= k; stepsLeft++) {
    // if we passed the leftmost fruit, we just terminate early
    if (leftCounts[stepsLeft] === undefined) {
      break;
    }

    const fruitsFromLeft = leftCounts[stepsLeft];
    const remainingSteps = k - 2 * stepsLeft; // recenter at origin

    let fruitsFromRight = 0;
    if (remainingSteps > 0) {
      // its possible we have so many remaining steps to go right, that we might even pass the right most fruit (which would be out of bounds for rightCounts)
      if (rightCounts[remainingSteps] === undefined) {
        if (rightCounts.length === 0) {
          fruitsFromRight = 0;
        } else {
          fruitsFromRight = rightCounts[rightCounts.length - 1];
        }
      } else {
        fruitsFromRight = rightCounts[remainingSteps];
      }
    }
    const totalFruits = fruitsFromLeft + fruitsFromRight;

    result = Math.max(result, totalFruits);
  }

  // simulate going `stepsRight` right first, then the remaining steps left
  for (let stepsRight = 1; stepsRight <= k; stepsRight++) {
    if (rightCounts[stepsRight] === undefined) {
      break;
    }

    const fruitsFromRight = rightCounts[stepsRight];
    const remainingSteps = k - 2 * stepsRight;

    let fruitsFromLeft = 0;
    if (remainingSteps > 0) {
      if (leftCounts[remainingSteps] === undefined) {
        if (leftCounts.length === 0) {
          fruitsFromLeft = 0;
        } else {
          fruitsFromLeft = leftCounts[leftCounts.length - 1];
        }
      } else {
        fruitsFromLeft = leftCounts[remainingSteps];
      }
    }

    const totalFruits = fruitsFromLeft + fruitsFromRight;

    result = Math.max(result, totalFruits);
  }

  // there may have been fruits on the step we started
  if (fruitsDict[startPos] !== undefined) {
    return result + fruitsDict[startPos];
  }
  return result;
};
