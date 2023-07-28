// https://leetcode.com/problems/design-hit-counter/description/
// difficulty: Medium
// tags: queue

// Problem
/*
Design a hit counter which counts the number of hits received in the past 5 minutes (i.e., the past 300 seconds).

Your system should accept a timestamp parameter (in seconds granularity), and you may assume that calls are being made to the system in chronological order (i.e., timestamp is monotonically increasing). Several hits may arrive roughly at the same time.

Implement the HitCounter class:

HitCounter() Initializes the object of the hit counter system.
void hit(int timestamp) Records a hit that happened at timestamp (in seconds). Several hits may happen at the same timestamp.
int getHits(int timestamp) Returns the number of hits in the past 5 minutes from timestamp (i.e., the past 300 seconds).
*/

// Solution, O(1) amortized time for hit or getHits, using a real queue
/*
I didn't implement a queue, but it would be faster.

Essentially, each time we add a hit, push it to our current hits. I also clear all old hits, though this could be done just when we get hits. Similarly, when we get hits, we clear from the front, then return the length.

Worst case, we have n hits added, then we add a hit that clears everything, which is n shift operations, meaning n^2 time for a hit or getHits (amortized to n time, as each hit can only be added and removed once). With a deque, it would just be n time, and amortized to constant time.
*/

var HitCounter = function () {
  this.hits = []; // fake deque
};

HitCounter.prototype.hit = function (timestamp) {
  this.hits.push(timestamp);
  while (this.hits[0] < timestamp - 299) {
    this.hits.shift();
  }
};

HitCounter.prototype.getHits = function (timestamp) {
  while (this.hits[0] < timestamp - 299) {
    this.hits.shift();
  }
  return this.hits.length;
};
