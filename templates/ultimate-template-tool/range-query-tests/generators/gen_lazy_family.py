"""Regenerate the 32 lazy-tree templates (template.py + template.cpp in each folder).

    python3 gen_lazy_family.py

The family is every 2N iterative lazy tree with node fields from {sum, min, max} and tags from {add, assign,
chmin, chmax}: lazy_common.py lists the variants, names them and writes their headers; lazy_emit.py and
lazy_emit_cpp.py write the Python and C++ bodies. Change the emitters, rerun this, then run
../test_templates.py and ../check_catalog.py (after `npm run gen:range-queries` in site/).
"""
import sys

sys.dont_write_bytecode = True  # keep __pycache__ out of the repo

from lazy_emit import write_py_all  # noqa: E402
from lazy_emit_cpp import write_cpp_all  # noqa: E402

if __name__ == "__main__":
    write_py_all()
    write_cpp_all()
