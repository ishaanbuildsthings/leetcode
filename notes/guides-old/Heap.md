# Heap

## Clean implementation

My code for 2462 has a good implementation of a heap (back when I used JS!)

## How a heap works:

A heap is implemented as an array. Each element in the heap is smaller than or equal to its children (for a min heap), or vice versa for a max heap. We usually keep the first element of the array as a dummy value to make counting easier, but there is a way to do it without that. If we have the first element is a dummy, then the left child of `arr[i]` is `arr[2*i + 1]`, and the right child is `arr[2*i + 2]`. The parent of the `ith` element is the `(i-1)//2th` element.

A complete tree is one where every level is filled except possibly the last, but the last is being filled left to right. A heap must be a complete tree or we lose the log n time benefit (need to think about why). When we add to the heap, push the element to the end of the array. Then percolate up as long as the element is bigger or smaller than its parent. When we remove from the heap, grab the first element from the heap. Take our last element and substitute it into the front, then percolate down. We cannot just percolate down our root element and then remove it, because we get a hole. If we try to fill this hole with our last element, the heap may no longer be valid.

            7
          /  \
         6    4

         consider this max heap. If we delete 7, then recursively try to fill the hole:


          /\
         6  4

         4
        /
       6

       Then replace the hole with our last heap element:

       4
        \
         6

        We don't have a valid heap anymore (this example is more clear in a bigger heap).


      Instead, we should take the 4, make it the root, then percolate down.

### Heapify

To heapify an array, we start iterating from the last element that does have a child (we could run the algorithm on all elements instead, and just skip over the ones that don't have children). For each element, percolate it down as much as needed. It appears to be n log n time, but you can prove the time is `O(n)` because the initial rows have a smaller height than the later rows. Note this is with sifting down. If we try to heapify something by adding n elements to a heap, and sifting them up as needed, the time complexity becomes `n log n` because the leaf nodes will take worst case log n time. So it is better to start at the leaves, and sift down, than start at the leaves and sift up.

## Tricky scenario for using a min heap vs. a max heap

Imagine we want the k smallest elements in an array. Once way is to maintain a MAX heap of size k. The heap holds our k smallest elements, but is a max heap. Then as we decide if we need to swap an element into the heap, and pop an element from the heap out, we can easily see if our new element is smaller than the biggest element in the heap. This feels counterintuitive since we are using a max heap for the smallest elements! My code for 973 has an example of this.

# Advanced heaps

## Fibonacci heaps

Not used yyet

## Treap

Not used yet

## Randomized heap

Not used yet
