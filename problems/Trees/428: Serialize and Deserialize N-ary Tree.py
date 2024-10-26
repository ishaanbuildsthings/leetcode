# https://leetcode.com/problems/serialize-and-deserialize-n-ary-tree/description/
# difficulty: hard
# tags: trees

# Problem
# Serialization is the process of converting a data structure or object into a sequence of bits so that it can be stored in a file or memory buffer, or transmitted across a network connection link to be reconstructed later in the same or another computer environment.

# Design an algorithm to serialize and deserialize an N-ary tree. An N-ary tree is a rooted tree in which each node has no more than N children. There is no restriction on how your serialization/deserialization algorithm should work. You just need to ensure that an N-ary tree can be serialized to a string and this string can be deserialized to the original tree structure.

# For example, you may serialize the following 3-ary tree

# For example, the above tree may be serialized as [1,null,2,3,4,5,null,null,6,7,null,8,null,9,10,null,null,11,null,12,null,13,null,null,14].

# You do not necessarily need to follow the above-suggested formats, there are many more different formats that work so please be creative and come up with different approaches yourself.

# Solution
# At first I tried serializing each tree as something like { root value : [children nodes with their own serializations] } but I got a memory limit error. I believe with stringifying it it recursively calls too much, we could manually construct a string with delimeters instead. But I opted for a parent reference strategy. Each node serializes its parent idx, its own idx, and its value. Takes n time and space to serialize and n time to deserialize.


"""
# Definition for a Node.
class Node(object):
    def __init__(self, val=None, children=[]):
        self.val = val
        self.children = children
"""

class Codec:
    def serialize(self, root: 'Node') -> str:
        """Encodes a tree to a single string.

        :type root: Node
        :rtype: str
        """
        # # edge case
        # if not root:
        #     return None

        # serialized = {root.val : []}
        # for child in root.children:
        #     serialized[root.val].append(self.serialize(child))
        # print(f'serialized is {serialized}')
        # return json.dumps(serialized)

        # edge case
        if not root:
            return None

        nodes = [] # stores a list of nodeIdx|parentNodeIdx|value

        idx = 0

        def dfs(node, parentIdx):
            nonlocal idx

            nodeIdx = idx
            idx += 1

            if parentIdx == None:
                nodes.append(f'{nodeIdx}|n|{node.val}')
            else:
                nodes.append(f'{nodeIdx}|{parentIdx}|{node.val}')
            for child in node.children:
                dfs(child, nodeIdx)
        dfs(root, None)
        return json.dumps(nodes)



    def deserialize(self, data: str) -> 'Node':
        """Decodes your encoded data to tree.

        :type data: str
        :rtype: Node
        """
        # # edge case
        # if data == None:
        #     return None

        # # print(f'data is {data}')
        # parsed = json.loads(data)
        # # print(f'parsed is {parsed}')

        # root = Node(list(parsed.keys())[0])
        # for subObject in list(parsed[list(parsed.keys())[0]]):
        #     root.children.append(self.deserialize(subObject))
        # return root

        # edge case
        if data == None:
            return None

        parsed = json.loads(data)

        dummySuperRoot = Node(None)

        nodeMap = {'n' : dummySuperRoot } # maps a nodeIdx to the actual node, n is an edge value for the parent of the root
        for node in parsed:
            nodeIdx, parentIdx, nodeVal = node.split('|')
            newNode = Node(nodeVal)
            nodeMap[nodeIdx] = newNode
            parentNode = nodeMap[parentIdx]
            parentNode.children.append(newNode)

        return dummySuperRoot.children[0]


# Your Codec object will be instantiated and called as such:
# codec = Codec()
# codec.deserialize(codec.serialize(root))