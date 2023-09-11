# https://leetcode.com/problems/design-a-text-editor/
# Difficulty: Hard
# Tags: linked list

# Problem
# Design a text editor with a cursor that can do the following:

# Add text to where the cursor is.
# Delete text from where the cursor is (simulating the backspace key).
# Move the cursor either left or right.
# When deleting text, only characters to the left of the cursor will be deleted. The cursor will also remain within the actual text and cannot be moved beyond it. More formally, we have that 0 <= cursor.position <= currentText.length always holds.

# Implement the TextEditor class:

# TextEditor() Initializes the object with empty text.
# void addText(string text) Appends text to where the cursor is. The cursor ends to the right of text.
# int deleteText(int k) Deletes k characters to the left of the cursor. Returns the number of characters actually deleted.
# string cursorLeft(int k) Moves the cursor to the left k times. Returns the last min(10, len) characters to the left of the cursor, where len is the number of characters to the left of the cursor.
# string cursorRight(int k) Moves the cursor to the right k times. Returns the last min(10, len) characters to the left of the cursor, where len is the number of characters to the left of the cursor.

# Solution
# Use a doubly linked list, which lets us delete from the middle in constant time. We take n space to store the current characters, moving the cursor takes steps time. Deleting is constant, adding is the length of the text.

class DoublyLinkedList:
    def __init__(self):
        self.left = ListNode()
        self.right = ListNode()
        self.left.next = self.right
        self.right.prev = self.left
    def __repr__(self):
        nodes = []
        current = self.left
        while current:
            nodes.append(current.get_val())
            current = current.next
        return "".join(nodes)

class ListNode:
    def __init__(self, val=None):
        self.val = val
        self.next = None
        self.prev = None
    def __repr__(self):
        return f"({self.val}) prev: {self.prev}"
    def get_val(self):
        return f'{self.val}'

class TextEditor:

    def __init__(self):
        self.dll = DoublyLinkedList()
        self.pointer = self.dll.right # pointer is always to the right of some character

    def addText(self, text: str) -> None:
        for char in text:
            new_node = ListNode(char)
            self.pointer.prev.next = new_node
            new_node.prev = self.pointer.prev
            self.pointer.prev = new_node
            new_node.next = self.pointer


    def deleteText(self, k: int) -> int:
        deleted = 0
        for _ in range(k):
            if self.pointer.prev and self.pointer.prev != self.dll.left:
                two_prev = self.pointer.prev.prev
                self.pointer.prev = two_prev
                two_prev.next = self.pointer
                deleted += 1
            else:
                break
        return deleted


    def cursorLeft(self, k: int) -> str:
        for i in range (k):
            if self.pointer.prev != self.dll.left:
                self.pointer = self.pointer.prev
            else:
                break
        on_left_rev = []
        new_pointer = self.pointer
        for i in range(10):
            if new_pointer.prev != self.dll.left:
                on_left_rev.append(new_pointer.prev.val)
                new_pointer = new_pointer.prev
            else:
                break
        return ''.join(on_left_rev[::-1])

    def cursorRight(self, k: int) -> str:
        for i in range(k):
            if self.pointer.next:
                self.pointer = self.pointer.next
            else:
                break
        on_left_rev = []
        new_pointer = self.pointer
        for i in range(10):
            if new_pointer.prev != self.dll.left:
                on_left_rev.append(new_pointer.prev.val)
                new_pointer = new_pointer.prev
            else:
                break
        return ''.join(on_left_rev[::-1])


# Your TextEditor object will be instantiated and called as such:
# obj = TextEditor()
# obj.addText(text)
# param_2 = obj.deleteText(k)
# param_3 = obj.cursorLeft(k)
# param_4 = obj.cursorRight(k)