# template by: https://github.com/agrawalishaan/leetcode
class P:
    def __init__():
        pass

    def printMat(self, matrix):
        print('\n'.join(['\t'.join([str(cell) for cell in row]) for row in matrix]))

    def printNestedDefaultDict(self, nestedDict):
        for key, innerDict in nestedDict.items():
            print(f"{key}: ", end="")
            innerMap = {innerKey: (innerVal if innerVal != float('inf') else 'inf') for innerKey, innerVal in innerDict.items()}
            print(innerMap)



