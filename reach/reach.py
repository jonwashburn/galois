#!/usr/bin/env python3
"""Ask what real-root counts a base can write, before any field is built.

  python3 reach.py --deg 12 --r1 12
  python3 reach.py --deg 12 --r1 12 --label 10301 --r 24

A refusal is a proof of no, from group theory. An allow means the group
permits it; the arithmetic still has to work out. Uncensused and primitive
labels fail open: the tool reports no opinion rather than a refusal.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import archscreen  # noqa: E402
import walkscreen  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--deg", type=int, required=True, help="degree of the base")
    ap.add_argument("--r1", type=int, required=True, help="real places of the base")
    ap.add_argument("--label", type=int, help="24T number, 1 to 25000")
    ap.add_argument("--r", type=int, help="real-root count aimed at upstairs")
    ap.add_argument("--type", type=int, dest="base_type", help="optional base type")
    args = ap.parse_args()

    if not walkscreen.load(os.path.join(HERE, "walktable.json.gz")):
        print("no walk table next to this file", file=sys.stderr)
        return 2

    arch = archscreen.reachable_counts(args.deg, args.r1)
    print("archimedean envelope: %s" % (arch or "none"))

    if args.label is None:
        got = walkscreen.signatures_for_base(args.deg, args.base_type or 0, args.r1)
        if args.base_type is None:
            # union over types: walk the by-base table via reachable on a dummy
            # is wrong; print the published compact table instead
            compact = os.path.join(HERE, "reach_by_base.json")
            rows = json.loads(open(compact).read())["by_base"]
            row = next((x for x in rows if x["deg"] == args.deg and x["r1"] == args.r1), None)
            if row is None:
                print("walk: no censused label delivers anything from this base")
            else:
                print("walk, union over labels: %s" % row["reachable_r"])
                print("labels per r: %s" % row["labels_per_r"])
        else:
            print("walk for that base type: %s" % (got if got is not None else "no opinion"))
        return 0

    reached = walkscreen.reachable(args.label, args.deg, args.r1, args.base_type)
    if reached is None:
        print("walk: no opinion on 24T%d (uncensused or primitive)" % args.label)
        return 0
    print("walk for 24T%d: %s" % (args.label, reached if reached else "nothing"))
    if args.r is not None:
        ok = walkscreen.screen(args.label, args.deg, args.r1, args.r, args.base_type)
        print("r=%d allowed: %s" % (args.r, "yes" if ok else "no"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
