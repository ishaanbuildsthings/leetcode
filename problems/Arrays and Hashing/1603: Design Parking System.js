// https://leetcode.com/problems/design-parking-system/description/
// Difficulty: Easy

// Problem
/*
Design a parking system for a parking lot. The parking lot has three kinds of parking spaces: big, medium, and small, with a fixed number of slots for each size.

Implement the ParkingSystem class:

ParkingSystem(int big, int medium, int small) Initializes object of the ParkingSystem class. The number of slots for each parking space are given as part of the constructor.
bool addCar(int carType) Checks whether there is a parking space of carType for the car that wants to get into the parking lot. carType can be of three kinds: big, medium, or small, which are represented by 1, 2, and 3 respectively. A car can only park in a parking space of its carType. If there is no space available, return false, else park the car in that size space and return true.
*/

// Solution, O(1) time and O(1) space
/*
Create an array to store the number of spaces for each car type. When adding a car, decrement the number of spaces for that car type. If the number of spaces is 0, return false. It's a bit more of an elegant solution that creating counters for each car type, since we don't need a bunch of if statements, we can just access the indices directly.
*/

var ParkingSystem = function (big, medium, small) {
  this.storage = [big, medium, small];
};

ParkingSystem.prototype.addCar = function (carType) {
  const index = carType - 1;
  if (this.storage[index] > 0) {
    this.storage[index]--;
    return true;
  }
  return false;
};
