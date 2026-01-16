// https://leetcode.com/problems/valid-sudoku/description/
// Difficulty: Medium

// Solution
// O(n*m) time and O(n*m) space, or O(1) time and space if we consider a sudoku board to always be 9x9. Iterate over each cell, and add the relevant data to a row hash set, a column hash set, and a box hash set, checking for duplicates.
// We can store 9 rows, and each row could store 9 numbers (though not really, because we would eventually have a collision), so n*m memory. Same with columns, and boxes.

const isValidSudoku = function (board) {
  const rows = new Array(9).fill().map(() => ({})); // each row element contains a mapping of the numbers inside it to their frequencies
  const columns = new Array(9).fill().map(() => ({}));
  const boxes = new Array(9).fill().map(() => ({})); // boxes will be numbered reading left to right and top to bottom

  for (let rowNumber = 0; rowNumber < board.length; rowNumber++) {
    for (let colNumber = 0; colNumber < board[0].length; colNumber++) {
      const number = board[rowNumber][colNumber];
      if (number === ".") continue;

      // check rows
      if (rows[rowNumber][number] === 1) {
        return false;
      }
      rows[rowNumber][number] = 1;

      // check columns
      if (columns[colNumber][number] === 1) {
        return false;
      }
      columns[colNumber][number] = 1;

      // check boxes
      const rowGrouping = Math.floor(rowNumber / 3); // rows 0-3 -> 0, 4-6 -> 1, 7-9 -> 2
      const colGrouping = Math.floor(colNumber / 3); // cols 0-3 -> 0, 4-6 -> 1, 7-9 -> 2
      // if we are in rowGrouping 0, we know we are in boxes 0, 1 or 2
      // if we are in rowGrouping 1, we know we are in boxes 3, 4, or 5, etc
      // our first possible box we could be in, based off of the rowGrouping, is (rowGrouping * 3)
      // the colGrouping then provides an offset to increment by
      const boxNumber = rowGrouping * 3 + colGrouping;
      if (boxes[boxNumber][number] === 1) {
        return false;
      }
      boxes[boxNumber][number] = 1;
    }
  }

  return true;
};
