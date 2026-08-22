class Solution:
    def minMeetingRooms(self, intervals: List[List[int]]) -> int:
        # events = []
        # for start, end in intervals:
        #     events.append([start, 1])
        #     events.append([end, -1])
        # events.sort()
        # curr = res = 0
        # for _, diff in events:
        #     curr += diff
        #     res = max(res, curr)
        # return res

        s = sorted([tup[0] for tup in intervals])
        e = sorted([tup[1] for tup in intervals])
        i = j = res = curr = 0
        while i < len(s):
            if s[i] < e[j]:
                curr += 1
                res = max(curr, res)
                i += 1
                continue
            j += 1
            curr -= 1
        return res
            