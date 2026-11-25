class Solution:
    def deckRevealedIncreasing(self, deck):
        s = sorted(deck)
        n = len(deck)

        res = [None] * n
        orig = deque(range(n))
        for card in s:
            res[orig.popleft()] = card
            if orig:
                orig.append(orig.popleft())

        return res