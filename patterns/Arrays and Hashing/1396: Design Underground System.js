// https://leetcode.com/problems/design-underground-system/description/
// Difficulty: Medium

// Problem
/*
An underground railway system is keeping track of customer travel times between different stations. They are using this data to calculate the average time it takes to travel from one station to another.

Implement the UndergroundSystem class:

void checkIn(int id, string stationName, int t)
A customer with a card ID equal to id, checks in at the station stationName at time t.
A customer can only be checked into one place at a time.
void checkOut(int id, string stationName, int t)
A customer with a card ID equal to id, checks out from the station stationName at time t.
double getAverageTime(string startStation, string endStation)
Returns the average time it takes to travel from startStation to endStation.
The average time is computed from all the previous traveling times from startStation to endStation that happened directly, meaning a check in at startStation followed by a check out from endStation.
The time it takes to travel from startStation to endStation may be different from the time it takes to travel from endStation to startStation.
There will be at least one customer that has traveled from startStation to endStation before getAverageTime is called.
You may assume all calls to the checkIn and checkOut methods are consistent. If a customer checks in at time t1 then checks out at time t2, then t1 < t2. All events happen in chronological order.
*/

// Solution, O(1) time for checkin, checkout, and get average. O(n^2) space for storing all completed trips (n^2 possible trips), where n is the number of stations. Also O(k) space to hold the concurrent passengers traveling, who have not yet been added to the mapping, so O(n^2 + k) space.
/*
Put concurrent passengers in a mapping, { 42 : ['leyton', 9] }.
When they complete a trip, remove them. Calculate their travel time, and update a mapping that contains { start location -> { end location -> [count, average time] } }.
We can also have a mapping that contains { [start location, end location] => [count, average time] }. Which is the same storage complexity but might be better in practice.
*/

var UndergroundSystem = function () {
  this.checkins = {};
  /*
    maps customer IDs to a tuple containing where they departed from, and at what time
    {
        42 : ['leyton', 9],
        32 : ['paradise', 14],
    }
    */

  this.mapping = {};
  /*
    maps check in locations to hash maps
    {
        leyton : {},
        paradise : {},
        cambridge : {}.
    }

    Each inner hash map contains the ending stations, and an average + count of how long it took to get there

    leyton : {
        paradise : [5, 36], // 5 people have gone from leyton to paradise, it takes 36 minutes on average
        cambridge : [9, 94], // 9 people have gone from leyton to cambridge, it takes 94 minutes on average
    }
    */
};

UndergroundSystem.prototype.checkIn = function (id, stationName, t) {
  this.checkins[id] = [stationName, t];
};

/**
 * @param {number} id
 * @param {string} stationName
 * @param {number} t
 * @return {void}
 */
UndergroundSystem.prototype.checkOut = function (id, stationName, t) {
  const tuple = this.checkins[id];
  const departureStation = tuple[0];
  const departureTime = tuple[1];
  delete this.checkins[id];
  const travelTime = t - departureTime;

  // if a trip from the traveler's starting location has been made
  if (departureStation in this.mapping) {
    const innerMap = this.mapping[departureStation]; // tracks trips to tuples of count/time
    // if this trip has been made before, update the average time
    if (stationName in innerMap) {
      const countTimeTuple = innerMap[stationName];
      const oldCount = countTimeTuple[0];
      const oldTime = countTimeTuple[1];
      const totalOldTime = oldCount * oldTime;
      const totalNewTime = travelTime + totalOldTime;
      const newCount = oldCount + 1;
      const newTime = totalNewTime / newCount;
      const newTuple = [newCount, newTime];
      innerMap[stationName] = newTuple;
    }
    // if the trip departing from the station has been made, but not arriving at this station, initialize the average time
    else {
      innerMap[stationName] = [1, travelTime];
    }
  }
  // if a trip from the traveler's starting location has never been made
  else {
    this.mapping[departureStation] = { [stationName]: [1, travelTime] };
  }
};

/**
 * @param {string} startStation
 * @param {string} endStation
 * @return {number}
 */
UndergroundSystem.prototype.getAverageTime = function (
  startStation,
  endStation
) {
  const innerMap = this.mapping[startStation];
  const tuple = innerMap[endStation];
  const averageTime = tuple[1];
  return averageTime;
};

/**
 * Your UndergroundSystem object will be instantiated and called as such:
 * var obj = new UndergroundSystem()
 * obj.checkIn(id,stationName,t)
 * obj.checkOut(id,stationName,t)
 * var param_3 = obj.getAverageTime(startStation,endStation)
 */
