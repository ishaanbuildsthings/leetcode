"""Runs every 2D / 3D range query generator.

    python3 gen_all.py             # (re)writes templates/ultimate-template-tool/range-queries-2d
    python3 gen_all.py --check     # writes nothing: exit 1 if any file differs from what the generators make now

Afterwards: python3 ../test_templates_2d.py, then npm run gen:range-queries-2d in site/ (the picker's manifest and
the copies it serves).
"""
import sys

import gen_3d
import gen_grid_bit
import gen_grid_seg
import gen_grid_static
import gen_grid_tags
import gen_kd
import gen_online
import gen_tags_online
import lib2d


def main():
    for gen in (gen_grid_static, gen_grid_bit, gen_grid_seg, gen_grid_tags, gen_tags_online, gen_kd, gen_online, gen_3d):
        gen.main()
    print(f"{len(lib2d.WRITTEN)} folders in all")
    extra = lib2d.unwritten()
    if extra:
        print(f"{len(extra)} folders on disk that no generator writes (delete them by hand if they are leftovers):")
        print("\n".join("    " + f for f in extra))
    if lib2d.CHECK and lib2d.STALE:
        print(f"{len(lib2d.STALE)} files differ from what the generators make now, e.g.:")
        print("\n".join("    FAIL  " + f for f in lib2d.STALE[:20]))
    sys.exit(1 if lib2d.CHECK and (lib2d.STALE or extra) else 0)


if __name__ == "__main__":
    main()
