class Solution:
    def eatenApples(self, apples: List[int], days: List[int]) -> int:
        res = 0

        sl = SortedList() # holds (rotsOnDayX)
        mp = {} # maps rotsOnDayX -> count
        for day in range(len(apples)):
            rotDay = day + days[day]
            cnt = apples[day]
            if rotDay not in mp:
                mp[rotDay] = cnt
                sl.add(rotDay)
            else:
                oldV = mp[rotDay]
                nv = oldV + cnt
                mp[rotDay] = nv
                sl.remove(rotDay)
                sl.add(rotDay)
            if day in mp:
                v = mp[day]
                del mp[day]
                sl.remove(day)
            
            if sl:
                res += 1
                poppedRot = sl.pop(0)
                poppedCnt = mp[poppedRot]
                del mp[poppedRot]
                poppedCnt -= 1
                if poppedCnt > 0 and poppedRot > day:
                    sl.add(poppedRot)
                    mp[poppedRot] = poppedCnt
        
        day += 1

        lst = list(sl)
        # holds (rotsOnDayX)
        for rotOnDayX in lst:
            cnt = mp[rotOnDayX]
            take = min(cnt, rotOnDayX - day)
            if take <= 0:
                continue
            res += take
            day += take
        
        return res