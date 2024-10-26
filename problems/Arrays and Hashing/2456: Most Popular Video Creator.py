# https://leetcode.com/problems/most-popular-video-creator/
# difficulty: medium

# Solution, O(n) time and space

class Solution:
    def mostPopularCreator(self, creators: List[str], ids: List[str], views: List[int]) -> List[List[str]]:
        creatorToPopularity = defaultdict(int)
        creatorToMostViewedVideo = {} # maps to the index of the array

        for i in range(len(creators)):
            creator = creators[i]
            viewCount = views[i]
            creatorToPopularity[creator] += viewCount

            vidId = ids[i]
            if not creator in creatorToMostViewedVideo:
                creatorToMostViewedVideo[creator] = i
                continue

            mostViews = views[creatorToMostViewedVideo[creator]]
            if viewCount > mostViews:
                creatorToMostViewedVideo[creator] = i
            elif viewCount == mostViews:
                currentStringId = ids[creatorToMostViewedVideo[creator]]
                newStringId = ids[i]
                if newStringId < currentStringId:
                    creatorToMostViewedVideo[creator] = i


        maxPopularity = max(popularity for popularity in creatorToPopularity.values())

        return [
            [creator, ids[creatorToMostViewedVideo[creator]]]
            for creator in creatorToPopularity
            if creatorToPopularity[creator] == maxPopularity
        ]
