// https://leetcode.com/problems/detect-squares/description/
// Difficulty: Medium

// Problem
/*
Simplfied: You are given points 1 by 1. Then, you might be given a point and a command, 'how many squares can you make with this point?' The squares must be axis-parallel. Multiples of the same point can be used to make different squares.

Detailed:
You are given a stream of points on the X-Y plane. Design an algorithm that:

Adds new points from the stream into a data structure. Duplicate points are allowed and should be treated as different points.
Given a query point, counts the number of ways to choose three points from the data structure such that the three points and the query point form an axis-aligned square with positive area.
An axis-aligned square is a square whose edges are all the same length and are either parallel or perpendicular to the x-axis and y-axis.

Implement the DetectSquares class:

DetectSquares() Initializes the object with an empty data structure.
void add(int[] point) Adds a new point point = [x, y] to the data structure.
int count(int[] point) Counts the number of ways to form axis-aligned squares with point point = [x, y] as described above.
*/

// Solution 1
/*
Create a mapping that maps x coordinates (key) to an object (value), that object maps y-coordinates (key) to the # of times that coordinate pair has occured (value)

ex: { 2 : { 5 : 3, 10 : 4 } } means 2,5 has occured 3 times, and 2,10 has occured 4

when we receive a point to add, add it to our mapping

when we receive a point to count, iterate through all points that have the same x-coordinate, since we know we need one of these to form a square. for every point, compute the sidelength, then check the other points to see if we can make a square
*/
// Time: O(n), where worst case n is the number of points, but this is only if all points have the same x-coordinate. space: O(n) as well, since we store all points

// * other solutions include mapping coordinate pairs to their occurences, iterating over all points, seeing if it is a diagonal, then checking the remaining two points

var DetectSquares = function () {
  this.mapping = {}; // maps an x coordinate (key) to a an object (value), that object maps y-coordinates to how many times that pair has occured
  // ex: { 2 : { 5 : 3, 10 : 4 } } means 2,5 has occured 3 times, and 2,10 has occured 4
};

DetectSquares.prototype.add = function (point) {
  const x = point[0];
  const y = point[1];

  // if we have never seen this x coordinate, initialize everything
  if (!(x in this.mapping)) {
    this.mapping[x] = { [y]: 1 };
  }

  // if we have seen the y-coord but not the x
  else if (!(y in this.mapping[x])) {
    this.mapping[x][y] = 1;
  }

  // if we have seen this exact coordinate before
  else {
    this.mapping[x][y]++;
  }
};

DetectSquares.prototype.count = function (point) {
  const x = point[0];
  const y = point[1];
  let totalSquares = 0;

  const yCoords = this.mapping[x];

  // iterate over the vertical line
  for (let yCoord in yCoords) {
    // since yCoord was a key, we need to convert it to a number
    yCoord = Number(yCoord);

    // don't consider points that are exactly the same as ours
    if (yCoord === y) continue;

    // otherwise we have a point above or below ours
    const sidelength = Math.abs(yCoord - y);

    // if we also see the bottom left and top left coordinates, add that many squares
    if (
      this.mapping[x - sidelength] &&
      this.mapping[x - sidelength][y] &&
      this.mapping[x - sidelength][yCoord]
    ) {
      const squares =
        1 *
        this.mapping[x][yCoord] *
        this.mapping[x - sidelength][y] *
        this.mapping[x - sidelength][yCoord];
      totalSquares += squares;
    }

    // if we also see the bottom right and top right coordinates, add that many squares
    if (
      this.mapping[x + sidelength] &&
      this.mapping[x + sidelength][y] &&
      this.mapping[x + sidelength][yCoord]
    ) {
      const squares =
        1 *
        this.mapping[x][yCoord] *
        this.mapping[x + sidelength][y] *
        this.mapping[x + sidelength][yCoord];
      totalSquares += squares;
    }
  }
  return totalSquares;
};

/**
 * Your DetectSquares object will be instantiated and called as such:
 * var obj = new DetectSquares()
 * obj.add(point)
 * var param_2 = obj.count(point)
 */
