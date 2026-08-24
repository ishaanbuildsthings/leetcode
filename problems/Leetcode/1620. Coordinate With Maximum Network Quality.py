class Solution:
    def bestCoordinate(self, towers: List[List[int]], radius: int) -> List[int]:
        resX, resY = None, None
        resQuality = -1
        height = max(tower[1] for tower in towers) + 1
        width = max(tower[0] for tower in towers) + 1
        for r in range(height):
            for c in range(width):
                x = c
                y = height - r - 1
                totQuality = 0
                for tx, ty, tq in towers:
                    dist = math.sqrt(abs(tx-x)**2+abs(ty-y)**2)
                    q = math.floor(tq / (1 + dist))
                    if dist <= radius:
                        totQuality += q

                if totQuality > resQuality:
                    resX, resY = x, y
                    resQuality = totQuality
                elif totQuality == resQuality:
                    if (x, y) < (resX, resY):
                        resX, resY = x, y
                    
        return [resX, resY]