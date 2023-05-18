// https://leetcode.com/problems/asteroid-collision/description/
// Difficulty: Medium
// tags: stack

// Problem
/*
 */

// Solution: O(n) time (at most every asteroid can be added and destroyed once) and O(n) space
/*
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
