/**
 * @param {number} rowsCount
 * @param {number} colsCount
 * @return {Array<Array<number>>}
 */
Array.prototype.snail = function(rowsCount, colsCount) {
    // this is original obj
    if (rowsCount * colsCount !== this.length) {
        return [];
    }
    
    const mat = Array.from({ length: rowsCount }, () => new Array(colsCount));
    
    for (let i = 0; i < this.length; i++) {
        const col = Math.floor(i / rowsCount);
        let row;
        if (col % 2) {
            row = rowsCount - 1 - (i % rowsCount);
        } else {
            row = i % rowsCount;
        }
        mat[row][col] = this[i];
    }
    return mat;
}

/**
 * const arr = [1,2,3,4];
 * arr.snail(1,4); // [[1,2,3,4]]
 */