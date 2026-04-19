var lengthLongestPath = function (input) {
    const dirsAndFiles = input.split("\n");
  
    const stack = [];
    let totalCharacterCount = 0;
    let result = 0;
  
    for (const dirFile of dirsAndFiles) {
      const tabCount = getTabCount(dirFile);
      const actualTabCount =
        tabCount === 1 && dirFile.startsWith("    ") ? 4 : tabCount;
  
      // Handle directories
      while (stack.length > 0 && stack[stack.length - 1][0] >= tabCount) {
        const poppedTuple = stack.pop();
        totalCharacterCount -= poppedTuple[1];
      }
  
      const contentLength = dirFile.length - actualTabCount;
  
      // Handle files
      if (isFile(dirFile)) {
        const numberOfSlashes = stack.length;
        const totalCharCount =
          contentLength + totalCharacterCount + numberOfSlashes;
        result = Math.max(result, totalCharCount);
      } else {
        // Handle directories
        stack.push([tabCount, contentLength]);
        totalCharacterCount += contentLength;
      }
    }
  
    return result;
  };
  
  function getTabCount(s) {
    if (s.slice(0, 4) === "    ") return 1; // Use integer 1 instead of array [1]
    let tabCount = 0;
    for (let i = 0; i < s.length; i++) {
      if (s[i] === "\t") {
        tabCount++;
      } else {
        break;
      }
    }
    return tabCount;
  }
  
  function isFile(s) {
    return s.indexOf(".") !== -1;
  }