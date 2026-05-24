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