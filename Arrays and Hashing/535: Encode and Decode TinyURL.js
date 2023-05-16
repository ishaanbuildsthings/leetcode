// https://leetcode.com/problems/encode-and-decode-tinyurl/description/
// Difficulty: Medium

// Problem
/*
Simplfied: Create a function that shortens a URL, and a decode function to get the original URL.

Detailed:
TinyURL is a URL shortening service where you enter a URL such as https://leetcode.com/problems/design-tinyurl and it returns a short URL such as http://tinyurl.com/4e9iAk. Design a class to encode a URL and decode a tiny URL.

There is no restriction on how your encode/decode algorithm should work. You just need to ensure that a URL can be encoded to a tiny URL and the tiny URL can be decoded to the original URL.

Implement the Solution class:

Solution() Initializes the object of the system.
String encode(String longUrl) Returns a tiny URL for the given longUrl.
String decode(String shortUrl) Returns the original long URL for the given shortUrl. It is guaranteed that the given shortUrl was encoded by the same object.
*/

// Solution
// O(1) time to encode and O(1) time to encode, O(n) space for the mapping. Technically the time can deteriorate once there are too many collisions, but this is unlikely as there are too many possible combinations.
/*
For the encoding, generate a random alphanumeric 8 digit url, storage the mapping of the tinyurl to the long url. For the decode, lookup the tinyurl in the mapping and return the long url.
*/

// maps tinyurls to their long versions
const mapping = {};
const CHAR_SET =
  "abcdefghijklmnopqrstuvwxyz1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ";

var encode = function (longUrl) {
  let tinyurl = "http://tinyurl.com/";
  let tinyurlSuffix = "";
  let duplicateUrl = true;
  // keep generating urls until we get a unique one
  while (duplicateUrl) {
    // urls can be of length 8
    for (let i = 0; i < 8; i++) {
      const randomCharIndex = Math.floor(Math.random() * CHAR_SET.length);
      const randomChar = CHAR_SET[randomCharIndex];
      tinyurlSuffix += randomChar;
    }
    // if this is a new url, break out of the loop
    if (!(tinyurl + tinyurlSuffix in mapping)) {
      duplicateUrl = false;
    }
    // otherwise reset the suffix and try again
    else {
      tinyurlSuffix = "";
    }
  }
  mapping[tinyurl + tinyurlSuffix] = longUrl;
  return tinyurl + tinyurlSuffix;
};

var decode = function (shortUrl) {
  return mapping[shortUrl];
};

/**
 * Your functions will be called as such:
 * decode(encode(url));
 */
