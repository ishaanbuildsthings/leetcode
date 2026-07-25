class Solution:
    def readBinaryWatch(self, turnedOn: int) -> List[str]:
        hoursToBits = {
            number : number.bit_count() for number in range(12)
        }
        minuteToBits = {
            number : number.bit_count() for number in range(60)
        }
        timeToBits = {}
        for hour in range(12):
            for minute in range(60):
                totalBits = hoursToBits[hour] + minuteToBits[minute]
                time = str(hour) + ':' + (str(minute) if len(str(minute)) == 2 else '0' + str(minute))
                timeToBits[time] = totalBits
        bitsToTime = defaultdict(list)
        for time, bits in timeToBits.items():
            bitsToTime[bits].append(time)
        return bitsToTime[turnedOn]