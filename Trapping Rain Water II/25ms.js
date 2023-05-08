function findCells(
  rowCoordinate,
  colCoordinate,
  frozen,
  childrenCells,
  numRows,
  numCols
) {
  // add the cell
  frozen.add(JSON.stringify([rowCoordinate, colCoordinate]));

  // if we are at an edge, terminate
  if (
    rowCoordinate === 0 ||
    colCoordinate === 0 ||
    rowCoordinate === numRows - 1 ||
    colCoordinate === numCols - 1
  )
    return;

  const neighborCoords = [
    [rowCoordinate - 1, colCoordinate], // top
    [rowCoordinate, colCoordinate + 1], // right
    [rowCoordinate, colCoordinate - 1], // left
    [rowCoordinate + 1, colCoordinate], // bottom
  ];

  // remove visited cells so we don't visit those
  const neighborCoordsFiltered = neighborCoords.filter(
    (coords) => !frozen.has(JSON.stringify(coords))
  );
  // console.log(`filtered neighbor coords inside findCells: ${JSON.stringify(neighborCoordsFiltered)}`);

  for (const coords of neighborCoordsFiltered) {
    childrenCells.push(JSON.stringify(coords));
  }

  for (const coords of neighborCoordsFiltered) {
    findCells(coords[0], coords[1], frozen, childrenCells, numRows, numCols);
  }
}

/**
 * @param {number[][]} heightMap
 * @return {number}
 */
function trapRainWater(heightMap) {
  const cache = {}; // maps dp calls to their outputs

  function dp(rowCoordinate, colCoordinate, visitedCells, depth) {
    // add cell for future calls
    visitedCells.add(JSON.stringify([rowCoordinate, colCoordinate]));

    // caching, currently only works for borders and top level calls
    const cacheKey = JSON.stringify([rowCoordinate, colCoordinate]);
    if (cacheKey in cache) {
      return cache[cacheKey];
    }

    const cellHeight = heightMap[rowCoordinate][colCoordinate];

    // if we are at a boundary of the matrix, we will spill over the edge, immediately return the cells height as the boundary
    if (
      rowCoordinate === 0 ||
      rowCoordinate === heightMap.length - 1 ||
      colCoordinate === 0 ||
      colCoordinate === heightMap[0].length - 1
    ) {
      // it is always okay to cache a boundary
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
    const neighborCoordsFiltered = neighborCoords.filter(
      (coords) => !visitedCells.has(JSON.stringify(coords))
    );

    // used for potential findCells call
    const frozen = new Set(visitedCells);

    const recursedDps = neighborCoordsFiltered.map((coords) =>
      dp(coords[0], coords[1], visitedCells, depth + 1)
    );
    const minRecursedDps = Math.min(...recursedDps);
    const result = Math.max(cellHeight, minRecursedDps);
    // it is always okay to cache a root level call
    if (depth === 0) {
      cache[cacheKey] = result;
    }

    // unvisit the cells
    if (cellHeight > minRecursedDps) {
      // console.log('cell height can be used as the boundary...');
      // console.log(`coords: ${rowCoordinate},${colCoordinate} value: ${heightMap[rowCoordinate][colCoordinate]}`);
      const childrenCells = [];
      findCells(
        rowCoordinate,
        colCoordinate,
        frozen,
        childrenCells,
        heightMap.length,
        heightMap[0].length
      );
      // console.log(childrenCells);
      // console.log(visitedCells)
      for (const childrenCell of childrenCells) {
        // console.log(`i am children: ${childrenCell}`);
        // console.log(visitedCells.has((childrenCell)))
        visitedCells.delete(childrenCell);
      }
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

  // console.log(restrictiveBoundaries);

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
}

const heightMap = [
  [9, 9, 9, 9, 9, 9, 8, 9, 9, 9, 9],
  [9, 0, 0, 0, 0, 0, 1, 0, 0, 0, 9],
  [9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9],
  [9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9],
  [9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9],
];

const x = Date.now();

trapRainWater(heightMap);
// console.log(trapRainWater(heightMap));

const y = Date.now();

console.log(y - x);
