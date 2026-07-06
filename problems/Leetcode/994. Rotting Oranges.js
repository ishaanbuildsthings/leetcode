/**
 * @param {number[][]} grid
 * @return {number}
 */
var orangesRotting = function(grid) {
    const HEIGHT = grid.length;
    const WIDTH = grid[0].length;

    const visited = new Array(HEIGHT).fill().map(() => new Array(WIDTH).fill(false));

    const deque = []; // fake deque, maintains tuples for coordinates, used in the bfs search
    for (let row = 0; row < HEIGHT; row++) {
        for (let col = 0; col < WIDTH; col++) {
            const cell = grid[row][col];
            if (cell === 2) {
                deque.push([row, col]);
                visited[row][col] = true; // any initial rotted oranges should not be later considered
            }
        }
    }

    let result = 0;

    // while there are rotten oranges we have not yet processed (not considered their neighbors)
    while (deque.length > 0) {
        // do a one-minute phase
        const length = deque.length;
        result++;

        for (let i = 0; i < length; i++) {
            const [row, col] = deque.shift(); // pretend O(1)

            // if we have a rotted orange, we want to make its fresh neighbors rotten, and then add those fresh ones to the queue so that they can rot more in turn

            // right adjacency
            if (col + 1 < WIDTH && grid[row][col + 1] === 1 && !visited[row][col + 1]) {
                visited[row][col + 1] = true;
                grid[row][col + 1] = 2;
                deque.push([row, col + 1]);
            }

            // left adjacency
            if (col - 1 >= 0 && grid[row][col - 1] === 1 && !visited[row][col - 1]) {
                visited[row][col - 1] = true;
                grid[row][col - 1] = 2;
                deque.push([row, col - 1]);
            }

            // top adjacency
            if (row - 1 >= 0 && grid[row - 1][col] === 1 && !visited[row - 1][col]) {
                visited[row - 1][col] = true;
                grid[row - 1][col] = 2;
                deque.push([row - 1, col]);
            }

            // down adjacency
            if (row + 1 < HEIGHT && grid[row + 1][col] === 1 && !visited[row + 1][col]) {
                visited[row + 1][col] = true;
                grid[row + 1][col] = 2;
                deque.push([row + 1, col]);
            }
        }
        
    }
    for (const row of grid) {
        for (const cell of row) {
            if (cell === 1) return -1;
        }
    }

    if (result - 1 === -1) return 0

    return result - 1;

};