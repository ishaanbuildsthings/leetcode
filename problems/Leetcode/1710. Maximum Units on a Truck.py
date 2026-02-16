class Solution:
    def maximumUnits(self, boxTypes: List[List[int]], truckSize: int) -> int:
        # can bucket sort
        boxTypes.sort(key=lambda tup: tup[-1], reverse=True)
        res = 0
        remain = truckSize
        
        for numberOfBoxes, unitsPerBox in boxTypes:
            if remain == 0:
                break
            take = min(remain, numberOfBoxes)
            res += take * unitsPerBox
            remain -= take
        
        return res