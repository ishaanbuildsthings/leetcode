class Solution:
    def badSensor(self, sensor1: List[int], sensor2: List[int]) -> int:
        # exact same, no defect
        if sensor1 == sensor2:
            return -1
        firstWrong = None
        for i in range(len(sensor1)):
            if sensor1[i] != sensor2[i]:
                firstWrong = i
                break
        # last datapoint was dropped, cannot tell
        if firstWrong == len(sensor1) - 1:
            return -1
        
        suff1 = sensor1[firstWrong:]
        suff2 = sensor2[firstWrong:]

        A = suff1[:-1] == suff2[1:]
        B = suff2[:-1] == suff1[1:]

        if A and B:
            return -1
        
        if A:
            return 1
        if B:
            return 2

        return -1