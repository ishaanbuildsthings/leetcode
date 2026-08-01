class Solution:
    def maximumTime(self, time: str) -> str:
        # ??
        # ?4+
        # ?3-
        # 0?
        # 1?
        # 2?
        
        ans = list(time)
        hour = time[:2]
        if hour == '??':
            ans[0] = '2'
            ans[1] = '3'
        elif hour[0] == '?':
            if int(hour[1]) >= 4:
                ans[0] = '1'
            else:
                ans[0] = '2'
        elif hour[1] == '?':
            if hour[0] == '2':
                ans[1] = '3'
            else:
                ans[1] = '9'
        
        if ans[3] == '?':
            ans[3] = '5'
        if ans[-1] == '?':
            ans[-1] = '9'
        return ''.join(ans)