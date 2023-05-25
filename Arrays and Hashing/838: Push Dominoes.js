// https://leetcode.com/problems/push-dominoes/description/
// Difficulty: Medium

// Problem
/*
Simplified:
Input: dominoes = "RR.L"
Output: "RR.L"
Explanation: The first domino expends no additional force on the second domino.

Detailed:
There are n dominoes in a line, and we place each domino vertically upright. In the beginning, we simultaneously push some of the dominoes either to the left or to the right.

After each second, each domino that is falling to the left pushes the adjacent domino on the left. Similarly, the dominoes falling to the right push their adjacent dominoes standing on the right.

When a vertical domino has dominoes falling on it from both sides, it stays still due to the balance of the forces.

For the purposes of this question, we will consider that a falling domino expends no additional force to a falling or already fallen domino.

You are given a string dominoes representing the initial state where:

dominoes[i] = 'L', if the ith domino has been pushed to the left,
dominoes[i] = 'R', if the ith domino has been pushed to the right, and
dominoes[i] = '.', if the ith domino has not been pushed.
Return a string representing the final state.
*/

// Solution, O(n) time and O(n) space. Iterate from left to right, whenever we see an L, we update distance from closest L to be 0. Whenever we see a ., we write the closest L. Whenever we see an R, distance from closest L becomes infinity since an R will always stop any number of Ls. Do the same thing in reverse for the closest R, then iterate again and update the result based on which is closer.

var pushDominoes = function (dominoes) {
  const leftDistances = new Array(dominoes.length).fill(null);

  let distanceFromLastL = Infinity;
  for (let i = dominoes.length - 1; i >= 0; i--) {
    distanceFromLastL++;

    if (dominoes[i] === "R") {
      distanceFromLastL = Infinity;
      continue;
    }
    if (dominoes[i] === "L") {
      distanceFromLastL = 0;
      continue;
    }

    leftDistances[i] = distanceFromLastL;
  }

  const rightDistances = new Array(dominoes.length).fill(null);

  let distanceFromLastR = Infinity;
  for (let i = 0; i < dominoes.length; i++) {
    distanceFromLastR++;

    if (dominoes[i] === "L") {
      distanceFromLastR = Infinity;
      continue;
    }
    if (dominoes[i] === "R") {
      distanceFromLastR = 0;
      continue;
    }

    rightDistances[i] = distanceFromLastR;
  }

  const result = dominoes.split("");

  for (let i = 0; i < result.length; i++) {
    // only want to update relevant pieces
    if (result[i] !== ".") {
      continue;
    }

    const leftDistance = leftDistances[i];
    const rightDistance = rightDistances[i];

    // can't be knocked, ex: L.R
    if (!leftDistance && !rightDistance) {
      continue;
    } else if (leftDistance && !rightDistance) {
      result[i] = "L";
    } else if (!leftDistance && rightDistance) {
      result[i] = "R;";
    } else {
      /* we have both distances */
      if (leftDistance < rightDistance) {
        result[i] = "L";
      } else if (leftDistance > rightDistance) {
        result[i] = "R";
      }
    }
  }

  return result.join("");
};
