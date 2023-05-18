// https://leetcode.com/problems/asteroid-collision/description/
// Difficulty: Medium
// tags: stack

// Problem
/*
Simplified:
Input: asteroids = [10,2,-5]
Output: [10]
Explanation: The 2 and -5 collide resulting in -5. The 10 and -5 collide resulting in 10.

Detailed:
We are given an array asteroids of integers representing asteroids in a row.

For each asteroid, the absolute value represents its size, and the sign represents its direction (positive meaning right, negative meaning left). Each asteroid moves at the same speed.

Find out the state of the asteroids after all collisions. If two asteroids meet, the smaller one will explode. If both are the same size, both will explode. Two asteroids moving in the same direction will never meet.


 */

// Solution: O(n) time (at most every asteroid can be added and destroyed once) and O(n) space
/*
Iterate over each asteroid, as long as it is facing left and the asteroid on its left isn't facing right, we don't have a collision. We can also add asteroids facing right whenever. If we add an asteroid facing left, and we already had an asteroid facing right, pop while there are collisions, handling the cases as needed. The code could be simplified a bit but this is very explicit / clear.
 */

var asteroidCollision = function (asteroids) {
  // initialize it with the first asteroid to avoid handling the edge case later of trying to add the first asteroid to the stack and having no prior asteroids to compare it to
  const stack = [asteroids[0]];
  for (let i = 1; i < asteroids.length; i++) {
    // if the asteroids are moving the same direction, we can add the new asteroid and continue
    if (
      (stack[stack.length - 1] < 0 && asteroids[i] < 0) ||
      (stack[stack.length - 1] > 0 && asteroids[i] > 0)
    ) {
      stack.push(asteroids[i]);
      continue;
    }

    // if the left asteroid is moving left, and our new asteroid is moving right, we can also add it and continue
    if (stack[stack.length - 1] < 0 && asteroids[i] > 0) {
      stack.push(asteroids[i]);
      continue;
    }

    let asteroidDestroyed = false;
    // while the most recent asteroid is moving right and not destroyed, keep handling collisions
    while (stack[stack.length - 1] > 0 && !asteroidDestroyed) {
      // if our new asteroid is too big, break the most recent one
      if (Math.abs(asteroids[i]) > stack[stack.length - 1]) {
        stack.pop();
      }
      // if our new asteroid is the exact same size, break the most recent one and indicate our new asteroid is broken
      else if (Math.abs(asteroids[i]) === stack[stack.length - 1]) {
        stack.pop();
        asteroidDestroyed = true;
      }
      // if our new asteroid is smaller, destroy it
      else if (Math.abs(asteroids[i]) < stack[stack.length - 1]) {
        asteroidDestroyed = true;
      }
    }

    if (!asteroidDestroyed) {
      stack.push(asteroids[i]);
    }
  }
  return stack;
};
