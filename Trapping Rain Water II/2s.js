/**
 * @param {number[][]} heightMap
 * @return {number}
 */
var trapRainWater = function (heightMap) {
  const cache = {}; // maps dp calls to their outputs

  function dp(rowCoordinate, colCoordinate, visitedCells, depth) {
    // caching
    const cacheKey = JSON.stringify([rowCoordinate, colCoordinate]);
    if (cacheKey in cache) {
      return cache[cacheKey];
    }

    const visitedCellsNew = new Set(visitedCells);

    const cellHeight = heightMap[rowCoordinate][colCoordinate];

    // if we are at a boundary of the matrix, we will spill over the edge, immediately return the cells height as the boundary
    if (
      rowCoordinate === 0 ||
      rowCoordinate === heightMap.length - 1 ||
      colCoordinate === 0 ||
      colCoordinate === heightMap[0].length - 1
    ) {
      cache[cacheKey] = cellHeight;
      return cellHeight;
    }

    // neighbors to call, we are no longer at a boundary at this point in the code
    const neighborCoords = [
      [rowCoordinate - 1, colCoordinate], // top
      [rowCoordinate, colCoordinate + 1], // right
      [rowCoordinate, colCoordinate - 1], // left
      [rowCoordinate + 1, colCoordinate], // bottom
    ];

    // remove visited cells in the current DP chain
    neighborCoordsFiltered = neighborCoords.filter(
      (coords) => !visitedCellsNew.has(JSON.stringify(coords))
    );

    // add current cell to visited for future calls
    visitedCellsNew.add(JSON.stringify([rowCoordinate, colCoordinate]));

    const recursedDps = neighborCoordsFiltered.map((coords) =>
      dp(coords[0], coords[1], visitedCellsNew, depth + 1)
    );
    const minRecursedDps = Math.min(...recursedDps);
    const result = Math.max(cellHeight, minRecursedDps);
    if (depth === 0) {
      cache[cacheKey] = result;
    }
    return result;
  }

  // creative spillage points matrix
  const restrictiveBoundaries = new Array(heightMap.length)
    .fill()
    .map(() => new Array(heightMap[0].length));
  // calculate the spillage points that can be reached from every cell
  for (let rowNumber = 0; rowNumber < heightMap.length; rowNumber++) {
    for (let colNumber = 0; colNumber < heightMap[0].length; colNumber++) {
      restrictiveBoundaries[rowNumber][colNumber] = dp(
        rowNumber,
        colNumber,
        new Set(),
        0
      );
    }
  }

  // calcualte the total water
  let totalWater = 0;
  for (let rowNumber = 0; rowNumber < heightMap.length; rowNumber++) {
    for (let colNumber = 0; colNumber < heightMap[0].length; colNumber++) {
      const cellHeight = heightMap[rowNumber][colNumber];
      const restrictiveBoundary = restrictiveBoundaries[rowNumber][colNumber];
      if (cellHeight < restrictiveBoundary) {
        totalWater += restrictiveBoundary - cellHeight;
      }
    }
  }
  return totalWater;
};

const heightMap = [
  [9, 9, 9, 9, 9, 9, 8, 9, 9, 9, 9],
  [9, 0, 0, 0, 0, 0, 1, 0, 0, 0, 9],
  [9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9],
  [9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9],
  [9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9],
];

const x = Date.now();

console.log(trapRainWater(heightMap));

const y = Date.now();

console.log(y - x);
