// https://leetcode.com/problems/maximum-number-of-groups-with-increasing-length/description/
// difficulty: Hard

// Problem
/*
You are given a 0-indexed array usageLimits of length n.

Your task is to create groups using numbers from 0 to n - 1, ensuring that each number, i, is used no more than usageLimits[i] times in total across all groups. You must also satisfy the following conditions:

Each group must consist of distinct numbers, meaning that no duplicate numbers are allowed within a single group.
Each group (except the first one) must have a length strictly greater than the previous group.
Return an integer denoting the maximum number of groups you can create while satisfying these conditions.
*/

// Solution, O(n log n) time, O(sort) space
/*
This problem was hard! I failed to derive the math solution in time during the contest. Initially, I tried a greedy solution, which TLEd due to too high usageLimit[i]. Then I tried to more abstractly represent the state with pointers, which I never got working. I don't think it fully works, but could be distilled to the math solution, though I didn't end up seeing it without help.

Of course, the most groups we can have is usageLimits.length.

I tried initially greedily sorting by largest first, then filling out resulting rows with characters (abstractly via pointers). But this fails for something like [10, 9, 2, 2, 1, 1]. as the greedy strategy produces 4 but the answer is 5. The problem is that I need to stack on top of prior elements (this might not make sense in the future but doesn't matter too much, I have drawn so many of these charts the past few days).

Ultimately, we can add numbers from the smallest count to the largest.

When we add a number, if we have sufficient elements for the next triangle number, we gain a group.

Imagine we have:
1, 1, 2, 2

then:

X = 1 group

X Y = 1 group

  Z
X Y Z = 2 groups

    A
  Z A
X Y Z = 3 groups

We're building top to bottom for each column, but in actuality the groups appear left to right.

There was a more formal way to represent this, which is basically to have n groups, say n is 3:

we must have a number a >= 1
a number b, so a+b >= 3
a number c, so a+b+c >= 6

etc

Not a very intuitive problem, math analysis is very hard.
*/

var maxIncreasingGroups = function (usageLimits) {
  // 0-indexed
  function getTriangleNum(num) {
    return ((1 + num) * (1 + (1 + num))) / 2;
  }

  let result = 0;
  let totalElements = 0;

  usageLimits.sort((a, b) => a - b);

  for (let i = 0; i < usageLimits.length; i++) {
    totalElements += usageLimits[i];
    // triangle number goal is what result currently is
    if (totalElements >= getTriangleNum(result)) {
      result++;
    }
  }

  return result;
};
