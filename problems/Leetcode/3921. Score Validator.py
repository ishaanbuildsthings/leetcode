class Solution:
    def scoreValidator(self, events: list[str]) -> list[int]:
        score = 0
        counter = 0
        for v in events:
            if v.isdigit():
                score += int(v)
                continue
            if v == 'W':
                counter += 1
                if counter == 10:
                    break
            if v == 'WD':
                score += 1
                continue
            if v == 'NB':
                score += 1

        return [score, counter]