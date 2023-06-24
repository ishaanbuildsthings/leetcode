/**
 * @param {number} x
 * @param {number} y
 * @param {number} z
 * @return {number}
 */
var longestString = function (x, y, z) {
  /*
    when we place AA, we must place a BB on the right, and either a BB on the left or an AB on the left

    say we start by placing one AA, then on the right we place a BB

    on the right of BB, we place either AA, or AB, whichever we have more of

    on the right of AB, we place AB or AA, whichever we have more of
    */

  let result1 = 0;
  if (x > 0) {
    result1 = getResult("AA", "AA", x, y, z);
  }

  let result2 = 0;
  if (y > 0) {
    result2 = getResult("BB", "BB", x, y, z);
  }

  let result3 = 0;
  if (z > 0) {
    result3 = getResult("AB", "AB", x, y, z);
  }

  return Math.max(result1, result2, result3);

  function getResult(leftmost, rightmost, x, y, z) {
    let result = 2;
    while (true) {
      let changeMade = false;
      if (rightmost === "AA") {
        if (y > 0) {
          rightmost = "BB";
          y--;
          result += 2;
          changeMade = true;
        }
      }

      if (rightmost === "AB") {
        if (x > 0) {
          rightmost = "AA";
          x--;
          result += 2;
          changeMade = true;
        }
      }

      if (rightmost === "BB") {
        // equal or more AB than AA
        if (z > 0 && z > y) {
          z--;
          changeMade = true;
          result += 2;
          rightMost = "AB";
        }

        // more AA than AB
        if (x > 0 && x > z) {
          x--;
          changeMade = true;
          result += 2;
          rightMost = "AA";
        }
      }

      // ______________

      if (leftmost === "AB") {
        // equal or more BB than AB
        if (y > 0 && y > x) {
          y--;
          result += 2;
          changeMade = true;
          leftMost = "BB";
        }

        // more AB than BB
        if (z > y && z > 0) {
          z--;
          changeMade = true;
          result += 2;
          leftMost = "AB";
        }
      }

      if (leftmost === "BB") {
        if (x > 0) {
          leftmost = "AA";
          result += 2;
          changeMade = true;
        }
      }

      // we can put BB or AB on the left
      if (leftmost === "AA") {
        // more BB than AB
        if (y > 0 && y > z) {
          y--;
          changeMade = true;
          result += 2;
          leftMost = "BB";
        }

        // equal or more AB than BB
        if (z > 0 && z >= y) {
          z--;
          changeMade = true;
          result += 2;
          leftMost = "AB";
        }
      }

      if (!changeMade) {
        break;
      }
    }
    return result;
  }
};
