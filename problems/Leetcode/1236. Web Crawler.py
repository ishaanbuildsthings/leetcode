# """
# This is HtmlParser's API interface.
# You should not implement it, or speculate about its implementation
# """
#class HtmlParser(object):
#    def getUrls(self, url):
#        """
#        :type url: str
#        :rtype List[str]
#        """

class Solution:
    def crawl(self, startUrl: str, htmlParser: 'HtmlParser') -> List[str]:

        desired = startUrl[7:].split('/')[0]
        
        seen = set()

        def dfs(url):
            seen.add(url)
            for adjUrl in htmlParser.getUrls(url):
                if adjUrl in seen:
                    continue
                if adjUrl[7:].split('/')[0] != desired:
                    continue
                dfs(adjUrl)
        
        dfs(startUrl)

        return list(seen)