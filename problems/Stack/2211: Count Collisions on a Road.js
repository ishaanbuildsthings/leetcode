// https://leetcode.com/problems/count-collisions-on-a-road/description/
// Difficulty: Medium
// tags: stack

// Problem
/*
There are n cars on an infinitely long road. The cars are numbered from 0 to n - 1 from left to right and each car is present at a unique point.

You are given a 0-indexed string directions of length n. directions[i] can be either 'L', 'R', or 'S' denoting whether the ith car is moving towards the left, towards the right, or staying at its current point respectively. Each moving car has the same speed.

The number of collisions can be calculated as follows:

When two cars moving in opposite directions collide with each other, the number of collisions increases by 2.
When a moving car collides with a stationary car, the number of collisions increases by 1.
After a collision, the cars involved can no longer move and will stay at the point where they collided. Other than that, cars cannot change their state or direction of motion.

Return the total number of collisions that will happen on the road.
*/

// Solution, O(n) time and O(n) space
// * Solution 2, linear space is possible. Since all cars will collide except the cars on the left, moving left, and the cars on the right, moving right, so we can just count the cars in the middle basically.

// Create a stack. Handle various cases, for instance if a car is moving right, then we add a stationary car to the stack, we gain a collision(s). Importantly we need a stack because if we have multiple cars moving right, then a stationary or left car, we have to account for multiple crashes.

var countCollisions = function (directions) {
  let collisions = 0;

  const stack = [];

  for (let i = 0; i < directions.length; i++) {
    const dir = directions[i];

    if (dir === "S") {
      while (stack[stack.length - 1] === "R") {
        stack.pop();
        collisions++;
      }
      stack.push("S");
    } else if (dir === "R") {
      stack.push("R");
    } else if (dir === "L") {
      // |  <-
      if (stack[stack.length - 1] === "S") {
        collisions++;
      }

      // -> -> <-
      else if (stack[stack.length - 1] === "R") {
        collisions++; // the new left car counts as one
        while (stack[stack.length - 1] === "R") {
          stack.pop();
          collisions++;
        }
        stack.push("S");
      }
    }
  }

  return collisions;
};
