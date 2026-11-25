class Solution:
    def bagOfTokensScore(self, tokens: list[int], power: int) -> int:
        res = 0
        score = 0
        d = deque(sorted(tokens))
        while d:
            if power >= d[0]:
                lostP = d.popleft()
                power -= lostP
                score += 1
                res = max(res, score)
                continue
            if not score:
                break
            score -= 1
            gainP = d.pop()
            power += gainP
        return res