class Solution:
    def expressiveWords(self, s: str, words: List[str]) -> int:
        def make(s):
            groups = []
            size = 0
            n = len(s)
            for i in range(n):
                if i == 0:
                    size += 1
                else:
                    if s[i - 1] == s[i]:
                        size += 1
                    else:
                        groups.append((s[i - 1], size))
                        size = 1
            groups.append((s[-1], size))
            return groups
        
        sgroup = make(s)

        res = 0

        for w in words:
            wgroup = make(w)
            if len(wgroup) != len(sgroup):
                continue
            failFound = False
            for i in range(len(wgroup)):
                if wgroup[i][0] != sgroup[i][0]:
                    failFound = True
                    break
                if wgroup[i][1] > sgroup[i][1]:
                    failFound = True
                    break
                if wgroup[i][1] == 1 and sgroup[i][1] == 2:
                    failFound = True
                    break
            if failFound:
                continue
            res += 1
        
        return res