class Solution:
    def alertNames(self, keyName: List[str], keyTime: List[str]) -> List[str]:
        mp = defaultdict(deque)

        def val(time):
            h, m = map(int, time.split(':'))
            return 60 * h + m
        
        z = sorted(zip(keyName, keyTime), key=lambda x : val(x[1]))

        res = set()

        for person, time in z:
            mp[person].append(val(time))
            while mp[person][0] + 60 < mp[person][-1]:
                mp[person].popleft()
            if len(mp[person]) >= 3:
                res.add(person)

        return sorted(res)

        