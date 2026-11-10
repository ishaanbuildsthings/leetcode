"""Which C++ compiler the tests use, and whether it can sanitize.

    python3 find_compiler.py    # prints the compiler (for shell scripts)

CXX wins if set, else the newest g++-15 ... g++-11, else g++. Templates need bits/stdc++.h, which macOS's own g++ (really
clang) doesn't have. Some GCC builds also can't link the sanitizers; sanitize_flags() returns [] for those.
"""
import functools
import os
import shutil
import subprocess
import tempfile


@functools.lru_cache(maxsize=None)
def cxx():
    if os.environ.get("CXX"):
        return os.environ["CXX"]
    for candidate in [f"g++-{v}" for v in range(15, 10, -1)] + ["g++"]:
        if shutil.which(candidate):
            return candidate
    raise RuntimeError("no C++ compiler found: set CXX")


@functools.lru_cache(maxsize=None)
def sanitize_flags():
    flags = ["-fsanitize=address,undefined", "-fno-sanitize-recover=all"]
    with tempfile.TemporaryDirectory() as tmp:
        src, exe = os.path.join(tmp, "t.cpp"), os.path.join(tmp, "t")
        open(src, "w").write("#include <bits/stdc++.h>\nint main() { return 0; }\n")
        built = subprocess.run([cxx(), "-std=c++17", *flags, "-o", exe, src], capture_output=True).returncode == 0
        if built and subprocess.run([exe], capture_output=True).returncode == 0:
            return flags
    return []


if __name__ == "__main__":
    print(cxx())
