# n=1 -> 1
# n=2 -> 1 + (1 + 2)
# n=3 -> 1 + (1 + 2) + (1 + 2 + 3)
def tetrahedralNumber(n):
    return n * (n + 1) * (n + 2) // 6

# Sum of "super" triangle numbers in ascending order, so this would be (1+2+3) + (2+3+4) + (3+4+5). In this example, start=1, size=3
def superTriangleSumAscending(start, size):
    firstTerm = start * (size * (size + 1) // 2)
    secondTerm = ((size * (size + 1) * (2 * size + 1)) // 6) - ((size * (size + 1)) // 2)
    secondTerm //= 2
    return firstTerm + secondTerm

# Sum of "super" triangle numbers in descending order, so this would be (7) + (7+6) + (7+6+5). In this example, start=7, size=3
def superTriangleSumDescending(start, size):
  firstTerm = start * (size * (size + 1) // 2)
  secondTerm = (size * (size + 1) * (size - 1)) // 6
  return firstTerm - secondTerm