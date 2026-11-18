class Solution:
    def countDays(self, days: int, meetings: List[List[int]]) -> int:
        # 1) events, track how many open we have

        """
        Think of each event as the moment something changes, not as a day. A meeting from day 5 to day 7 still occupies all of day 7, so day 7 isn’t where anything changes. The change happens when day 8 begins, the first day the meeting is gone. So the closing event goes at 8.


        day:      5    6    7    8
        meeting:  ■    ■    ■    ·
                ↑              ↑
                +1 here       -1 here (first free day)
        """

        # events = []
        # for l, r in meetings:
        #     events.append((l, 1))
        #     events.append((r + 1, -1))
        # events.sort()
        # res = 0
        # curr = 0
        # for i in range(len(events)):
        #     prevTime = events[i - 1][0] if i else 0
        #     idx, payload = events[i]
        #     width = idx - prevTime
        #     if curr:
        #         res += width
        #     curr += payload
        # return days - res



        # 2) coordinate compress sweep line
        # times = set()
        # for l, r in meetings:
        #     times.add(l)
        #     times.add(r + 1)
        # times = sorted(times)
        # compressed = {times[i]:i for i in range(len(times))}

        # sweep = [0] * len(times)
        # for l, r in meetings:
        #     c1 = compressed[l]
        #     sweep[c1] += 1
        #     c2 = compressed[r + 1]
        #     sweep[c2] -= 1

        # res = 0
        # curr = 0
        # for i in range(len(times) - 1):
        #     curr += sweep[i]
        #     if curr:
        #         res += times[i + 1] - times[i]
        # return days - res


        # 3) merge intervals
        # meetings.sort()
        # prevL, prevR = meetings[0]
        # merged = []
        # res = 0
        # for i in range(1, len(meetings)):
        #     l, r = meetings[i]
        #     if l > prevR:
        #         merged.append([prevL, prevR])
        #         prevL, prevR = l, r
        #         continue
        #     prevR = max(prevR, r)
        # merged.append([prevL, prevR])
        # tot = sum(tup[1] - tup[0] + 1 for tup in merged)
        # return days - tot


        # 4) sparse seg tree
        
