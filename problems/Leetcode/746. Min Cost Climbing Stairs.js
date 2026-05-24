/**
 * @param {number[]} cost
 * @return {number}
 */
var minCostClimbingStairs = function(cost) {
    // edge case that lets us iterate from the 3rd to last element later
    if (cost.length === 2) {
        return Math.min(...cost);
    }

    let costRight = cost[cost.length - 1];
    let costLeft = cost[cost.length - 2];
    let currentCost = 0;
    for (let i = cost.length - 3; i >= 0; i--) {
        const option1 = cost[i] + costLeft;
        const option2 = cost[i] + costRight;
        currentCost = Math.min(option1, option2);
        costRight = costLeft;
        costLeft = currentCost;
    }

    return Math.min(currentCost, costRight); // since we can start at the first or second step
};