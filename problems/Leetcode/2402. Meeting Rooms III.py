class Solution:
    def mostBooked(self, n: int, meetings: List[List[int]]) -> int:
        
        meetingCounts = [0] * n
        meetings.sort()

        avail = list(range(n))
        pending = [] # holds (time room becomes free, room#)
        time = 0

        for l, r in meetings:
            time = max(time, l)
            # put now available rooms in use
            while pending and pending[0][0] <= time:
                timeFree, roomNum = heapq.heappop(pending)
                heapq.heappush(avail, roomNum)
            
            # if nothing is free then free up the first room
            if not avail:
                firstTime, roomNum = heapq.heappop(pending)
                time = firstTime
                heapq.heappush(avail, roomNum)
            
            usedRoom = heapq.heappop(avail)
            meetingCounts[usedRoom] += 1
            duration = r - l
            heapq.heappush(pending, (time + duration, usedRoom))
        
        return meetingCounts.index(max(meetingCounts))
                
            