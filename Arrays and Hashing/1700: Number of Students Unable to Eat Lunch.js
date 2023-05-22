// https://leetcode.com/problems/number-of-students-unable-to-eat-lunch/description/
// Difficulty: Easy
// tags: queue

// Problem
/*
Simplified: We have lunches: [1, 0, 0, 1, 1, 1] and students [0, 1, 0, 0, 1, 0]. If the top student can eat the top lunch they do, otherwise they queue in the end of the line again. Find out how many cannot eat.
*/

// Solution 1, O(n) time and O(1) space
/*
It doesn't matter what order the students try to eat in, because students are not unique and potentially all students get to try to eat the same lunch. Maintain a counter for the number of 1 students we have left, and number of 0s, and keep iterating over the sandwiches until one of them blocks.
*/

var countStudents = function (students, sandwiches) {
  let oneCount = 0;
  let zeroCount = 0;
  for (const student of students) {
    if (student === 1) {
      oneCount++;
    } else {
      zeroCount++;
    }
  }

  let totalEaten = 0;
  for (const sandwich of sandwiches) {
    if (sandwich === 1 && oneCount > 0) {
      oneCount--;
      totalEaten++;
    } else if (sandwich === 1 && oneCount === 0) {
      return sandwiches.length - totalEaten;
    } else if (sandwich === 0 && zeroCount > 0) {
      zeroCount--;
      totalEaten++;
    } else if (sandwich === 0 && zeroCount === 0) {
      return sandwiches.length - totalEaten;
    }
  }

  return 0;
};

// Solution 2, O(n^2) time, assuming we use a deque, and O(1) space
/*
Simulate the eating, check each student and add them back to the end of the line. If no students could eat in a rotation, break.
*/

var countStudents = function (students, sandwiches) {
  while (true) {
    const sandwichLength = sandwiches.length;
    for (let i = 0; i < students.length; i++) {
      if (students[0] === sandwiches[0]) {
        students.shift();
        sandwiches.shift();
      } else {
        const student = students.shift();
        students.push(student);
      }
    }
    if (sandwiches.length === sandwichLength) {
      return students.length;
    }
  }
};
/*
sand         student
1 0 0 0 1 1 | 1 1 1 0 0 1
  0 0 0 1 1 |   1 1 0 0 1
  0 0 0 1 1 |   1 0 0 1 1
  0 0 0 1 1 |   0 0 1 1 1
    0 0 1 1 |     0 1 1 1
      0 1 1 |       1 1 1
*/
