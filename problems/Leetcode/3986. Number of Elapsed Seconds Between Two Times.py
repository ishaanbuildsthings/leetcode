class Solution:
    def secondsBetweenTimes(self, startTime: str, endTime: str) -> int:

        h1, m1, s1 = startTime.split(':')
        h1 = int(h1)
        m1 = int(m1)
        s1 = int(s1)

        # print(f'{h1=} {m1=} {s2=}')

        h2, m2, s2 = endTime.split(':')
        h2 = int(h2)
        m2 = int(m2)
        s2 = int(s2)

        tot1 = s1 + (60 * m1) + (3600 * h1)

        tot2 = s2 + (60 * m2) + (3600 * h2)

        print(f'{h2=} {m2=} {s2=}')

        return tot2 - tot1

        