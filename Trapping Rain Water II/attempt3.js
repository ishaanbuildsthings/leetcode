var trapRainWater = function (heightMap) {
  const cache = {}; // maps dp calls to their outputs

  function dp(rowCoordinate, colCoordinate, visitedCells, depth) {
    const cacheKey = JSON.stringify([rowCoordinate, colCoordinate]);
    if (cacheKey in cache) {
      return cache[cacheKey];
    }

    const cellHeight = heightMap[rowCoordinate][colCoordinate];

    if (
      rowCoordinate === 0 ||
      rowCoordinate === heightMap.length - 1 ||
      colCoordinate === 0 ||
      colCoordinate === heightMap[0].length - 1
    ) {
      cache[cacheKey] = [cellHeight, new Set()];
      return cache[cacheKey];
    }

    const neighborCoords = [
      [rowCoordinate - 1, colCoordinate], // top
      [rowCoordinate, colCoordinate + 1], // right
      [rowCoordinate, colCoordinate - 1], // left
      [rowCoordinate + 1, colCoordinate], // bottom
    ];

    const neighborCoordsFiltered = neighborCoords.filter(
      (coords) => !visitedCells.has(JSON.stringify(coords))
    );

    visitedCells.add(JSON.stringify([rowCoordinate, colCoordinate]));

    const children = new Set();

    const recursedDps = neighborCoordsFiltered.map((coords) => {
      const [result, childCoords] = dp(
        coords[0],
        coords[1],
        visitedCells,
        depth + 1
      );
      for (const childCoord of childCoords) {
        children.add(childCoord);
      }
      children.add(JSON.stringify(coords));
      return result;
    });

    const minRecursedDps = Math.min(...recursedDps);
    const result = Math.max(cellHeight, minRecursedDps);

    if (cellHeight > minRecursedDps) {
      for (const child of children) {
        visitedCells.delete(child);
      }
    }

    if (depth === 0) {
      cache[cacheKey] = [result, children];
    }

    return [result, children];
  }

  const restrictiveBoundaries = new Array(heightMap.length)
    .fill()
    .map(() => new Array(heightMap[0].length));

  for (let rowNumber = 0; rowNumber < heightMap.length; rowNumber++) {
    for (let colNumber = 0; colNumber < heightMap[0].length; colNumber++) {
      restrictiveBoundaries[rowNumber][colNumber] = dp(
        rowNumber,
        colNumber,
        new Set(),
        0
      )[0];
    }
  }

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

trapRainWater(heightMap);

const y = Date.now();

console.log(y - x);
