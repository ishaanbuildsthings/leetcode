// https://leetcode.com/problems/car-fleet/solutions/
// Difficulty: Medium

// Solution, O(n log n) time and O(n) space
/*
First, sort the positions and speeds by position, as we can't really do anything with the unsorted data. To know if a car forms a fleet or not, we have to know if it can catch up to the car in front of it. For instance if one car is moving at 5 and a car behind it is moving at 10, the car moving at 10 can catch up (assuming the distance from target works out), meaning 10 would not form a fleet. But if a car were moving at 5, and there were a car behind it that could never catch up, that car would form the head of a new fleet.

The tricky case is what if we have one car moving at 5, another at 20, and one at 10. The 10 car might seemingly never be able to catch up to the 20, but it might if the 5 bottlenecks the 20. What we should do is start with the car closest to the finish line, and determine how long it will take to get to the finish line. Then, go to the next car. If the next car could theoretically reach the line first, it would actually join the fleet in front of it. So the 20 would join the 5, and the bottleneck time would not change. But if we have a new slower car, say speed 3, it would form a new bottleneck time.
*/

var carFleet = function (target, position, speed) {
  const tuples = position.map((position, index) => [position, speed[index]]);
  tuples.sort((a, b) => b[0] - a[0]);
  const posSorted = tuples.map((tuple) => tuple[0]);
  const speedSorted = tuples.map((tuple) => tuple[1]);

  let fleets = 0;
  let finishTime = -Infinity; // the 'car' before the first car finishes infinitly fast, so the first car can never catch up, adding a fleet

  for (let i = 0; i < posSorted.length; i++) {
    const distanceToFinish = target - posSorted[i];
    const speed = speedSorted[i];
    const timeToFinish = distanceToFinish / speed;

    // if our car takes longer to reach the finish line than the car in front of it, add a fleet and update the bottleneck time
    if (timeToFinish > finishTime) {
      fleets++;
      finishTime = timeToFinish;
    }
  }
  return fleets;
};
