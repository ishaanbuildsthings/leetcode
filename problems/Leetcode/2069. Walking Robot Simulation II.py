class Robot:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.pos = 0
        self.perimeter = (2 * (width - 1)) + (2 * (height - 1))
        self.hasMoved = False

    def step(self, num):
        self.pos += num
        self.pos %= self.perimeter
        self.hasMoved = True

    def getPos(self):
        x = self.pos
        w, h = self.width - 1, self.height - 1
        # we are on the bottom strip
        if x <= w:
            return [x, 0]
        x -= w
        # we are on the right strip
        if x <= h:
            return [w, x]
        # we are on the top strip
        x -= h
        if x <= w:
            return [w - x, h]
        x -= w
        # we are on the left strip
        return [0, h - x]

    def getDir(self):
        # needed bcause later if we are at 0,0 we are facing south
        if not self.hasMoved:
            return "East"
        x = self.pos
        w, h = self.width - 1, self.height - 1
        if x == 0:
            return "South"
        if x <= w:
            return "East"
        x -= w
        if x <= h:
            return "North"
        x -= h
        if x <= w:
            return "West"
        return "South"