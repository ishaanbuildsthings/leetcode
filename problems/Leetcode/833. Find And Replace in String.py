class Solution:
    def findReplaceString(self, s: str, indices: List[int], sources: List[str], targets: List[str]) -> str:
        z = [(indices[i], sources[i], targets[i]) for i in range(len(indices))]
        z.sort()

        res = []
        j = 0 # string pointer
        for idx, src, target in z:
            if s[idx:idx+len(src)] != src:
                continue
            while j < idx:
                res.append(s[j])
                j += 1
            res.append(target)
            j = idx + len(src)
        while j < len(s):
            res.append(s[j])
            j += 1
        return ''.join(res)