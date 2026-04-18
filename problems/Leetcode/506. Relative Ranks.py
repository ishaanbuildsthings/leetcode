class Solution:
    def findRelativeRanks(self, score: List[int]) -> List[str]:
        sortedScores = sorted(score, reverse=True)

        scoreToRank = {
            sortedScores[i] : i for i in range(len(sortedScores))
        }

        return [
            "Gold Medal" if scoreToRank[score[i]] == 0 else
            "Silver Medal" if scoreToRank[score[i]] == 1 else
            "Bronze Medal" if scoreToRank[score[i]] == 2 else
            str(scoreToRank[score[i]] + 1) for i in range(len(score))
        ]

        