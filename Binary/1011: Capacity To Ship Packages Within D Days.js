// https://leetcode.com/problems/capacity-to-ship-packages-within-d-days/description/
// Difficulty: Medium
// tags: binary search

// Problem
/*
A conveyor belt has packages that must be shipped from one port to another within days days.

The ith package on the conveyor belt has a weight of weights[i]. Each day, we load the ship with packages on the conveyor belt (in the order given by weights). We may not load more weight than the maximum weight capacity of the ship.

Return the least weight capacity of the ship that will result in all the packages on the conveyor belt being shipped within days days.
*/

// Solution
/*
Assign an upper and lower boundary for the number of days. We know we must at least fit the biggest size package, so our lower boundary is that. Our lower boundary could also be the minimum capacity we would need to fit totalWeight/num days, but the largest weight is a better lower bound, since it's almost always bigger than the average weight. For the upper bound, what is the worst case? It is if we can only ship one package a day, and we need the max capacity to ship it, so it would be the max capacity * number of days we need. For instance 10 packages of weight 10, and only 5 days to ship them, we would need to do 2 a day, so 20.

Do a binary search, check the number of days we take, and adjust accordingly
*/

var shipWithinDays = function (weights, days) {
  // initialize boundaries
  const maxWeight = weights.reduce((acc, val) => Math.max(acc, val));
  let lowerBound = maxWeight;
  const minPackagesPerDay = Math.ceil(weights.length / days);
  let upperBound = maxWeight * minPackagesPerDay;

  let midpoint = Math.floor((upperBound + lowerBound) / 2);

  while (lowerBound < upperBound) {
    midpoint = Math.floor((upperBound + lowerBound) / 2); // errs left, our packing capacity

    // track if we can pack all the weights under the days threshold
    let currentSum = 0;
    let currentDays = 1;
    for (const weight of weights) {
      // if we can fit the weight in our packing capacity, do so
      if (currentSum + weight <= midpoint) {
        currentSum += weight;
      }
      // otherwise, we need an extra day, and we can reset our sum to be that new weight
      else {
        currentDays++;
        currentSum = weight;
      }
    }

    // we could finish in time, try a smaller capacity, but this might have been our smallest capacity so we should keep it in the range
    if (currentDays <= days) {
      upperBound = midpoint;
    }
    // we definitely could not finish in time, we need to try at least 1 capacity higher
    else {
      lowerBound = midpoint + 1;
    }
  }

  return lowerBound;
};

// capacity: 4
//     weights 3 3 7
