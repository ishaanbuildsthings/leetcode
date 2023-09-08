# https://leetcode.com/problems/generate-random-point-in-a-circle/description/
# Difficulty: Medium
# Tags: Math and Geometry

# Problem
# Given the radius and the position of the center of a circle, implement the function randPoint which generates a uniform random point inside the circle.

# Implement the Solution class:

# Solution(double radius, double x_center, double y_center) initializes the object with the radius of the circle radius and the position of the center (x_center, y_center).
# randPoint() returns a random point inside the circle. A point on the circumference of the circle is considered to be in the circle. The answer is returned as an array [x, y].

# Solution, O(1) average time and space, O(infinity) worst case time
# Generate random points inside the square until one is in the circle.

class Solution:

    def __init__(self, radius: float, x_center: float, y_center: float):
        self.radius = radius
        self.x_center = x_center
        self.y_center = y_center

    def randPoint(self) -> List[float]:
        while True:
            # generate a random x coordinate within the square
            rand_x = random.uniform(self.x_center - self.radius, self.x_center + self.radius)
            rand_y = random.uniform(self.y_center - self.radius, self.y_center + self.radius)
            x_diff = abs(rand_x - self.x_center)
            y_diff = abs(rand_y - self.y_center)
            distance = math.sqrt(x_diff**2 + y_diff**2)
            if distance < self.radius:
                return [rand_x, rand_y]



# Your Solution object will be instantiated and called as such:
# obj = Solution(radius, x_center, y_center)
# param_1 = obj.randPoint()