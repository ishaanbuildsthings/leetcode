#include <bits/stdc++.h>
using namespace std;

int main() {
    bitset<8> a;                  // 00000000
    bitset<8> b(42);              // 00101010  (from an integer)
    bitset<8> c("11001010");      // 11001010  (leftmost char is the HIGH bit)

    // --- single bits ---
    a[0] = 1;                     // 00000001
    a.set(3);                     // 00001001
    a.set(5, true);               // 00101001
    a.reset(0);                   // 00101000
    a.flip(1);                    // 00101010
    cout << a.test(3) << '\n';    // 1
    cout << a[7] << '\n';         // 0

    // --- whole set ---
    bitset<8> d;
    d.set();                      // 11111111
    d.flip();                     // 00000000
    d.reset();                    // 00000000

    // --- bitwise ---
    cout << (b & c) << '\n';      // 00001010
    cout << (b | c) << '\n';      // 11101010
    cout << (b ^ c) << '\n';      // 11100000
    cout << (~b)    << '\n';      // 11010101
    bitset<8> e = b;
    e |= c;                       // 11101010
    e &= b;                       // 00101010
    e ^= b;                       // 00000000

    // --- shifts ---
    cout << (b << 2) << '\n';     // 10101000
    cout << (b >> 3) << '\n';     // 00000101

    // --- queries ---
    cout << b.count() << '\n';    // 3
    cout << b.any()   << '\n';    // 1
    cout << b.none()  << '\n';    // 0
    cout << b.all()   << '\n';    // 0
    cout << b.size()  << '\n';    // 8

    // --- comparison ---
    cout << (b == c) << '\n';     // 0
    cout << (b != c) << '\n';     // 1

    // --- conversion / output ---
    cout << b.to_ulong()  << '\n';   // 42
    cout << b.to_string() << '\n';   // 00101010
    cout << b << '\n';               // 00101010

    // --- GCC-only: iterate set bits ---
    for (size_t i = b._Find_first(); i < b.size(); i = b._Find_next(i)) {
        cout << i << ' ';         // 1 3 5
    }
    cout << '\n';
}