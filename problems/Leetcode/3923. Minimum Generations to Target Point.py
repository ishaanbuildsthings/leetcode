class Solution:
    def minGenerations(self, points: List[List[int]], target: List[int]) -> int:
        # 20
        # 40
        # 80

        # target = [100,100,100]


        if target in points:
            return 0

        points = [(x, y, z) for x, y, z in points]


        for generation in range(1, 22):
            npoints = set()
            for i in range(len(points)):
                x1, y1, z1 = points[i]
                for j in range(i + 1, len(points)):
                    x2, y2, z2 = points[j]
                    np = ((x1+x2)//2, (y1+y2)//2, (z1+z2)//2)
                    npoints.add(np)

            if (target[0], target[1], target[2]) in npoints:
                return generation
                
            for p in points:
                npoints.add(p)
                

            points = list(npoints)

        return -1
            